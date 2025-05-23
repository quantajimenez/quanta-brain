# quanta/execution/trade_outcome_log.py

import logging
import json
import os
import boto3
from datetime import datetime

S3_BUCKET = os.getenv("QUANTA_LOG_S3_BUCKET", "quanta-execution-logs")
S3_PREFIX = os.getenv("QUANTA_LOG_S3_PREFIX", "trade_outcomes")

logger = logging.getLogger("quanta.execution.trade_outcome_log")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_trade_outcome(ticker, result, pnl, confidence, reason=""):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ticker": ticker,
        "result": result,
        "pnl": pnl,
        "confidence": confidence,
        "reason": reason
    }
    logger.info(f"[TRADE OUTCOME] {json.dumps(log_entry)}")
    # Save to S3
    s3 = boto3.client("s3")
    key = f"{S3_PREFIX}/{ticker}/{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(log_entry))
