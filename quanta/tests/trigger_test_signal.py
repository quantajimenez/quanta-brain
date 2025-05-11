import requests
import json

test_data = {
    "ticker": "SPY",
    "price": "545.90",
    "signal": "SUPPORT_RECLAIM",
    "confidence": "HIGH",
    "Type": "CALL",
    "strike": "540",
    "expiry": "2025-05-15",
    "session": "REGULAR"
}

webhook_url = "https://<your-render-url>/webhook"  # Replace with your live URL
response = requests.post(webhook_url, json=test_data)
print("POST sent. Status:", response.status_code)
print(response.text)
