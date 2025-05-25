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

S3_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
REDIS_URL = os.getenv("REDIS_URL")
SCAN_INTERVAL = int(os.getenv("JOBPRODUCER_SCAN_INTERVAL", 600))  # seconds

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def get_redis_connection():
    if REDIS_URL:
        return redis.from_url(REDIS_URL)
    else:
        raise Exception("REDIS_URL not found in environment variables.")

def list_polygon_files():
    """Dynamically find all tickers and dates in S3: polygon/{ticker}/{YYYY-MM-DD}.json"""
    paginator = s3.get_paginator('list_objects_v2')
    jobs = []
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix='polygon/'):
        for obj in page.get('Contents', []):
            key = obj['Key']
            # polygon/SPY/2014-01-03.json
            parts = key.split('/')
            if len(parts) == 3 and parts[2].endswith('.json'):
                ticker = parts[1]
                date = parts[2].replace('.json', '')
                jobs.append((ticker, date))
    return jobs

def main():
    r = get_redis_connection()
    logging.info("[PRODUCER] Job Producer is running and connected to Redis...")
    seen_jobs_key = "quanta_produced_jobs"  # Redis SET to keep track
    while True:
        try:
            all_jobs = list_polygon_files()
            pushed = 0
            for ticker, date in all_jobs:
                job_id = f"{ticker}_{date}"
                # Only enqueue if this job_id not seen before
                if not r.sismember(seen_jobs_key, job_id):
                    job = {
                        "id": str(uuid.uuid4()),
                        "ticker": ticker,
                        "date": date,
                        "task": "analyze_data"
                    }
                    r.lpush("quanta_jobs", json.dumps(job))
                    r.sadd(seen_jobs_key, job_id)
                    pushed += 1
                    logging.info(f"[PRODUCER] Enqueued job: {job}")
            logging.info(f"[PRODUCER] Scan complete. {pushed} new jobs pushed. Sleeping for {SCAN_INTERVAL} seconds.")
        except Exception as e:
            logging.error(f"[PRODUCER][ERROR] {e}")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
