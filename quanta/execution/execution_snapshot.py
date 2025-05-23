# quanta/execution/execution_snapshot.py

import logging
import json
import os
import boto3
from datetime import datetime

S3_BUCKET = os.getenv("QUANTA_LOG_S3_BUCKET", "quanta-execution-logs")
S3_PREFIX = os.getenv("QUANTA_LOG_S3_PREFIX", "execution_snapshots")

logger = logging.getLogger("quanta.execution.execution_snapshot")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_execution_snapshot(stage, status, details=""):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "status": status,
        "details": details
    }
    logger.info(f"[EXECUTION SNAPSHOT] {json.dumps(log_entry)}")
    # Save to S3
    s3 = boto3.client("s3")
    key = f"{S3_PREFIX}/{stage}/{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(log_entry))
