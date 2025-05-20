# quanta/ingest/integration_test.py

import requests

def test_webhook():
    url = "http://localhost:10000/webhook"
    payload = {"ticker": "AAPL", "price": 170.00}
    response = requests.post(url, json=payload)
    print(f"Test POST status: {response.status_code}, response: {response.json()}")

if __name__ == "__main__":
    test_webhook()

