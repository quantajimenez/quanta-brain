# quanta/ingest/resilience.py

import time
import logging
from quanta.ingest.alerts import send_insight_alert

logger = logging.getLogger("resilience")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    logger.addHandler(handler)

def start_poller():
    # Poll fallback logic (poll every 15s if no webhooks)
    while True:
        # TODO: Check memory/store for recent events; if none, poll sources
        logger.info("[RESILIENCE] Poller tick")
        # If no new events for >2min, alert
        # send_insight_alert("No events in last 2 minutes!")
        time.sleep(15)
