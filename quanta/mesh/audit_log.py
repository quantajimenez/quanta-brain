# quanta/mesh/audit_log.py

import os
import threading
import datetime

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class MeshAuditLogger:
    def __init__(self, s3_key="mesh_audit.log"):
        self.use_s3 = False
        self.s3_key = s3_key
        self.lock = threading.Lock()

        bucket = os.environ.get("QUANTA_AUDIT_S3_BUCKET")
        region = os.environ.get("AWS_DEFAULT_REGION")
        if bucket and region:
            try:
                self.s3 = boto3.client("s3", region_name=region)
                # Check if bucket exists (simple call)
                self.s3.head_bucket(Bucket=bucket)
                self.bucket = bucket
                self.use_s3 = True
            except (NoCredentialsError, ClientError) as e:
                print(f"[WARN] S3 logging disabled: {e}. Falling back to local logging.")
                self.use_s3 = False

        if not self.use_s3:
            # fallback to local logs
            logdir = "/logs" if os.path.isdir("/logs") else os.path.join(os.path.dirname(__file__), "..", "..", "logs")
            os.makedirs(logdir, exist_ok=True)
            self.filename = os.path.join(logdir, "mesh_audit.log")

    def log_event(self, event_type, agent, detail=""):
        entry = f"{datetime.datetime.utcnow().isoformat()} | {event_type.upper()} | {agent} | {detail}\n"
        with self.lock:
            if self.use_s3:
                try:
                    # Download, append, upload (simple approach)
                    try:
                        obj = self.s3.get_object(Bucket=self.bucket, Key=self.s3_key)
                        old_logs = obj["Body"].read().decode("utf-8")
                    except self.s3.exceptions.NoSuchKey:
                        old_logs = ""
                    new_logs = old_logs + entry
                    self.s3.put_object(Bucket=self.bucket, Key=self.s3_key, Body=new_logs.encode("utf-8"))
                except Exception as e:
                    print(f"[ERROR] Failed S3 log write: {e}")
            else:
                with open(self.filename, "a") as f:
                    f.write(entry)

    def query(self, last_n=100):
        with self.lock:
            if self.use_s3:
                try:
                    obj = self.s3.get_object(Bucket=self.bucket, Key=self.s3_key)
                    lines = obj["Body"].read().decode("utf-8").splitlines()
                    return lines[-last_n:]
                except self.s3.exceptions.NoSuchKey:
                    return []
                except Exception as e:
                    print(f"[ERROR] Failed S3 log read: {e}")
                    return []
            else:
                if not os.path.exists(self.filename):
                    return []
                with open(self.filename, "r") as f:
                    return f.readlines()[-last_n:]
