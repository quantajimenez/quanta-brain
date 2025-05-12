# quanta/status_registry/timestamp_registry.py

from datetime import datetime

timestamp_log = {}

def update_timestamp(module):
    timestamp_log[module] = datetime.utcnow().isoformat()
    print(f"[TIMESTAMP] {module} → {timestamp_log[module]}")

def get_timestamp(module):
    return timestamp_log.get(module, "N/A")
