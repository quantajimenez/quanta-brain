# quanta/ingest/polygon_daily_scheduler.py

import os
import requests
import json
from datetime import date
from multiprocessing import Pool
import boto3
import logging

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
S3_BUCKET = os.getenv("QUANTA_HIST_S3_BUCKET", "quanta-historical-marketdata")
S3_PREFIX = "polygon"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon_daily_scheduler")

s3 = boto3.client("s3")

def fetch_and_save(ticker):
    today = date.today().strftime("%Y-%m-%d")
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{today}/{today}"
        f"?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    )
    s3_key = f"{S3_PREFIX}/{ticker}_{today}.json"
    try:
        logger.info(f"Fetching {ticker} for {today} ...")
        r = requests.get(url)
        r.raise_for_status()
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=r.text)
        logger.info(f"Saved {ticker} for {today} to S3: {s3_key}")
    except Exception as e:
        logger.error(f"ERROR fetching {ticker} {today}: {e}")

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        pool.map(fetch_and_save, TICKERS)
