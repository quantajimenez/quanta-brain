import os
import json
import boto3
from datetime import datetime

def upload_signal_to_s3(data: dict, prefix: str = "youtube") -> str:
    bucket = os.getenv("S3_BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not all([bucket, region, access_key, secret_key]):
        raise ValueError("Missing one or more required S3 environment variables.")

    filename = f"{prefix}_patterns_{datetime.utcnow().date()}.json"

    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    s3.put_object(
        Bucket=bucket,
        Key=f"{prefix}/{filename}",
        Body=json.dumps(data),
        ContentType="application/json"
    )

    print(f"✅ Uploaded: {filename} → s3://{bucket}/{prefix}/")
    return filename

