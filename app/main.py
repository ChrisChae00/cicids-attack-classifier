import io
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
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


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/features")
def get_features():
    return {"features": feature_names}


@app.post("/predict-csv")
async def predict_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    missing = [f for f in feature_names if f not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing required features", "missing_features": missing},
        )

    try:
        X = df[feature_names].values
        X_scaled = scaler.transform(X)
        preds = xgb_model.predict(X_scaled)
        probas = xgb_model.predict_proba(X_scaled)
        labels = label_encoder.inverse_transform(preds)

        summary = {}
        results = []
        for i, (label, proba) in enumerate(zip(labels, probas)):
            confidence = round(float(np.max(proba)) * 100, 2)
            summary[label] = summary.get(label, 0) + 1
            results.append({"row": i + 1, "prediction": label, "confidence": confidence})

        return {"total_rows": len(results), "summary": summary, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
