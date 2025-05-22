import os
import gzip
import pandas as pd
import concurrent.futures
import logging
import boto3
from botocore.config import Config
from quanta.crews.langchain_boot import boot_langchain_memory

TICKERS = ["NVDA", "AAPL", "TSLA", "SPY"]
S3_BUCKET = "flatfiles"
S3_PREFIX = "us_stocks_sip/minute_aggs_v1"
YEARS = range(2004, 2025)  # Or narrower for initial test
MONTHS = range(1, 13)

# Polygon S3 endpoint (from docs)
ENDPOINT_URL = "https://files.polygon.io"

def s3_session():
    return boto3.Session(
        aws_access_key_id=os.getenv("POLYGON_S3_KEY"),
        aws_secret_access_key=os.getenv("POLYGON_S3_SECRET"),
    )

def ingest_ticker(ticker):
    llm, embeddings, vectorstore = boot_langchain_memory()
    s3 = s3_session().client('s3', endpoint_url=ENDPOINT_URL, config=Config(signature_version='s3v4'))
    for year in YEARS:
        for month in MONTHS:
            for day in range(1, 32):  # Safe for calendar, will skip non-existent days
                key = f"{S3_PREFIX}/{year}/{month:02d}/{year}-{month:02d}-{day:02d}.csv.gz"
                try:
                    local_path = f"/tmp/{ticker}_{year}_{month:02d}_{day:02d}.csv.gz"
                    s3.download_file(S3_BUCKET, key, local_path)
                    with gzip.open(local_path, 'rt') as f:
                        df = pd.read_csv(f)
                    df = df[df['ticker'] == ticker]
                    records = df.astype(str).apply(lambda row: ','.join(row), axis=1).tolist()
                    batch_size = 1000
                    for i in range(0, len(records), batch_size):
                        batch = records[i:i + batch_size]
                        vectorstore.add_texts(batch)
                    logging.info(f"Ingested {len(df)} bars for {ticker} {year}-{month:02d}-{day:02d}")
                    os.remove(local_path)
                except Exception as e:
                    logging.warning(f"File {key} not found or error: {e}")
                    continue

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(ingest_ticker, TICKERS)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
