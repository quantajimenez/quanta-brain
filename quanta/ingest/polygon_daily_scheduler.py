# quanta/ingest/polygon_daily_scheduler.py

import os
import requests
import json
from datetime import date
from multiprocessing import Pool

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/polygon")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_and_save(ticker):
    today = date.today().strftime("%Y-%m-%d")
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{today}/{today}"
        f"?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    )
    filename = os.path.join(DATA_DIR, f"{ticker}_{today}.json")
    if os.path.exists(filename):
        print(f"Already exists: {filename}")
        return
    try:
        print(f"Fetching {ticker} for {today} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filename, "w") as f:
            f.write(r.text)
        print(f"Saved {ticker} for {today}")
    except Exception as e:
        print(f"ERROR fetching {ticker} {today}: {e}")

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        pool.map(fetch_and_save, TICKERS)
