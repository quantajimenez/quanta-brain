# quanta/mesh/audit_log.py

import datetime
import threading
import os

class MeshAuditLogger:
    def __init__(self, filename=None):
        # Use persistent disk on Render (or fallback to repo logs/ in dev)
        logdir = "/logs" if os.path.isdir("/logs") else os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        os.makedirs(logdir, exist_ok=True)
        self.filename = filename or os.path.join(logdir, "mesh_audit.log")
        self.lock = threading.Lock()

    def log_event(self, event_type, agent, detail=""):
        entry = f"{datetime.datetime.utcnow().isoformat()} | {event_type.upper()} | {agent} | {detail}\n"
        with self.lock:
            with open(self.filename, "a") as f:
                f.write(entry)

    def query(self, last_n=100):
        with self.lock:
            if not os.path.exists(self.filename):
                return []
            with open(self.filename, "r") as f:
                return f.readlines()[-last_n:]
