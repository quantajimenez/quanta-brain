# quanta/ingest/polygon_bulk_history_ingest.py

import os
import requests
import json
from datetime import date, timedelta
from multiprocessing import Pool
import boto3
import logging

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
START_DATE = date(2023, 1, 1)
END_DATE = date(2024, 12, 31)
S3_BUCKET = os.getenv("QUANTA_HIST_S3_BUCKET", "quanta-historical-marketdata")
S3_PREFIX = "polygon_bulk"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon_bulk_history_ingest")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2"),
)

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield (start_date + timedelta(n)).strftime("%Y-%m-%d")

def fetch_and_save(args):
    ticker, day = args
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{day}/{day}"
        f"?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    )
    s3_key = f"{S3_PREFIX}/{ticker}_{day}.json"
    try:
        logger.info(f"Fetching {ticker} for {day} ...")
        r = requests.get(url)
        r.raise_for_status()
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=r.text)
        logger.info(f"Saved {ticker} for {day} to S3: {s3_key}")
    except Exception as e:
        logger.error(f"ERROR fetching {ticker} {day}: {e}")

if __name__ == "__main__":
    jobs = []
    for ticker in TICKERS:
        for day in daterange(START_DATE, END_DATE):
            jobs.append((ticker, day))
    logger.info(f"Total jobs: {len(jobs)}")
    # Number of agents = processes. Use 20 as per your paid Render plan.
    with Pool(processes=20) as pool:
        pool.map(fetch_and_save, jobs)
