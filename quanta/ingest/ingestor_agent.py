# quanta/ingest/ingestor_agent.py

import time
from quanta.ingest.logging_utils import log_event

def ingest_event(event):
    # Time-stamp, validate, and store in vector DB (stub for now)
    event_dict = event.dict() if hasattr(event, "dict") else dict(event)
    event_dict["timestamp"] = time.time()
    # TODO: Store in FAISS/Chroma vector DB here
    log_event(event_dict)
    # print(f"[INGESTOR] Ingested event: {event_dict}")

