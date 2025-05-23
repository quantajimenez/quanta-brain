# quanta/ingest/ingestor_agent.py

import time
import json
import os
import boto3
from datetime import datetime
from quanta.ingest.logging_utils import log_event

S3_BUCKET = os.getenv("QUANTA_EVENT_S3_BUCKET", "quanta-ingest-events")
S3_PREFIX = os.getenv("QUANTA_EVENT_S3_PREFIX", "ingested_events")

def ingest_event(event):
    # Time-stamp, validate, and store in vector DB (stub for now)
    event_dict = event.dict() if hasattr(event, "dict") else dict(event)
    event_dict["timestamp"] = time.time()
    # TODO: Store in FAISS/Chroma vector DB here

    # Save to S3 as a persistent record
    s3 = boto3.client("s3")
    s3_key = f"{S3_PREFIX}/{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=json.dumps(event_dict))

    log_event(event_dict)
