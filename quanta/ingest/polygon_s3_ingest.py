# quanta/ingest/polygon_s3_ingest.py

import boto3
from botocore.config import Config
import os
import gzip
import pandas as pd
from datetime import datetime

# --- S3 Credentials (Load from environment variables) ---
POLYGON_ACCESS_KEY = os.getenv('POLYGON_S3_ACCESS_KEY')
POLYGON_SECRET_KEY = os.getenv('POLYGON_S3_SECRET_KEY')

if not POLYGON_ACCESS_KEY or not POLYGON_SECRET_KEY:
    raise Exception("Polygon S3 credentials not set in environment variables.")

session = boto3.Session(
    aws_access_key_id=POLYGON_ACCESS_KEY,
    aws_secret_access_key=POLYGON_SECRET_KEY
)

s3 = session.client(
    's3',
    endpoint_url='https://files.polygon.io',
    config=Config(signature_version='s3v4')
)

# --- Download Parameters ---
year = '2025'
month = '05'
prefix = f'us_stocks_sip/minute_aggs_v1/{year}/{month}/'
output_dir = f'downloads/{year}/{month}'
os.makedirs(output_dir, exist_ok=True)

response = s3.list_objects_v2(Bucket='flatfiles', Prefix=prefix)
files = response.get('Contents', [])

if not files:
    print("No files found.")
    exit(1)

obj = files[0]
filename = obj['Key'].split('/')[-1]
local_path = os.path.join(output_dir, filename)
print(f"Downloading {obj['Key']} --> {local_path}")
s3.download_file('flatfiles', obj['Key'], local_path)
print(f"Done: {local_path}")

print("\nDecompressing and previewing CSV contents...")
with gzip.open(local_path, 'rt') as f:
    df = pd.read_csv(f)

print("Loaded DataFrame shape:", df.shape)
print("Columns:", df.columns.tolist())
print("First 5 rows:")
print(df.head())

TARGET_TICKERS = ['SPY', 'TSLA', 'NVDA', 'AAPL']
df = df[df['ticker'].isin(TARGET_TICKERS)]
print(f"Filtered DataFrame shape: {df.shape}")

def ingest_minute_bar(row):
    event = {
        "ticker": row['ticker'],
        "event_type": "stock_bar",
        "timestamp": int(row['window_start']),
        "datetime": datetime.utcfromtimestamp(int(str(row['window_start'])[:10])).isoformat() + "Z",
        "open": row['open'],
        "high": row['high'],
        "low": row['low'],
        "close": row['close'],
        "volume": row['volume'],
        "num_trades": row['transactions']
    }
    print(event)

print("\nIngesting first 10 bars as sample:")
for idx, row in df.iterrows():
    ingest_minute_bar(row)
    if idx >= 9:
        break

print(f"\nParsed {min(10, len(df))} 1-min bar events (sample) for {TARGET_TICKERS}")
