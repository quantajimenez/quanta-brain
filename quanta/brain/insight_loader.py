import os
import boto3
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
INSIGHTS_PREFIX = "insights/"
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

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

def ingest_to_brain(insight):
    # TODO: Replace this with your real ingestion logic.
    # This could be a database insert, API call, or vector DB upload.
    # For now, we'll just log the ID as a placeholder.
    logging.info(f"[BRAIN LOADER] Ingested insight to brain: {insight.get('id')}")
    # Example: vector_db.insert(insight) or db.insert(insight)

def load_all_insights():
    all_data = []
    keys = list_all_insight_keys()
    logging.info(f"[BRAIN LOADER] Found {len(keys)} insight files in S3.")
    for key in keys:
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
            data = json.loads(obj['Body'].read().decode())
            all_data.append(data)
            ingest_to_brain(data)
        except Exception as e:
            logging.error(f"[BRAIN LOADER][ERROR] Failed to load {key}: {e}")
    logging.info(f"[BRAIN LOADER] Loaded insights (sample):\n{json.dumps(all_data[:3], indent=2)}")
    return all_data

if __name__ == "__main__":
    logging.info("[BRAIN LOADER] Starting loader loop.")
    while True:
        load_all_insights()
        time.sleep(60)
