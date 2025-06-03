# quanta/brain/youtube_brain_logic.py

import json
import os
import boto3
from datetime import datetime

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_REGION", "us-east-1")

s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def list_youtube_insights():
    print("🔎 Looking for YouTube insights in quanta-insights...")
    try:
        response = s3.list_objects_v2(
            Bucket="quanta-insights",
            Prefix="insights/YOUTUBE_"
        )
        files = [obj["Key"] for obj in response.get("Contents", [])]
        print(f"📦 Found {len(files)} files")
        return files
    except Exception as e:
        print(f"❌ Error listing insights: {e}")
        return []

def process_and_write_signal(key):
    try:
        raw = s3.get_object(Bucket="quanta-insights", Key=key)
        content = json.loads(raw["Body"].read())

        action = "INSIGHT"
        if "breakout" in json.dumps(content).lower():
            action = "BUY"

        signal = {
            "source": "youtube",
            "action": action,
            "raw_key": key,
            "timestamp": datetime.utcnow().isoformat()
        }

        signal_key = key.replace("insights", "signals/youtube_signals")
        s3.put_object(
            Bucket="quanta-signals",
            Key=signal_key,
            Body=json.dumps(signal),
            ContentType="application/json"
        )

        print(f"✅ Wrote signal: {signal_key}")

    except Exception as e:
        print(f"❌ Failed to process {key}: {e}")

def run():
    print("🧠 Starting YouTube brain logic...")
    files = list_youtube_insights()
    if not files:
        print("⚠️ No YouTube insights found.")
        return
    for key in files:
        process_and_write_signal(key)

if __name__ == "__main__":
    run()

