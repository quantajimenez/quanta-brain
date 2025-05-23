# quanta/utils/s3_reader.py

import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()  # Ensure .env variables are loaded

def get_s3_client():
    """
    Create an S3 client using credentials from environment variables.
    Supports Wasabi or AWS.
    """
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("WASABI_ENDPOINT"),
        aws_access_key_id=os.getenv("WASABI_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("WASABI_SECRET_KEY"),
    )

def list_youtube_signals(limit=10):
    """
    List recent YouTube signals from the S3 insights bucket (default: Wasabi).
    Returns a list of parsed JSON entries, sorted by last modified.
    """
    print("✅ Loading YouTube signals from S3...")
    
    bucket = os.getenv("INSIGHTS_BUCKET", "quanta-insights")
    prefix = "youtube/"
    print(f"📦 Bucket: {bucket} | Prefix: {prefix}")

    s3 = get_s3_client()

    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        print("🧾 S3 list_objects_v2 succeeded")
    except ClientError as e:
        print(f"❌ S3 list_objects_v2 failed: {e}")
        raise RuntimeError("Failed to list YouTube signals from S3") from e

    objects = response.get("Contents", [])
    if not objects:
        print("⚠️ No YouTube signals found in S3 bucket.")
        return []

    # Sort files by modification date (latest first)
    sorted_files = sorted(objects, key=lambda obj: obj["LastModified"], reverse=True)[:limit]

    results = []
    for obj in sorted_files:
        key = obj["Key"]
        try:
            file_obj = s3.get_object(Bucket=bucket, Key=key)
            body = file_obj["Body"].read().decode("utf-8")
            payload = json.loads(body)
            results.append(payload)
            print(f"✅ Parsed: {key}")
        except Exception as e:
            print(f"❌ Failed to parse {key}: {e}")
            results.append({"error": f"Failed to parse {key}", "details": str(e)})

    return results

