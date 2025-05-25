import os
import redis
import time
import uuid
import logging
import json
import boto3

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# --- S3 and Redis config ---
S3_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
REDIS_URL = os.environ.get("REDIS_URL")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)
r = redis.from_url(REDIS_URL)

def get_all_s3_keys(prefix="polygon/"):
    """Return all S3 keys under prefix (for all tickers/dates)."""
    keys = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get('Contents', []):
            keys.append(obj['Key'])
    return keys

def already_queued(job_id):
    """Check if job_id is already in Redis SET (idempotency)."""
    return r.sismember("quanta_jobs_submitted", job_id)

def mark_queued(job_id):
    r.sadd("quanta_jobs_submitted", job_id)

def main():
    logging.info("Job Producer is running and connected to Redis...")
    while True:
        keys = get_all_s3_keys()
        logging.info(f"Found {len(keys)} files in S3 under polygon/")
        for key in keys:
            try:
                parts = key.split("/")
                if len(parts) != 3:  # polygon/TICKER/DATE.json
                    continue
                _, ticker, file = parts
                if not file.endswith('.json'):
                    continue
                date = file.replace('.json','')
                job_id = f"{ticker}_{date}"
                if already_queued(job_id):
                    continue  # skip jobs already pushed
                job = {
                    "id": str(uuid.uuid4()),
                    "ticker": ticker,
                    "date": date,
                    "task": "analyze_data"
                }
                r.lpush("quanta_jobs", json.dumps(job))
                mark_queued(job_id)
                logging.info(f"[PRODUCER] Enqueued job for {ticker} {date} | id={job['id']}")
            except Exception as e:
                logging.error(f"[PRODUCER] Error enqueuing job for {key}: {e}")
        time.sleep(60)  # Scan S3 every 1 minute for new files

if __name__ == "__main__":
    main()
