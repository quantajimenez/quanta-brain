# quanta/ingest/polygon_data_batch_loader.py

import os
import json
import boto3
import logging

S3_BUCKET = os.getenv("QUANTA_HIST_S3_BUCKET", "quanta-historical-marketdata")
S3_PREFIX = "polygon"
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
DATES = ["2024-05-20", "2024-05-21", "2024-05-22"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon_data_batch_loader")

s3 = boto3.client("s3")

def load_bars_from_s3(ticker, date):
    key = f"{S3_PREFIX}/{ticker}_{date}.json"
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        bars = json.loads(obj['Body'].read().decode())
        logger.info(f"{key}: {len(bars)} bars")
        return bars
    except Exception as e:
        logger.warning(f"{key}: MISSING or ERROR: {e}")
        return []

for ticker in TICKERS:
    for date in DATES:
        load_bars_from_s3(ticker, date)
