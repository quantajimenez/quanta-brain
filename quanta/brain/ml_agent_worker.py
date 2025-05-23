import boto3
import os
import json

S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

def upload_insight_to_s3(data):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=AWS_REGION,
    )
    s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=json.dumps(data))
    print(f"[ML AGENT] Uploaded latest insight to S3: {S3_BUCKET}/{S3_KEY}")

# After each job is processed and you have a result dict:
result_dict = {
    "id": job["id"],
    "prediction": prediction,  # your ML output
    "timestamp": time.time(),
    # add any other metadata you want
}

upload_insight_to_s3(result_dict)
