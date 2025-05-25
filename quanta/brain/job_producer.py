import os
import redis
import time
import uuid
import logging
import json
import boto3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# S3 Setup
S3_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def get_redis_connection():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url)
    else:
        raise Exception("REDIS_URL not found in environment variables.")

def list_all_hist_files():
    """Lists all available ticker/date .json files under polygon/<TICKER>/"""
    paginator = s3.get_paginator('list_objects_v2')
    result = []
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix="polygon/"):
        for obj in page.get('Contents', []):
            key = obj['Key']
            # Expecting keys like polygon/SPY/2014-01-03.json
            if key.endswith('.json'):
                parts = key.split('/')
                if len(parts) == 3:
                    ticker = parts[1]
                    date = parts[2].replace('.json','')
                    result.append((ticker, date, key))
    return result

def main():
    r = get_redis_connection()
    jobs = list_all_hist_files()
    logging.info(f"[PRODUCER] Found {len(jobs)} jobs to enqueue.")
    for ticker, date, key in jobs:
        job = {
            "id": str(uuid.uuid4()),
            "ticker": ticker,
            "date": date,
            "task": "analyze_data"
        }
        try:
            r.lpush("quanta_jobs", json.dumps(job))
            logging.info(f"[PRODUCER] Enqueued job: {job}")
        except Exception as e:
            logging.error(f"[PRODUCER] Failed to enqueue job for {ticker} {date}: {e}")
        # Optionally throttle to avoid overloading downstream systems:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
