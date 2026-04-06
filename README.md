# cicids-attack-classifier

A FastAPI web application that classifies network traffic as Benign or a specific attack type (DoS, DDoS, BruteForce, PortScan, WebAttack, Botnet) using a pre-trained XGBoost model trained on the CICIDS dataset.

## Project Structure

```
cicids-attack-classifier/
├── app/
│   ├── main.py
│   └── model/
│       ├── xgb_model.pkl
│       ├── scaler.pkl
│       ├── label_encoder.pkl
│       └── feature_names.pkl
├── static/
│   └── index.html
├── requirements.txt
└── README.md
```

## Setup

1. Place the four model files in `app/model/`:
   - `xgb_model.pkl`
   - `scaler.pkl`
   - `label_encoder.pkl`
   - `feature_names.pkl`

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run Locally

```bash
uvicorn app.main:app --reload
```

Open your browser at `http://localhost:8000`.

## API Documentation

### `GET /features`

Returns the list of 77 required feature names.

**Response:**
```json
{
  "features": ["feature_1", "feature_2", "..."]
}
```

### `POST /predict-csv`

Upload a CSV file to get attack predictions for each row.

**Request:**
```bash
curl -X POST http://localhost:8000/predict-csv \
  -F "file=@network_traffic.csv"
```

**Response:**
```json
{
  "total_rows": 3,
  "summary": {
    "BENIGN": 2,
    "DoS Hulk": 1
  },
  "results": [
    { "row": 1, "prediction": "BENIGN",   "confidence": 99.87 },
    { "row": 2, "prediction": "DoS Hulk", "confidence": 97.43 },
    { "row": 3, "prediction": "BENIGN",   "confidence": 98.12 }
  ]
}
```

**Error responses:**
- `400` — Wrong file type, or missing required feature columns
- `500` — Prediction error

## Deploy on Render

1. Push this repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Set the **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Set **Build Command**:
   ```
   pip install -r requirements.txt
   ```
