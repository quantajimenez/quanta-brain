import os
import requests
import time
from datetime import datetime, timedelta

# CONFIGURE
API_KEY = os.environ.get("POLYGON_API_KEY", "zxrVbIvTfgf8YXteVAS1NajfZwPrWRs")  # Replace with your production key or keep env var
TICKERS = ["NVDA", "AAPL", "TSLA", "SPY"]
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 1, 31)
DATA_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "polygon")

def fetch_bars(ticker, date_str):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=asc&apiKey={API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    ensure_dir(DATA_ROOT)
    for ticker in TICKERS:
        ticker_dir = os.path.join(DATA_ROOT, ticker)
        ensure_dir(ticker_dir)
        current_date = START_DATE
        while current_date <= END_DATE:
            date_str = current_date.strftime("%Y-%m-%d")
            outpath = os.path.join(ticker_dir, f"{date_str}.json")
            if os.path.exists(outpath):
                print(f"[SKIP] {ticker} {date_str} already exists")
            else:
                try:
                    print(f"[FETCH] {ticker} {date_str}")
                    data = fetch_bars(ticker, date_str)
                    with open(outpath, "w") as f:
                        import json
                        json.dump(data, f)
                    print(f"[SUCCESS] {ticker} {date_str}")
                    time.sleep(0.5)  # throttle to avoid rate limits
                except Exception as e:
                    print(f"[ERROR] {ticker} {date_str}: {e}")
            current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
