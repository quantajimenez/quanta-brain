import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

RENDER_API_KEY = os.getenv("RENDER_API_KEY")
SERVICE_ID = os.getenv("RENDER_SERVICE_ID")  # e.g., srv-xxxx
CHECK_INTERVAL_MINUTES = 10  # log freshness window

def get_latest_logs():
    headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/logs?limit=1"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logs = response.json()
        if logs and "logs" in logs and logs["logs"]:
            return logs["logs"][0]
    return None

def parse_timestamp(ts_str):
    try:
        return datetime.datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")

def check_log_health():
    latest_log = get_latest_logs()
    if not latest_log:
        print("[⚠️] No logs returned. Render service may be down.")
        return

    timestamp = parse_timestamp(latest_log["timestamp"])
    now = datetime.datetime.utcnow()
    delta = now - timestamp

    if delta.total_seconds() > CHECK_INTERVAL_MINUTES * 60:
        print(f"[❌] Quanta appears inactive. Last log was {delta} ago.")
        # Placeholder: log to Quanta memory or escalate
    else:
        print(f"[✅] Quanta is active. Last log at {timestamp} UTC.")

if __name__ == "__main__":
    check_log_health()
