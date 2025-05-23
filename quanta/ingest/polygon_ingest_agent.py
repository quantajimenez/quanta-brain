# quanta/ingest/polygon_ingest_agent.py

import os
import requests
import json
import boto3
import logging

API_KEY = os.getenv("POLYGON_API_KEY")
S3_BUCKET = os.getenv("QUANTA_HIST_S3_BUCKET", "quanta-historical-marketdata")
S3_PREFIX = "polygon"
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
DATES = ["2024-05-20", "2024-05-21", "2024-05-22"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon_ingest_agent")

s3 = boto3.client("s3")

def fetch_and_save(ticker, date):
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date}/{date}"
        f"?adjusted=true&sort=asc&apiKey={API_KEY}"
    )
    resp = requests.get(url)
    if resp.status_code == 200:
        bars = resp.json().get("results", [])
        key = f"{S3_PREFIX}/{ticker}_{date}.json"
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(bars))
        logger.info(f"Saved {len(bars)} bars to s3://{S3_BUCKET}/{key}")
    else:
        logger.error(f"Failed to fetch {ticker} for {date}: {resp.status_code}")

if __name__ == "__main__":
    for ticker in TICKERS:
        for date in DATES:
            logger.info(f"Fetching {ticker} for {date} ...")
            fetch_and_save(ticker, date)
