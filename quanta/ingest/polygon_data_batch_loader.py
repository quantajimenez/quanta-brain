import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "polygon")
TICKERS = ["NVDA", "TSLA", "AAPL", "SPY"]
DATES = ["2024-05-20", "2024-05-21", "2024-05-22"]

for ticker in TICKERS:
    for date in DATES:
        fname = f"{ticker}_{date}.json"
        fpath = os.path.join(DATA_DIR, fname)
        if not os.path.exists(fpath):
            print(f"{fname}: MISSING")
            continue
        with open(fpath, "r") as f:
            bars = json.load(f)
        print(f"{fname}: {len(bars)} bars")
