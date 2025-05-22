import os
import json

TICKER = "NVDA"
DATE = "2024-05-20"

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "polygon", f"{TICKER}_{DATE}.json")

print(f"Looking for file: {DATA_PATH}")

if not os.path.exists(DATA_PATH):
    print(f"File not found: {DATA_PATH}")
    bars = []
else:
    with open(DATA_PATH, "r") as f:
        bars = json.load(f)

print(f"Loaded {len(bars)} bars for {TICKER}")
print("First 3 bars:", bars[:3])
