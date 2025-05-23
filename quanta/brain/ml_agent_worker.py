import os
import time
import uuid
import redis
import json
import boto3

# S3 config
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

# Redis config (only using REDIS_URL for simplicity)
REDIS_URL = os.getenv("REDIS_URL")

def upload_insight_to_s3(data):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=AWS_REGION,
        )
        s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=json.dumps(data))
        print(f"[ML AGENT] Uploaded latest insight to S3: {S3_BUCKET}/{S3_KEY}")
    except Exception as e:
        print(f"[ML AGENT][ERROR] Failed to upload insight to S3: {e}")

def ml_predict(job_payload):
    # Dummy ML: Just returns a random float. Replace with your model.
    import random
    return random.uniform(0, 1)

def main():
    r = redis.from_url(REDIS_URL)
    print("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                job_data = json.loads(job[1])
                print(f"[ML AGENT] Got job: {job_data}")

                # 1. Run your ML model (replace with actual prediction code)
                prediction = ml_predict(job_data.get("task", ""))

                # 2. Compose result
                result_dict = {
                    "id": job_data["id"],
                    "prediction": prediction,
                    "timestamp": time.time(),
                    "raw_job": job_data,
                }

                # 3. Upload to S3
                upload_insight_to_s3(result_dict)

                print(f"[ML AGENT] Processed job: {job_data['id']}")
            except Exception as e:
                print(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
