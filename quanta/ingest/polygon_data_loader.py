# quanta/ingest/polygon_data_loader.py

import os
import json
import boto3
import logging

S3_BUCKET = os.getenv("QUANTA_HIST_S3_BUCKET", "quanta-historical-marketdata")
S3_PREFIX = "polygon"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon_data_loader")

s3 = boto3.client("s3")

def load_bars(ticker, date):
    key = f"{S3_PREFIX}/{ticker}_{date}.json"
    logger.info(f"Looking for file: s3://{S3_BUCKET}/{key}")
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        bars = json.loads(obj['Body'].read().decode())
        logger.info(f"Loaded {len(bars)} bars for {ticker} on {date}")
        return bars
    except Exception as e:
        logger.warning(f"File not found or error: {e}")
        return []

if __name__ == "__main__":
    ticker = "NVDA"
    date = "2024-05-20"
    bars = load_bars(ticker, date)
    logger.info(f"First 3 bars: {bars[:3]}")
