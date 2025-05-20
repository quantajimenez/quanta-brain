# quanta/ingest/logging_utils.py

import logging

def log_event(event):
    logging.info(f"[LOG] Event: {event}")
    # TODO: Save to S3/object storage if needed

