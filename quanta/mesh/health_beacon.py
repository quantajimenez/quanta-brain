# quanta/mesh/health_beacon.py

import time
import json
import redis
import psutil
from datetime import datetime
from quanta.utils.logger import setup_logger

logger = setup_logger("HealthBeaconAgent")

# Adjust to your actual Redis connection (local or Upstash)
REDIS_URL = "redis://localhost:6379"
redis_conn = redis.Redis.from_url(REDIS_URL)

def emit_heartbeat(agent_name):
    beacon = {
        "agent": agent_name,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": int(time.time() - psutil.boot_time()),  # uptime in seconds
        "memory_usage": psutil.virtual_memory().percent,
        "error_rate": 0.0,  # Placeholder (replace with actual tracking if needed)
        "queue_length": 0   # Placeholder (replace if your agent uses queues)
    }
    redis_conn.publish("quanta:health_beacons", json.dumps(beacon))
    logger.info(f"✅ Heartbeat sent: {beacon}")

if __name__ == "__main__":
    agent_name = "strategist"  # Set this dynamically per agent later
    while True:
        emit_heartbeat(agent_name)
        time.sleep(10)

