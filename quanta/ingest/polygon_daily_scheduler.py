import os
import requests
import json
from datetime import datetime

API_KEY = os.getenv("POLYGON_API_KEY")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "polygon")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]

def fetch_and_save(ticker, date):
    date_str = date.strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&apiKey={API_KEY}"
    print(f"Fetching {ticker} for {date_str} ...")
    resp = requests.get(url)
    if resp.status_code == 200:
        bars = resp.json().get("results", [])
        fname = f"{ticker}_{date_str}.json"
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath, "w") as f:
            json.dump(bars, f)
        print(f"Saved {len(bars)} bars to {fname}")
    else:
        print(f"Failed to fetch {ticker} for {date_str}: {resp.status_code}")

if __name__ == "__main__":
    today = datetime.now()
    for ticker in TICKERS:
        fetch_and_save(ticker, today)
