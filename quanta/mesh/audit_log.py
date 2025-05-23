# quanta/mesh/audit_log.py

import threading
import os
import boto3
import json
from datetime import datetime

S3_BUCKET = os.getenv("QUANTA_AUDIT_S3_BUCKET", "quanta-mesh-logs")
S3_PREFIX = os.getenv("QUANTA_AUDIT_S3_PREFIX", "audit")

class MeshAuditLogger:
    def __init__(self):
        self.lock = threading.Lock()
        self.s3 = boto3.client("s3")
    
    def log_event(self, event_type, agent, detail=""):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.upper(),
            "agent": agent,
            "detail": detail,
        }
        key = f"{S3_PREFIX}/{event_type.lower()}/{agent}/{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}.json"
        with self.lock:
            self.s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(entry))
    
    def query(self, last_n=100):
        # This will list recent logs. For demo, fetch the last N from S3 by prefix.
        # In prod, use Athena/Elasticsearch for querying.
        response = self.s3.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=S3_PREFIX,
            MaxKeys=last_n
        )
        logs = []
        for obj in sorted(response.get("Contents", []), key=lambda x: x["LastModified"], reverse=True)[:last_n]:
            log_obj = self.s3.get_object(Bucket=S3_BUCKET, Key=obj["Key"])
            logs.append(json.loads(log_obj["Body"].read()))
        return logs
