# quanta/ingest/polygon_auto_backfill_worker.py

import os
from polygon import RESTClient
from datetime import datetime, timedelta
import json
import boto3
import logging

API_KEY = os.getenv("POLYGON_API_KEY")
TICKERS = ["SPY", "AAPL", "MSFT", "TSLA"]
START_DATE = "2014-01-01"
END_DATE = "2024-01-01"
S3_BUCKET = "quanta-historical-marketdata"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon_auto_backfill_worker")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2"),
)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def fetch_minute_bars(client, ticker, date):
    try:
        resp = client.get_aggs(
            ticker=ticker, multiplier=1, timespan="minute",
            from_=date, to=date, adjusted=True, sort="asc", limit=50000,
        )
        return resp
    except Exception as e:
        logger.error(f"Error fetching {ticker} for {date}: {e}")
        return []

def main():
    client = RESTClient(API_KEY)
    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(END_DATE, "%Y-%m-%d")
    for ticker in TICKERS:
        for single_date in daterange(start_date, end_date):
            date_str = single_date.strftime("%Y-%m-%d")
            logger.info(f"Downloading minute bars for {ticker} {date_str}")
            bars = fetch_minute_bars(client, ticker, date_str)
            data = json.dumps([bar.__dict__ for bar in bars])
            s3_key = f"polygon/{ticker}/{date_str}.json"
            try:
                s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=data)
                logger.info(f"Uploaded {s3_key} to s3://{S3_BUCKET}/{s3_key}")
            except Exception as e:
                logger.error(f"Error uploading {s3_key} to S3: {e}")

if __name__ == "__main__":
    main()
