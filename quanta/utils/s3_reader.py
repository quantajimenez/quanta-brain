import os
import boto3
from botocore.exceptions import ClientError

def list_youtube_signals():
    """
    List objects in the configured S3 bucket with the prefix 'youtube/'.
    Assumes AWS credentials are set in environment variables.
    """
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "us-east-1")
    bucket = os.getenv("S3_BUCKET_NAME")
    prefix = os.getenv("S3_PREFIX", "youtube")

    if not all([access_key, secret_key, bucket]):
        raise Exception("Missing one or more required S3 environment variables.")

    session = boto3.session.Session()
    s3 = session.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        keys = [obj["Key"] for obj in response.get("Contents", [])]
        return keys
    except ClientError as e:
        raise Exception(f"S3 list_objects_v2 failed: {e}")
