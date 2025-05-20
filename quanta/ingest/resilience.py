# quanta/ingest/resilience.py

import time
from quanta.ingest.alerts import send_insight_alert

def start_poller():
    # Poll fallback logic (poll every 15s if no webhooks)
    while True:
        # TODO: Check memory/store for recent events; if none, poll sources
        # This is a stub!
        print("[RESILIENCE] Poller tick")
        time.sleep(15)
        # If no new events for >2min, alert
        # send_insight_alert("No events in last 2 minutes!")

