# quanta/brain/brain_logic.py

import os
import boto3
import json
import time
import logging
from datetime import datetime

# --- Logging config ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- S3 Config ---
S3_INSIGHTS_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_SIGNALS_BUCKET = os.getenv("S3_SIGNALS_BUCKET", "quanta-signals")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
INSIGHTS_PREFIX = "insights/"

# --- S3 Client ---
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def list_all_insight_keys():
    keys = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_INSIGHTS_BUCKET, Prefix=INSIGHTS_PREFIX):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                keys.append(obj["Key"])
    return keys

def load_insight(key):
    obj = s3.get_object(Bucket=S3_INSIGHTS_BUCKET, Key=key)
    return json.loads(obj["Body"].read().decode())

def generate_alert_from_insight(insight):
    # Example rule: if any model predicts class 1 with >0.7, issue BUY; if class 0 with >0.7, SELL; else HOLD
    models = insight.get("models", {})
    ticker = insight.get("raw_job", {}).get("ticker", "UNKNOWN")
    date = insight.get("raw_job", {}).get("date", "UNKNOWN")
    id_ = insight.get("id", "")
    highest_buy = 0
    highest_sell = 0

    for model, result in models.items():
        try:
            prob = result["probabilities"]
            pred = result["prediction"]
            if pred == 1 and prob[1] > highest_buy:
                highest_buy = prob[1]
            if pred == 0 and prob[0] > highest_sell:
                highest_sell = prob[0]
        except Exception:
            continue

    if highest_buy >= 0.7:
        action = "BUY"
        confidence = highest_buy
    elif highest_sell >= 0.7:
        action = "SELL"
        confidence = highest_sell
    else:
        action = "HOLD"
        confidence = max(highest_buy, highest_sell)

    # Build the alert object
    alert = {
        "id": id_,
        "timestamp": datetime.utcnow().isoformat(),
        "ticker": ticker,
        "date": date,
        "action": action,
        "confidence": confidence,
        "models": models,
        "features": insight.get("features", []),
        "reasoning": f"Rule-based aggregation of ML model outputs. BUY if any model predicts class 1 with >0.7 prob, SELL if class 0 >0.7, else HOLD."
    }
    return alert

def store_alert(alert):
    key = f"alerts/{alert['ticker']}_{alert['date']}_{alert['action']}_{alert['id']}.json"
    s3.put_object(
        Bucket=S3_SIGNALS_BUCKET,
        Key=key,
        Body=json.dumps(alert)
    )
    logging.info(f"[BRAIN LOGIC] Stored alert: {key} | Action: {alert['action']} | Confidence: {alert['confidence']}")

def main():
    logging.info("[BRAIN LOGIC] Starting alert generation loop.")
    processed = set()  # To avoid double processing

    while True:
        keys = list_all_insight_keys()
        for key in keys:
            if key in processed:
                continue
            try:
                insight = load_insight(key)
                alert = generate_alert_from_insight(insight)
                store_alert(alert)
                processed.add(key)
            except Exception as e:
                logging.error(f"[BRAIN LOGIC] Error processing {key}: {e}")
        time.sleep(60)  # Check for new insights every minute

if __name__ == "__main__":
    main()
