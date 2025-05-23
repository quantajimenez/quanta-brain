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

def ml_predict(job_payload):
    """
    Example ML: Random Forest Classifier on synthetic data
    In production: Load real historical features from S3 or job_payload
    """
    # Generate dummy classification data for model training (replace with your real data pipeline)
    X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
    clf = RandomForestClassifier()
    clf.fit(X, y)
    # For demo: generate random features or map from job_payload if you have real ones
    features = np.random.rand(4)
    prediction = int(clf.predict([features])[0])
    proba = clf.predict_proba([features])[0].tolist()
    return prediction, proba, features.tolist()

def main():
    r = redis.from_url(REDIS_URL)
    logging.info("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                job_data = json.loads(job[1])
                logging.info(f"[ML AGENT] Got job: {job_data}")

                # --- Run ML model (Random Forest demo) ---
                prediction, proba, features = ml_predict(job_data.get("task", ""))

                # --- Compose result ---
                result_dict = {
                    "id": job_data["id"],
                    "prediction": prediction,
                    "probabilities": proba,
                    "features": features,
                    "timestamp": time.time(),
                    "raw_job": job_data,
                }

                # --- Upload to S3 ---
                upload_insight_to_s3(result_dict)
                logging.info(f"[ML AGENT] Processed job: {job_data['id']}")

            except Exception as e:
                logging.error(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
