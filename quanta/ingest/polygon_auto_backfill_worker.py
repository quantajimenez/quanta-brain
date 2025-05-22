# quanta/ingest/polygon_auto_backfill_worker.py

import os
import requests
import threading
from datetime import datetime, timedelta
from time import sleep

# Your Render environment variable (or set directly here for local test)
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY") or "zxrVbIvTfgf8YXteVAS1NajfZwPrWRrs"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "polygon")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
START_YEAR = 2004
END_YEAR = 2024
MAX_THREADS = 10
BAR_TYPE = "minute"  # 1-min bars

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_bar_file(ticker, date, bars):
    target_dir = os.path.join(DATA_DIR, ticker)
    ensure_dir(target_dir)
    target_file = os.path.join(target_dir, f"{date}.json")
    with open(target_file, "w") as f:
        f.write(bars)

def fetch_day(ticker, date):
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/"
        f"{date}/{date}?adjusted=true&sort=asc&limit=50000&apiKey={POLYGON_API_KEY}"
    )
    r = requests.get(url)
    if r.status_code == 200:
        save_bar_file(ticker, date, r.text)
        print(f"[SUCCESS] {ticker} {date}")
    else:
        print(f"[ERROR] {ticker} {date} - Status {r.status_code} {r.text}")

def get_trading_days(start_year, end_year):
    days = []
    d = datetime(start_year, 1, 1)
    end = datetime(end_year + 1, 1, 1)
    while d < end:
        # Only weekdays (ignore holidays for now)
        if d.weekday() < 5:
            days.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return days

def worker(thread_id, jobs):
    for ticker, date in jobs:
        # Skip if already exists (resume support)
        fpath = os.path.join(DATA_DIR, ticker, f"{date}.json")
        if os.path.exists(fpath):
            print(f"[SKIP] {ticker} {date} already exists.")
            continue
        try:
            fetch_day(ticker, date)
        except Exception as e:
            print(f"[EXCEPTION] {ticker} {date} - {e}")
            sleep(2)

def run_ingestion():
    days = get_trading_days(START_YEAR, END_YEAR)
    all_jobs = [(ticker, date) for ticker in TICKERS for date in days]
    total = len(all_jobs)
    print(f"Total jobs: {total} ({len(TICKERS)} tickers, {len(days)} days)")

    # Split jobs into chunks for threads
    chunk_size = (total // MAX_THREADS) + 1
    threads = []
    for i in range(MAX_THREADS):
        jobs = all_jobs[i * chunk_size : (i + 1) * chunk_size]
        t = threading.Thread(target=worker, args=(i, jobs))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Ingestion complete!")

if __name__ == "__main__":
    run_ingestion()
