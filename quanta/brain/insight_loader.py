# quanta/brain/insight_loader.py

import os
import boto3
import json
import time
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 Config ---
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def load_latest_insight():
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        data = json.loads(obj['Body'].read().decode())
        logging.info(f"[BRAIN LOADER] Latest insight loaded from S3:\n{json.dumps(data, indent=2)}")
        # TODO: Insert here to push to database, API, dashboard, etc.
        return data
    except Exception as e:
        logging.error(f"[BRAIN LOADER][ERROR] Failed to load latest insight: {e}")

if __name__ == "__main__":
    logging.info("[BRAIN LOADER] Starting loader loop.")
    while True:
        load_latest_insight()
        time.sleep(10)
