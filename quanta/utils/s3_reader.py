# quanta/utils/s3_reader.py

import boto3
import os

def list_youtube_signals():
    """
    List all YouTube signal files in the S3 bucket under the given prefix.
    Defaults to 'quanta-insights' bucket and 'youtube' prefix.
    """
    bucket = os.getenv("S3_BUCKET_NAME", "quanta-insights")
    prefix = os.getenv("S3_PREFIX", "youtube")

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not all([aws_access_key, aws_secret_key]):
        print("❌ Missing AWS credentials. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
        return []

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    try:
        print(f"🧠 Loading YouTube signals from S3...\n📦 Bucket: {bucket} | Prefix: {prefix}/")
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' not in response:
            print("⚠️ No files found in the specified prefix.")
            return []

        keys = [obj['Key'] for obj in response['Contents']]
        print(f"✅ Found {len(keys)} objects.")
        return keys

    except Exception as e:
        print(f"❌ S3 list_objects_v2 failed: {e}")
        return []

