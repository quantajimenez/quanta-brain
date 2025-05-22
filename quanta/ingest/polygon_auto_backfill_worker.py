import os
import json
import datetime
from polygon import RESTClient
from tqdm import tqdm

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "YOUR_POLYGON_API_KEY")
TICKERS = ["SPY", "AAPL", "NVDA", "TSLA"]
START_DATE = "2024-01-01"    # Use 'YYYY-MM-DD' for 1 month (adjust as needed)
END_DATE = "2024-01-31"      # Inclusive; can automate this to today for rolling ingest
OUTPUT_BASE = "quanta/data/polygon"

def fetch_and_save(client, ticker, date):
    try:
        resp = client.stocks_equities_aggregates(
            ticker=ticker,
            multiplier=1,
            timespan="minute",
            from_=date,
            to=date,
            adjusted=True,
            sort="asc",
            limit=50000
        )
        bars = resp['results'] if 'results' in resp else []
        if not bars:
            print(f"[NO DATA] {ticker} {date}")
            return
        # --- Create output directory if missing ---
        ticker_dir = os.path.join(OUTPUT_BASE, ticker)
        os.makedirs(ticker_dir, exist_ok=True)
        out_path = os.path.join(ticker_dir, f"{date}.json")
        with open(out_path, "w") as f:
            json.dump(bars, f)
        print(f"[SUCCESS] {ticker} {date} -> {out_path} ({len(bars)} bars)")
    except Exception as e:
        print(f"[ERROR] {ticker} {date} {e}")

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield (start_date + datetime.timedelta(n)).strftime("%Y-%m-%d")

if __name__ == "__main__":
    client = RESTClient(POLYGON_API_KEY)
    start = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")
    for ticker in TICKERS:
        for date in tqdm(list(daterange(start, end)), desc=f"{ticker}"):
            fetch_and_save(client, ticker, date)
