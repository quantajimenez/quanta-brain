import os
import requests

# Get API key from environment variable (set in Render dashboard)
POLYGON_API_KEY = os.environ["POLYGON_API_KEY"]

def fetch_minute_bars(symbol, date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get('results', [])

if __name__ == "__main__":
    # Example: NVDA on 2024-05-20
    bars = fetch_minute_bars("NVDA", "2024-05-20")
    print("Sample output (first 2 bars):")
    for bar in bars[:2]:
        print(bar)
