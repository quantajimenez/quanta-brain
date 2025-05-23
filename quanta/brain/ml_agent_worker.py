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
from sklearn.datasets import make_classification

from quanta.ingest.polygon_data_loader import load_bars  # THIS LINE LOADS YOUR S3 DATA

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 config ---
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

# --- Redis config ---
REDIS_URL = os.getenv("REDIS_URL")

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

def extract_features(bars):
    # Simple feature extraction example: mean values for OHLCV
    opens = [bar['open'] for bar in bars if 'open' in bar]
    highs = [bar['high'] for bar in bars if 'high' in bar]
    lows = [bar['low'] for bar in bars if 'low' in bar]
    closes = [bar['close'] for bar in bars if 'close' in bar]
    volumes = [bar['volume'] for bar in bars if 'volume' in bar]
    # Require minimum 10 bars for meaningful stats
    if len(opens) < 10:
        return None
    return [
        np.mean(opens),
        np.mean(highs),
        np.mean(lows),
        np.mean(closes),
        np.mean(volumes)
    ]

def ml_predict(features):
    # Model 1: Random Forest (dummy fit for demo)
    X, y = make_classification(n_samples=100, n_features=5, n_classes=2, random_state=42)
    rf = RandomForestClassifier()
    rf.fit(X, y)
    rf_pred = int(rf.predict([features])[0])
    rf_proba = rf.predict_proba([features])[0].tolist()
    # Model 2: Logistic Regression (dummy fit for demo)
    lr = LogisticRegression()
    lr.fit(X, y)
    lr_pred = int(lr.predict([features])[0])
    lr_proba = lr.predict_proba([features])[0].tolist()
    return {
        "random_forest": {"prediction": rf_pred, "proba": rf_proba},
        "logistic_regression": {"prediction": lr_pred, "proba": lr_proba}
    }

def main():
    r = redis.from_url(REDIS_URL)
    logging.info("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                job_data = json.loads(job[1])
                ticker = job_data.get('ticker')
                date = job_data.get('date')
                logging.info(f"[ML AGENT] Got job: {job_data}")
                bars = load_bars(ticker, date)
                logging.info(f"[ML AGENT] Loaded {len(bars)} bars for {ticker} on {date}")
                if not bars or len(bars) < 10:
                    logging.warning("[ML AGENT] Not enough data for features.")
                    continue
                features = extract_features(bars)
                if features is None:
                    logging.warning("[ML AGENT] Not enough data for feature extraction.")
                    continue
                results = ml_predict(features)
                result_dict = {
                    "id": job_data["id"],
                    "ticker": ticker,
                    "date": date,
                    "results": results,
                    "features": features,
                    "timestamp": time.time(),
                    "raw_job": job_data,
                }
                upload_insight_to_s3(result_dict)
                logging.info(f"[ML AGENT] Processed job: {job_data['id']}")
            except Exception as e:
                logging.error(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
