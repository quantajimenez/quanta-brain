import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "polygon")

def load_bars(ticker, date):
    fname = f"{ticker}_{date}.json"
    fpath = os.path.join(DATA_DIR, fname)
    print(f"Looking for file: {fpath}")
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return []
    with open(fpath, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    ticker = "NVDA"
    date = "2024-05-20"
    bars = load_bars(ticker, date)
    print(f"Loaded {len(bars)} bars for {ticker}")
    print(f"First 3 bars: {bars[:3]}")
