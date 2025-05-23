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

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 config ---
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
HIST_S3_BUCKET = os.getenv("QUANTA_HIST_S3_BUCKET", "quanta-historical-marketdata")
REDIS_URL = os.getenv("REDIS_URL")

def load_bars_from_s3(ticker, date):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=AWS_REGION,
    )
    key = f"polygon/{ticker}/{date}.json"
    try:
        obj = s3.get_object(Bucket=HIST_S3_BUCKET, Key=key)
        bars = json.loads(obj['Body'].read().decode())
        return bars
    except Exception as e:
        logging.error(f"[ML AGENT][ERROR] Could not load bars: {e}")
        return []

def extract_features(bars):
    # Example feature extraction from bar data (replace with your own logic)
    closes = [bar.get('c', 0) for bar in bars if 'c' in bar]
    if len(closes) < 10:
        return None  # Not enough data
    features = [
        np.mean(closes),
        np.std(closes),
        closes[-1] - closes[0],  # Price change
        np.max(closes) - np.min(closes)  # Price range
    ]
    return features

def upload_insight_to_s3(data):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=AWS_REGION,
        )
        s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=json.dumps(data))
        logging.info(f"[ML AGENT] Uploaded latest insight to S3: {S3_BUCKET}/{S3_KEY}")
    except Exception as e:
        logging.error(f"[ML AGENT][ERROR] Failed to upload insight to S3: {e}")

def ml_predict(features):
    """
    Run both Random Forest and Logistic Regression on the features.
    In production, load real models trained on your data.
    """
    # Dummy data to fit models (replace with your real training set)
    X_train = np.random.rand(100, 4)
    y_train = np.random.randint(2, size=100)
    
    # Train models (in real world, load from disk/S3 or retrain periodically)
    rf = RandomForestClassifier().fit(X_train, y_train)
    lr = LogisticRegression().fit(X_train, y_train)
    
    rf_pred = int(rf.predict([features])[0])
    rf_proba = rf.predict_proba([features])[0].tolist()
    lr_pred = int(lr.predict([features])[0])
    lr_proba = lr.predict_proba([features])[0].tolist()
    
    return {
        "random_forest": {"prediction": rf_pred, "probabilities": rf_proba},
        "logistic_regression": {"prediction": lr_pred, "probabilities": lr_proba}
    }

def main():
    r = redis.from_url(REDIS_URL)
    logging.info("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                job_data = json.loads(job[1])
                logging.info(f"[ML AGENT] Got job: {job_data}")

                ticker = job_data.get("ticker", "SPY")
                date = job_data.get("date", "2014-01-01")
                bars = load_bars_from_s3(ticker, date)
                features = extract_features(bars)
                if not features:
                    logging.warning("[ML AGENT] Not enough data for features.")
                    continue

                predictions = ml_predict(features)
                result_dict = {
                    "id": job_data.get("id", str(uuid.uuid4())),
                    "ticker": ticker,
                    "date": date,
                    "predictions": predictions,
                    "features": features,
                    "timestamp": time.time(),
                    "raw_job": job_data,
                }
                upload_insight_to_s3(result_dict)
                logging.info(f"[ML AGENT] Processed job: {result_dict['id']}")

            except Exception as e:
                logging.error(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
