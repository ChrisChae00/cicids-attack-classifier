# cicids-attack-classifier

A FastAPI web application that classifies network traffic as Benign or a specific attack type (DoS, DDoS, BruteForce, PortScan, WebAttack, Botnet) using a pre-trained XGBoost model trained on the CICIDS dataset.

## Project Structure

```
cicids-attack-classifier/
├── app/
│   ├── main.py
│   ├── model/
│   │   ├── xgb_model.pkl
│   │   ├── scaler.pkl
│   │   ├── label_encoder.pkl
│   │   └── feature_names.pkl
│   └── testset/
│       ├── demo_attack_heavy.csv
│       ├── demo_balanced.csv
│       ├── demo_realistic.csv
│       └── unseen_test_data.csv
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

Open your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

> [!NOTE]
> For macOS users, accessing via `http://127.0.0.1:8000` is recommended over `localhost` to ensure reliable connectivity and avoid potential IPv6 resolution issues.

## Sample Data

Sample CSV files containing test network traffic data are provided for verification:

- `app/testset/unseen_test_data.csv`
- `app/testset/demo_balanced.csv`
- `app/testset/demo_attack_heavy.csv`
- `app/testset/demo_realistic.csv`


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
    { "row": 1, "prediction": "BENIGN", "confidence": 99.87 },
    { "row": 2, "prediction": "DoS Hulk", "confidence": 97.43 },
    { "row": 3, "prediction": "BENIGN", "confidence": 98.12 }
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
