# quanta/ingest/webhook_listener.py

from fastapi import FastAPI, Request, HTTPException
from quanta.ingest.payload_parser import parse_payload
from quanta.ingest.ingestor_agent import ingest_event
from quanta.ingest.alerts import send_insight_alert
from pydantic import BaseModel
import os
import logging
import json

app = FastAPI()

# --- New: Data Model and S3/file storage logic, as in main.py ---
class Insight(BaseModel):
    id: str
    prediction: int = None
    probabilities: list = []
    features: list = []
    timestamp: float = None
    raw_job: dict = {}

INSIGHTS_DIR = os.getenv("INSIGHTS_DIR", "brain_insights")
os.makedirs(INSIGHTS_DIR, exist_ok=True)

@app.post("/insight")
async def ingest_insight(insight: Insight):
    try:
        file_path = os.path.join(INSIGHTS_DIR, f"{insight.id}.json")
        with open(file_path, "w") as f:
            f.write(insight.json())
        logging.info(f"[ORCHESTRATOR] Stored insight {insight.id} to {file_path}")
        # TODO: Add DB, vectorstore, or retraining logic here
        return {"status": "success", "id": insight.id}
    except Exception as e:
        logging.error(f"[ORCHESTRATOR][ERROR] Failed to store insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Existing webhook endpoint remains unchanged ---
@app.post("/webhook")
async def webhook_endpoint(request: Request):
    try:
        data = await request.json()
        parsed = parse_payload(data)
        if not parsed['valid']:
            send_insight_alert(f"Invalid payload: {parsed['error']}")
            raise HTTPException(status_code=400, detail=parsed['error'])
        ingest_event(parsed['payload'])
        return {"status": "success"}
    except Exception as e:
        send_insight_alert(f"Webhook exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
