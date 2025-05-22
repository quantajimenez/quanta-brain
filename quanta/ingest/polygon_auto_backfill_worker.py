import os
from polygon import RESTClient
from datetime import datetime, timedelta

API_KEY = os.getenv("POLYGON_API_KEY", "<YOUR_POLYGON_API_KEY>")  # or hardcode for now

TICKER = "SPY"  # Change this to your ticker
START_DATE = "2024-01-01"
END_DATE = "2024-01-31"
OUT_DIR = "quanta/data/polygon/SPY"
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

if __name__ == "__main__":
    client = RESTClient(API_KEY)
    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")
    for single_date in daterange(start_dt, end_dt):
        ymd = single_date.strftime("%Y-%m-%d")
        try:
            print(f"[FETCH] {TICKER} {ymd}")
            bars = fetch_minute_bars(client, TICKER, ymd)
            # Save to file
            out_path = os.path.join(OUT_DIR, f"{ymd}.json")
            with open(out_path, "w") as f:
                import json
                json.dump([bar.__dict__ for bar in bars], f)
            print(f"[SUCCESS] {TICKER} {ymd} {len(bars)} bars")
        except Exception as e:
            print(f"[ERROR] {TICKER} {ymd} {e}")
