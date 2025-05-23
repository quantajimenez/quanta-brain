# quanta/utils/s3_reader.py

import os
import boto3
import json
from datetime import datetime

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("WASABI_ENDPOINT"),
        aws_access_key_id=os.getenv("WASABI_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("WASABI_SECRET_KEY"),
    )

def list_youtube_signals(limit=10):
    bucket = os.getenv("INSIGHTS_BUCKET", "quanta-insights")
    prefix = "youtube/"
    s3 = get_s3_client()

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])

    sorted_files = sorted(objects, key=lambda obj: obj["LastModified"], reverse=True)[:limit]
    results = []

    for obj in sorted_files:
        file_obj = s3.get_object(Bucket=bucket, Key=obj["Key"])
        payload = file_obj["Body"].read().decode("utf-8")
        try:
            results.append(json.loads(payload))
        except Exception as e:
            results.append({"error": f"Failed to parse {obj['Key']}: {str(e)}"})

    return results

