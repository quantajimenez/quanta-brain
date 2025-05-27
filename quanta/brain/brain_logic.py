import os
import boto3
import json
import time
import logging
import redis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

REDIS_URL = os.getenv("REDIS_URL")

def send_heartbeat(worker_name):
    try:
        r = redis.from_url(REDIS_URL)
        r.set(f"health_{worker_name}", time.time())
    except Exception as e:
        print(f"Heartbeat error for {worker_name}: {e}")

INSIGHTS_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
SIGNALS_BUCKET = os.getenv("S3_SIGNALS_BUCKET", "quanta-signals")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
INSIGHTS_PREFIX = "insights/"
SIGNALS_PREFIX = "signals/"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def list_insight_keys():
    keys = []
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=INSIGHTS_BUCKET, Prefix=INSIGHTS_PREFIX):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('_merged.json'):  # only merged insights for now
                keys.append(obj['Key'])
    return keys

def analyze_insight(insight):
    rf_pred = None
    try:
        rf_pred = insight["models"]["RandomForest"]["prediction"]
    except Exception as e:
        logging.warning(f"RandomForest prediction missing: {e}")

    action = None
    if rf_pred == 1:
        action = "BUY"
    elif rf_pred == 0:
        action = "SELL"

    return {
        "id": insight.get("id"),
        "ticker": insight.get("raw_job", {}).get("ticker"),
        "date": insight.get("raw_job", {}).get("date"),
        "timestamp": insight.get("timestamp"),
        "action": action,
        "features": insight.get("features"),
        "raw_insight": insight
    }

def save_signal(signal):
    if not signal["action"]:
        return
    key = f'{SIGNALS_PREFIX}{signal["ticker"]}_{signal["date"]}_signal.json'
    s3.put_object(
        Bucket=SIGNALS_BUCKET,
        Key=key,
        Body=json.dumps(signal)
    )
    logging.info(f"Saved signal to {SIGNALS_BUCKET}/{key}")

def main():
    logging.info("[BRAIN LOGIC] Starting brain logic worker.")
    seen = set()
    while True:
        send_heartbeat("brain_logic_worker")
        keys = list_insight_keys()
        for key in keys:
            if key in seen:
                continue
            try:
                obj = s3.get_object(Bucket=INSIGHTS_BUCKET, Key=key)
                insight = json.loads(obj["Body"].read().decode())
                signal = analyze_insight(insight)
                save_signal(signal)
                seen.add(key)
            except Exception as e:
                logging.error(f"Failed to process {key}: {e}")
        time.sleep(120)  # Check every 2 min

if __name__ == "__main__":
    main()
