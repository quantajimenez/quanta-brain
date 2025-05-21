# quanta/mesh/alert_engine.py

import time
import redis
import json
from datetime import datetime
from quanta.utils.logger import setup_logger
from quanta.ingest.alerts import send_insight_alert

logger = setup_logger("AlertEngine")

# Redis connection
redis_conn = redis.Redis.from_url("redis://localhost:6379")

# Threshold to trigger alert (in seconds)
HEARTBEAT_TIMEOUT = 30

# Track the last time we saw each agent
last_seen = {}

def check_alerts():
    now = datetime.utcnow()
    for agent, last_time_str in last_seen.items():
        try:
            last_time = datetime.fromisoformat(last_time_str)
            if (now - last_time).total_seconds() > HEARTBEAT_TIMEOUT:
                alert_msg = f"⛔ Agent '{agent}' missed heartbeat!"
                logger.warning(alert_msg)
                send_insight_alert(alert_msg)
        except Exception as e:
            logger.error(f"Timestamp parse error for {agent}: {e}")

def monitor():
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("quanta:health_beacons")
    logger.info("🔍 Listening for heartbeats...")

    while True:
        try:
            # Non-blocking get_message
            message = pubsub.get_message(timeout=1.0)
            if message and message['type'] == 'message':
                try:
                    beacon = json.loads(message['data'])
                    last_seen[beacon["agent"]] = beacon["timestamp"]
                except Exception as e:
                    logger.error(f"Failed to parse beacon: {e}")
            check_alerts()  # Always check timeouts
            time.sleep(1)
        except Exception as e:
            logger.error(f"Alert engine error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    monitor()


if __name__ == "__main__":
    monitor()

