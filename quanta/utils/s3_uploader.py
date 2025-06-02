import os
import json
import boto3
from datetime import datetime


def upload_signal_to_s3(data: dict, prefix: str = "insights", label: str = "YOUTUBE") -> str:
    """
    Uploads a JSON insight file to the configured S3 bucket.
    
    Args:
        data (dict): The data to upload.
        prefix (str): S3 folder prefix. Default is 'insights'.
        label (str): Optional label for the file name (e.g., 'YOUTUBE', 'NEWS').
    
    Returns:
        str: The final S3 object key used.
    """
    bucket = os.getenv("S3_BUCKET_NAME", "quanta-insights")
    region = os.getenv("AWS_REGION", "us-east-1")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not all([bucket, region, access_key, secret_key]):
        raise ValueError("Missing one or more required S3 environment variables.")

    # Construct file name: e.g., insights/YOUTUBE_20250527_153210.json
    filename = f"{label}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    object_key = f"{prefix}/{filename}"

    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    s3.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=json.dumps(data),
        ContentType="application/json"
    )

    print(f"✅ Uploaded to S3: s3://{bucket}/{object_key}")
    return object_key
