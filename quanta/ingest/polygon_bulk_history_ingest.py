import requests
import json
import os

API_KEY = "zxrVbIvTfgf8YXteVAS1NajfZwPrWRrs"  # Update in Render as needed

# Minimal test tickers and dates (scale up later)
TICKERS = ["NVDA", "AAPL"]
DATES = ["2024-05-20"]

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "polygon")
os.makedirs(DATA_DIR, exist_ok=True)

for ticker in TICKERS:
    for date in DATES:
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/"
            f"{date}/{date}?adjusted=true&sort=asc&apiKey={API_KEY}"
        )
        print(f"Requesting: {url}")
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            bars = data.get("results", [])
            print(f"Fetched {len(bars)} bars for {ticker} on {date}")
            out_path = os.path.join(DATA_DIR, f"{ticker}_{date}.json")
            with open(out_path, "w") as f:
                json.dump(bars, f)
            print(f"Saved to {out_path}")
        else:
            print(f"Failed to fetch {ticker} on {date}: {resp.status_code} - {resp.text}")
