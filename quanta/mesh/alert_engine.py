# quanta/mesh/alert_engine.py

import time
import redis
import json
from datetime import datetime, timedelta
from quanta.utils.logger import setup_logger
from quanta.ingest.alerts import send_insight_alert

logger = setup_logger("AlertEngine")
redis_conn = redis.Redis.from_url("redis://localhost:6379")
HEARTBEAT_TIMEOUT = 30  # seconds

last_seen = {}

def check_alerts():
    now = datetime.utcnow()
    for agent, last_time in last_seen.items():
        ts = datetime.fromisoformat(last_time)
        if (now - ts).total_seconds() > HEARTBEAT_TIMEOUT:
            alert_msg = f"⛔ Agent '{agent}' missed heartbeat!"
            logger.warning(alert_msg)
            send_insight_alert(alert_msg)

def monitor():
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("quanta:health_beacons")
    logger.info("🔍 Listening for heartbeats...")

    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
        try:
            beacon = json.loads(message['data'])
            last_seen[beacon["agent"]] = beacon["timestamp"]
            check_alerts()
        except Exception as e:
            logger.error(f"Failed to parse beacon: {e}")

if __name__ == "__main__":
    monitor()

