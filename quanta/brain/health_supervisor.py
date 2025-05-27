# health_supervisor.py

import os
import redis
import time
import boto3
import json
from datetime import datetime

# --- Config ---
REDIS_URL = os.getenv("REDIS_URL")
WORKERS = [
    "ml_agent_worker",
    "brain_logic_worker",
    "insight_loader",
    "job_producer",
    "s3_loader_ml_agent"
]
S3_BUCKET = os.getenv("S3_AUDIT_BUCKET", "quanta-mesh-audit-logs")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
ALERT_THRESHOLD_SEC = 180  # 3 minutes

# --- AWS S3 Client ---
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def log_alert_to_s3(worker, last_heartbeat, now_ts):
    alert = {
        "worker": worker,
        "last_heartbeat": last_heartbeat,
        "detected_at": now_ts,
        "alert_type": "heartbeat_missed",
        "message": f"Worker '{worker}' missed heartbeat. Last was at {last_heartbeat}, now {now_ts}."
    }
    filename = f"alerts/{worker}_{now_ts}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=json.dumps(alert)
    )
    print(f"[SUPERVISOR] Alert written to {S3_BUCKET}/{filename}")

def main():
    r = redis.from_url(REDIS_URL)
    while True:
        now_ts = int(time.time())
        for worker in WORKERS:
            key = f"health_{worker}"
            last = r.get(key)
            if last is None:
                print(f"[SUPERVISOR] No heartbeat for {worker}.")
                log_alert_to_s3(worker, None, now_ts)
                continue
            last = float(last)
            diff = now_ts - last
            if diff > ALERT_THRESHOLD_SEC:
                print(f"[SUPERVISOR] {worker} missed heartbeat by {diff} sec.")
                log_alert_to_s3(worker, last, now_ts)
            else:
                print(f"[SUPERVISOR] {worker} is healthy. Last: {last}, Now: {now_ts}, Diff: {diff}")
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
