import os
import time
import uuid
import redis
import json
import boto3
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# Import your loader for historical market data
from quanta.ingest.polygon_data_loader import load_bars

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 config ---
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

# --- Redis config ---
REDIS_URL = os.getenv("REDIS_URL")

def upload_insight_to_s3(data, s3_key):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=AWS_REGION,
        )
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=json.dumps(data))
        logging.info(f"[ML AGENT] Uploaded insight to S3: {S3_BUCKET}/{s3_key}")
    except Exception as e:
        logging.error(f"[ML AGENT][ERROR] Failed to upload insight to S3: {e}")

def load_features_from_s3(ticker, date):
    """Loads OHLCV bar data for the ticker/date and extracts features for the ML model."""
    bars = load_bars(ticker, date)
    if not bars or len(bars) < 4:
        return None  # Not enough data
    # For now, take first 4 closing prices as features; extend with more sophisticated features as needed
    features = [bar.get('c', 0) for bar in bars[:4]]
    return features

def ml_predict(job_payload, model_type="random_forest"):
    """Predict using the selected ML model."""
    ticker = job_payload.get("ticker", "SPY")
    date = job_payload.get("date", "2014-01-01")
    features = load_features_from_s3(ticker, date)
    if not features or len(features) < 4:
        return 0, [0.5, 0.5], features or []

    # --- You would train on historical features and labels in production ---
    # Here we use dummy labels as placeholder
    X_train = [features, [f + np.random.uniform(-1, 1) for f in features]]  # just demo variation
    y_train = [0, 1]

    if model_type == "random_forest":
        clf = RandomForestClassifier()
    elif model_type == "logistic_regression":
        clf = LogisticRegression()
    else:
        raise ValueError("Unknown model type")

    clf.fit(X_train, y_train)
    prediction = int(clf.predict([features])[0])
    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba([features])[0].tolist()
    else:
        proba = [0.5, 0.5]
    return prediction, proba, features

def main():
    r = redis.from_url(REDIS_URL)
    logging.info("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                job_data = json.loads(job[1])
                logging.info(f"[ML AGENT] Got job: {job_data}")

                model_type = job_data.get("model", "random_forest")
                task_payload = job_data.get("task", {})

                # --- Run ML model (Random Forest or Logistic Regression) ---
                prediction, proba, features = ml_predict(task_payload, model_type=model_type)

                # --- Compose result ---
                result_dict = {
                    "id": job_data.get("id", str(uuid.uuid4())),
                    "model": model_type,
                    "prediction": prediction,
                    "probabilities": proba,
                    "features": features,
                    "timestamp": time.time(),
                    "raw_job": job_data,
                }

                # --- Write output as unique key per insight ---
                s3_key = f"{task_payload.get('ticker','unknown')}_{task_payload.get('date','unknown')}_{model_type}_insight.json"
                upload_insight_to_s3(result_dict, s3_key)
                logging.info(f"[ML AGENT] Processed job: {result_dict['id']}")

            except Exception as e:
                logging.error(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
