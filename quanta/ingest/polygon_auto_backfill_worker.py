import os
from polygon import RESTClient
from datetime import datetime, timedelta
import json

API_KEY = os.getenv("POLYGON_API_KEY")
TICKER = "SPY"
START_DATE = "2024-01-01"
END_DATE = "2024-01-01"  # Only 1 day for your test

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

        # LOG FILE SIZE AND FIRST FEW LINES HERE
        try:
            file_size = os.path.getsize(out_path)
            print(f"File size: {file_size} bytes")

            with open(out_path, "r") as f:
                lines = f.readlines()
                # Print only the first 3 lines for brevity
                print(f"First 3 lines of file:\n{''.join(lines[:3])}")
        except Exception as e:
            print(f"Error reading output file for logs: {e}")

if __name__ == "__main__":
    main()
