import io
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"
STATIC_DIR = BASE_DIR.parent / "static"

xgb_model = None
scaler = None
label_encoder = None
feature_names = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global xgb_model, scaler, label_encoder, feature_names
    xgb_model = joblib.load(MODEL_DIR / "xgb_model.pkl")
    scaler = joblib.load(MODEL_DIR / "scaler.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")
    yield


app = FastAPI(title="Cyber Attack Predictor", lifespan=lifespan)

# Read allowed origins from environment variables, fallback to localhost for development
origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000")
allowed_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    # Restrict methods to only what this API actually needs
    allow_methods=["GET", "POST", "OPTIONS"],
    # Restrict headers to standard API headers and prevent arbitrary headers
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/features")
def get_features():
    return {"features": feature_names}


@app.post("/predict-csv")
# Remove 'async' to allow FastAPI to execute this CPU-bound handler in a separate threadpool
def predict_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    try:
        # Read the file stream directly to prevent memory overload (OOM issues)
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    missing = [f for f in feature_names if f not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing required features", "missing_features": missing},
        )

    try:
        demo_mode = "Actual_Label" in df.columns
        X = df[feature_names].values
        X_scaled = scaler.transform(X)
        preds = xgb_model.predict(X_scaled)
        probas = xgb_model.predict_proba(X_scaled)
        labels = label_encoder.inverse_transform(preds)

        summary = {}
        results = []

        if demo_mode:
            actuals = df["Actual_Label"].astype(str).tolist()
            correct_count = 0
            for i, (label, proba, actual) in enumerate(zip(labels, probas, actuals)):
                # Convert Numpy element to standard Python string to avoid JSON serialization errors
                safe_label = str(label)
                confidence = round(float(np.max(proba)) * 100, 2)
                is_correct = safe_label == actual
                if is_correct:
                    correct_count += 1
                summary[safe_label] = summary.get(safe_label, 0) + 1
                results.append({
                    "row": i + 1,
                    "actual": actual,
                    "prediction": safe_label,
                    "confidence": confidence,
                    "is_correct": is_correct,
                })
            accuracy = round(correct_count / len(results) * 100, 2)
            return {
                "mode": "demo",
                "total_rows": len(results),
                "summary": summary,
                "accuracy": accuracy,
                "results": results,
            }
        else:
            for i, (label, proba) in enumerate(zip(labels, probas)):
                # Convert Numpy element to standard Python string to avoid JSON serialization errors
                safe_label = str(label)
                confidence = round(float(np.max(proba)) * 100, 2)
                summary[safe_label] = summary.get(safe_label, 0) + 1
                results.append({"row": i + 1, "prediction": safe_label, "confidence": confidence})
            return {"mode": "unseen", "total_rows": len(results), "summary": summary, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
