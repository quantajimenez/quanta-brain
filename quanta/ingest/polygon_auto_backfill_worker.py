import os
from polygon import RESTClient
from datetime import datetime, timedelta
import json

API_KEY = os.getenv("POLYGON_API_KEY")
TICKER = "SPY"
START_DATE = "2024-01-01"
END_DATE = "2024-01-01"  # Only 1 day for your test

# Write to Render's persistent disk
OUT_DIR = "/data/polygon/SPY"
os.makedirs(OUT_DIR, exist_ok=True)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def fetch_minute_bars(client, ticker, date):
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

def main():
    client = RESTClient(API_KEY)
    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(END_DATE, "%Y-%m-%d")

    for single_date in daterange(start_date, end_date):
        date_str = single_date.strftime("%Y-%m-%d")
        print(f"Downloading minute bars for {TICKER} {date_str}")
        bars = fetch_minute_bars(client, TICKER, date_str)
        out_path = f"{OUT_DIR}/{date_str}.json"
        with open(out_path, "w") as f:
            json.dump([bar.__dict__ for bar in bars], f)
        print(f"Saved data to {out_path}")

if __name__ == "__main__":
    main()
