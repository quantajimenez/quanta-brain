import os
import boto3
import json
import time
import logging
import requests

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 Config ---
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
INSIGHTS_PREFIX = "insights/"
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
BRAIN_API_URL = os.getenv("BRAIN_API_URL", "https://quanta-realtime.onrender.com/ingest/insight")  # Update to your real endpoint

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def list_all_insight_keys():
    keys = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=INSIGHTS_PREFIX):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.json'):
                keys.append(obj['Key'])
    return keys

def post_to_brain(insight):
    try:
        resp = requests.post(BRAIN_API_URL, json=insight)
        if resp.status_code == 200:
            logging.info(f"[BRAIN LOADER] Posted insight {insight.get('id')} to brain.")
        else:
            logging.warning(f"[BRAIN LOADER] Failed to POST insight {insight.get('id')} | Status {resp.status_code} | {resp.text}")
    except Exception as e:
        logging.error(f"[BRAIN LOADER] Error posting to brain: {e}")

def load_and_post_all_insights():
    keys = list_all_insight_keys()
    logging.info(f"[BRAIN LOADER] Found {len(keys)} insight files in S3.")
    for key in keys:
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
            data = json.loads(obj['Body'].read().decode())
            post_to_brain(data)
        except Exception as e:
            logging.error(f"[BRAIN LOADER][ERROR] Failed to load/post {key}: {e}")

if __name__ == "__main__":
    logging.info("[BRAIN LOADER] Starting loader loop.")
    while True:
        load_and_post_all_insights()
        time.sleep(300)  # Repeat every 5 min
