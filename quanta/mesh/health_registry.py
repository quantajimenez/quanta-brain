# quanta/mesh/health_registry.py

import redis
import json
import threading
from datetime import datetime
from quanta.utils.logger import setup_logger

logger = setup_logger("HealthRegistry")

redis_conn = redis.Redis.from_url("redis://localhost:6379")

# In-memory cache of last known agent states
agent_health_cache = {}

def store_beacon(beacon):
    agent = beacon["agent"]
    data = {
        "timestamp": beacon["timestamp"],
        "uptime": beacon["uptime"],
        "memory_usage": beacon["memory_usage"],
        "error_rate": beacon["error_rate"],
        "queue_length": beacon["queue_length"],
        "last_updated": datetime.utcnow().isoformat()
    }
    redis_conn.hset("quanta:agent_health", agent, json.dumps(data))
    logger.info(f"✅ Stored health status for {agent}")


def listen():
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("quanta:health_beacons")
    logger.info("📡 Listening to Redis channel: quanta:health_beacons")

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                beacon = json.loads(message['data'])
                store_beacon(beacon)
            except Exception as e:
                logger.error(f"❌ Failed to parse/store beacon: {e}")

if __name__ == "__main__":
    threading.Thread(target=listen).start()

