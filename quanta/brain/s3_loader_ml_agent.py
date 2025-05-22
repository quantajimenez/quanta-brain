import os
import boto3
import json
import pandas as pd
from datetime import datetime

# --- ENV ---
S3_BUCKET = "quanta-historical-marketdata"
TICKERS = ["SPY", "AAPL", "MSFT", "TSLA"]
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

# AWS credentials from environment
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

def get_s3_keys(bucket, prefix):
    """List all S3 file keys under prefix"""
    keys = []
    kwargs = {'Bucket': bucket, 'Prefix': prefix}
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp.get('Contents', []):
            keys.append(obj['Key'])
        if resp.get('IsTruncated'):
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        else:
            break
    return keys

def load_json_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj['Body'].read())

def analyze_and_train(ticker, data):
    # Dummy ML analysis: just calculate mean close price
    closes = [bar.get('close') for bar in data if bar.get('close') is not None]
    if closes:
        mean_close = sum(closes) / len(closes)
        print(f"[{ticker}] ML: Mean Close = {mean_close:.2f} for {len(closes)} bars")
    else:
        print(f"[{ticker}] ML: No data")
    # TODO: Replace with real ML model call (sklearn, keras, pytorch, etc)

def main():
    for ticker in TICKERS:
        prefix = f"polygon/{ticker}/"
        print(f"\n=== Processing {ticker} ===")
        keys = get_s3_keys(S3_BUCKET, prefix)
        print(f"Found {len(keys)} files in S3 for {ticker}.")
        for key in sorted(keys):
            date_str = key.split('/')[-1].replace('.json','')
            try:
                bars = load_json_from_s3(S3_BUCKET, key)
                analyze_and_train(ticker, bars)
            except Exception as e:
                print(f"Error loading/analyzing {key}: {e}")

if __name__ == "__main__":
    main()
