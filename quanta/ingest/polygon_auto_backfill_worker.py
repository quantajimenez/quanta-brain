import os
from polygon import RESTClient
from datetime import datetime, timedelta
import json

API_KEY = os.getenv("POLYGON_API_KEY")
TICKER = "SPY"
# Use a recent weekday that is NOT a holiday or weekend. Example: Dec 18, 2023 (was a Monday)
DATE_TO_TEST = "2023-12-18"

OUT_DIR = f"/data/polygon/{TICKER}"
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_minute_bars(client, ticker, date):
    try:
        resp = client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="minute",
            from_=date,
            to=date,
            adjusted=True,
            sort="asc",
            limit=50000,
        )
        return resp
    except Exception as e:
        print(f"Error fetching {ticker} for {date}: {e}")
        return []

def main():
    client = RESTClient(API_KEY)
    date_str = DATE_TO_TEST
    print(f"Downloading minute bars for {TICKER} {date_str}")
    bars = fetch_minute_bars(client, TICKER, date_str)
    out_path = f"{OUT_DIR}/{date_str}.json"
    with open(out_path, "w") as f:
        json.dump([bar.__dict__ for bar in bars], f)
    print(f"Saved data to {out_path}")

    # File check output for Render logs:
    try:
        file_size = os.path.getsize(out_path)
        print(f"File size: {file_size} bytes")
        with open(out_path, "r") as f:
            lines = f.readlines()
            print(f"First 3 lines of file:\n{''.join(lines[:3])}")
    except Exception as e:
        print(f"Error reading {out_path} for logs: {e}")

if __name__ == "__main__":
    main()
