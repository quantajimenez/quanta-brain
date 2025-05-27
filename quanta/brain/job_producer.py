import os 
import redis
import time
import uuid
import logging
import json
import boto3

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

REDIS_URL = os.environ.get("REDIS_URL")

def send_heartbeat(worker_name):
    try:
        r = redis.from_url(REDIS_URL)
        r.set(f"health_{worker_name}", time.time())
    except Exception as e:
        print(f"Heartbeat error for {worker_name}: {e}")

S3_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")
S3_PREFIX = os.getenv("S3_POLYGON_PREFIX", "polygon/")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
REDIS_JOBS_KEY = os.getenv("REDIS_JOBS_KEY", "quanta_jobs")
REDIS_SET_KEY = os.getenv("REDIS_SET_KEY", "quanta_jobs_submitted")

if not REDIS_URL:
    raise Exception("REDIS_URL not found in environment variables.")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)
r = redis.from_url(REDIS_URL)

def get_all_s3_keys(prefix=None):
    if prefix is None:
        prefix = S3_PREFIX
    keys = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get('Contents', []):
            keys.append(obj['Key'])
    return keys

def already_queued(job_id):
    return r.sismember(REDIS_SET_KEY, job_id)

def mark_queued(job_id):
    r.sadd(REDIS_SET_KEY, job_id)

def main():
    logging.info("Job Producer is running and connected to Redis...")
    while True:
        send_heartbeat("job_producer")
        keys = get_all_s3_keys()
        logging.info(f"Found {len(keys)} files in S3 under {S3_PREFIX}")
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
                    logging.debug(f"[PRODUCER] Skipped already-queued job: {job_id}")
                    continue  # skip jobs already pushed
                job = {
                    "id": str(uuid.uuid4()),
                    "ticker": ticker,
                    "date": date,
                    "task": "analyze_data"
                }
                r.lpush(REDIS_JOBS_KEY, json.dumps(job))
                mark_queued(job_id)
                logging.info(f"[PRODUCER] Enqueued job for {ticker} {date} | id={job['id']}")
            except Exception as e:
                logging.error(f"[PRODUCER] Error enqueuing job for {key}: {e}")
        time.sleep(60)  # Scan S3 every 1 minute for new files

if __name__ == "__main__":
    main()
