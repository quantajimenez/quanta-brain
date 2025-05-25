import os
import redis
import uuid
import json
import logging
import boto3

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- S3 Config ---
S3_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
REDIS_URL = os.environ.get("REDIS_URL")

# Initialize Redis
def get_redis_connection():
    if not REDIS_URL:
        raise Exception("REDIS_URL not found in environment variables.")
    return redis.from_url(REDIS_URL)

# Initialize S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def list_all_polygon_keys(bucket):
    """List all ticker/date keys under polygon/ in S3 bucket"""
    paginator = s3.get_paginator('list_objects_v2')
    tickers = set()
    jobs = []
    for page in paginator.paginate(Bucket=bucket, Prefix="polygon/"):
        for obj in page.get('Contents', []):
            key = obj['Key']
            # Expected: polygon/TICKER/DATE.json
            parts = key.split('/')
            if len(parts) == 3 and parts[2].endswith('.json'):
                ticker = parts[1]
                date = parts[2].replace('.json','')
                jobs.append((ticker, date))
                tickers.add(ticker)
    return jobs

def main():
    r = get_redis_connection()
    jobs = list_all_polygon_keys(S3_BUCKET)
    logging.info(f"Found {len(jobs)} (ticker, date) combinations in S3.")

    pushed = 0
    for ticker, date in jobs:
        job = {
            "id": str(uuid.uuid4()),
            "ticker": ticker,
            "date": date,
            "task": "analyze_data"
        }
        r.lpush("quanta_jobs", json.dumps(job))
        pushed += 1
        if pushed % 100 == 0:
            logging.info(f"Pushed {pushed} jobs so far...")

    logging.info(f"FINISHED: Pushed total {pushed} jobs to Redis.")

if __name__ == "__main__":
    main()
