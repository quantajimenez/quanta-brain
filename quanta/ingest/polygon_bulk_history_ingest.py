import os
import requests
import json
from datetime import datetime, timedelta

API_KEY = os.getenv("POLYGON_API_KEY")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "polygon")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
DATES = [
    "2024-05-20",
    "2024-05-21",
    "2024-05-22"
]

def fetch_and_save(ticker, date):
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date}/{date}"
        f"?adjusted=true&sort=asc&apiKey={API_KEY}"
    )
    resp = requests.get(url)
    if resp.status_code == 200:
        bars = resp.json().get("results", [])
        fname = f"{ticker}_{date}.json"
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath, "w") as f:
            json.dump(bars, f)
        print(f"Saved {len(bars)} bars for {ticker} on {date} to {fname}")
    else:
        print(f"Failed to fetch {ticker} for {date}: {resp.status_code}")

if __name__ == "__main__":
    for ticker in TICKERS:
        for date in DATES:
            fetch_and_save(ticker, date)
