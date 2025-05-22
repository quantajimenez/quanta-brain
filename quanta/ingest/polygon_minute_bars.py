import requests

# Official Quanta Polygon API Key (REPLACE with os.environ for production)
POLYGON_API_KEY = "zxrVbIvTfgf8YXteVAS1NajfZwPrWRrs"

def fetch_polygon_minute_bars(symbol: str, date: str, limit: int = 2):
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
        f"?adjusted=true&sort=asc&limit={limit}&apiKey={POLYGON_API_KEY}"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    bars = data.get("results", [])
    return bars

if __name__ == "__main__":
    # Example: NVDA on 2024-05-20
    bars = fetch_polygon_minute_bars("NVDA", "2024-05-20")
    print("Sample output (first 2 bars):")
    for bar in bars[:2]:
        print(bar)
