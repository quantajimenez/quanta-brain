import os
import time
import uuid
import redis
import json
import boto3
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 config ---
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
HIST_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")

# --- Redis config ---
REDIS_URL = os.getenv("REDIS_URL")

# --- Import loader for historical bars ---
from quanta.ingest.polygon_data_loader import load_bars

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
    # Example ML: Random Forest Classifier on synthetic data
    X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
    clf = RandomForestClassifier()
    clf.fit(X, y)
    features = np.array(features).reshape(1, -1)
    prediction = int(clf.predict(features)[0])
    proba = clf.predict_proba(features)[0].tolist()
    return prediction, proba, features.tolist()[0]

def main():
    r = redis.from_url(REDIS_URL)
    logging.info("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                # Print out the raw job
                logging.info(f"[ML AGENT][DEBUG] Raw job from Redis: {job}")
                job_data = json.loads(job[1])
                logging.info(f"[ML AGENT][DEBUG] Decoded job_data: {job_data}")

                # --- LOAD HISTORICAL DATA FROM S3 ---
                ticker = job_data.get("ticker")
                date = job_data.get("date")

                # Add extra debug info
                if ticker is None or date is None:
                    logging.error(f"[ML AGENT][ERROR] Missing ticker or date in job_data: {job_data}")
                    continue

                # Build correct S3 key for historical data
                s3_key = f"polygon/{ticker}/{date}.json"
                logging.info(f"[ML AGENT] Fetching bars from S3: {HIST_BUCKET}/{s3_key}")

                # Override loader call to pass correct path
                bars = load_bars(ticker, date)  # Loader should expect (ticker, date) and internally build s3_key
                logging.info(f"[ML AGENT] Loaded bars: {bars[:3]} (total: {len(bars)})")

                # --- Simple feature extraction: require at least 4 bars ---
                if not bars or len(bars) < 4:
                    logging.warning("[ML AGENT] Not enough data for features.")
                    continue

                # --- Example: use open/high/low/close from first bar as features ---
                first_bar = bars[0]
                features = [
                    first_bar.get("open", 0),
                    first_bar.get("high", 0),
                    first_bar.get("low", 0),
                    first_bar.get("close", 0)
                ]

                prediction, proba, used_features = ml_predict(features)

                result_dict = {
                    "id": job_data.get("id"),
                    "prediction": prediction,
                    "probabilities": proba,
                    "features": used_features,
                    "timestamp": time.time(),
                    "raw_job": job_data,
                }

                upload_insight_to_s3(result_dict)
                logging.info(f"[ML AGENT] Processed job: {job_data.get('id')}")

            except Exception as e:
                logging.error(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
