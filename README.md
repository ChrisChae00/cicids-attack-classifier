# CICIDS-2017 Attack Classifier

A FastAPI web application that classifies network traffic as Benign or a specific attack type (DoS, DDoS, BruteForce, PortScan, WebAttack, Botnet) using a pre-trained XGBoost model trained on the CICIDS dataset.

## Model Research & Comparison

This project includes a comprehensive research phase where different machine learning models were evaluated using the CICIDS-2017 dataset.

- **Notebook:** [`final-project-ai-ml.ipynb`](./notebook/final-project-ai-ml.ipynb)
- **Key Highlights:**
  - Granular label mapping (15 types to 7 major categories).
  - Data preprocessing pipeline (handling missing/infinite values, scaling).
  - Comparative analysis of classifiers (XGBoost, RandomForest, etc.).
  - _Note: The research was conducted in a Kaggle environment using a 2.3M+ row dataset._

## Project Structure

```text
cicids-attack-classifier/
├── app/                        # Backend Application
│   ├── main.py                 # FastAPI routing & logic
│   ├── model/                  # Serialized model artifacts
│   │   ├── xgb_model.pkl
│   │   ├── scaler.pkl
│   │   ├── label_encoder.pkl
│   │   └── feature_names.pkl
│   └── testset/                # Sample CSVs for testing
├── notebook/                   # Research & Experiments
│   └── final-project-ai-ml.ipynb
├── static/                     # Frontend UI
│   └── index.html
├── requirements.txt            # Python dependencies
└── README.md
```

## Setup & Local Run

### 1. Requirements

Ensure you have Python 3.8+ installed. Install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Model Preparation

Place the following four model files in `app/model/`:

- `xgb_model.pkl`, `scaler.pkl`, `label_encoder.pkl`, `feature_names.pkl`

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

Open your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

> [!NOTE]
> For macOS users, accessing via `http://127.0.0.1:8000` is recommended over `localhost` to avoid IPv6 resolution issues.

## Sample Data for Testing

Sample CSV files are provided in `app/testset/` to verify the classifier:

- `unseen_test_data.csv`: Real-world scenario data.
- `demo_balanced.csv`: Evenly distributed attack types.
- `demo_attack_heavy.csv` / `demo_realistic.csv`: Stress-test scenarios.

## API Documentation

### `GET /features`

Returns the list of 77 required network feature names.

### `POST /predict-csv`

Upload a CSV file to get batch predictions.

**Example Request:**

```bash
curl -X POST http://localhost:8000/predict-csv -F "file=@network_traffic.csv"
```

## Deployment (Render)

1. Push this repository to GitHub.
2. Connect to [Render](https://render.com) as a **Web Service**.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
