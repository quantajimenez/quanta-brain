# quanta/ingest/polygon_bulk_history_ingest.py

import os
import requests
import json
from datetime import date, timedelta
from multiprocessing import Pool

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
START_DATE = date(2023, 1, 1)
END_DATE = date(2024, 12, 31)
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/polygon")
os.makedirs(DATA_DIR, exist_ok=True)

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield (start_date + timedelta(n)).strftime("%Y-%m-%d")

def fetch_and_save(args):
    ticker, day = args
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{day}/{day}"
        f"?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    )
    filename = os.path.join(DATA_DIR, f"{ticker}_{day}.json")
    if os.path.exists(filename):
        print(f"Already exists: {filename}")
        return
    try:
        print(f"Fetching {ticker} for {day} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filename, "w") as f:
            f.write(r.text)
        print(f"Saved {ticker} for {day}")
    except Exception as e:
        print(f"ERROR fetching {ticker} {day}: {e}")

if __name__ == "__main__":
    jobs = []
    for ticker in TICKERS:
        for day in daterange(START_DATE, END_DATE):
            jobs.append((ticker, day))
    print(f"Total jobs: {len(jobs)}")
    # Number of agents = processes. Use 20 as per your paid Render plan.
    with Pool(processes=20) as pool:
        pool.map(fetch_and_save, jobs)
