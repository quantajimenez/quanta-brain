import os
import json
import boto3
import uuid

def upload_signal_to_s3(data: dict, prefix: str = "youtube") -> str:
    """
    Uploads a single signal JSON to S3 with a unique UUID-based key.

    Args:
        data (dict): The signal data to upload.
        prefix (str): Folder prefix within the bucket, defaults to 'youtube'.

    Returns:
        str: The S3 key of the uploaded object.
    """
    bucket = os.getenv("S3_BUCKET_NAME", "quanta-insights")
    region = os.getenv("AWS_REGION", "us-east-1")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not all([bucket, region, access_key, secret_key]):
        raise ValueError("❌ Missing one or more required S3 environment variables.")

    object_key = f"{prefix}/{uuid.uuid4()}.json"

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

