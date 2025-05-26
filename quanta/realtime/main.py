# quanta/realtime/main.py  

from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel
import threading
import uvicorn
import logging
import os
import json

# Import all sub-API FastAPI apps
from quanta.mesh.api import app as mesh_api
from quanta.ingest.webhook_listener import app as ingest_api
from quanta.mesh.health_dashboard import app as health_api

from quanta.brain.youtube_router import router as youtube_router

orchestrator_app = FastAPI(title="Quanta Unified Orchestrator")

# Mount full FastAPI sub-apps under specific prefixes
orchestrator_app.mount("/mesh", mesh_api)
orchestrator_app.mount("/ingest", ingest_api)
orchestrator_app.mount("/health", health_api)

# Register lightweight routers directly (like YouTube)
api_router = APIRouter()
api_router.include_router(youtube_router, prefix="/youtube")
orchestrator_app.include_router(api_router)

# --- INSIGHTS ENDPOINT ---
class Insight(BaseModel):
    id: str
    prediction: int = None
    probabilities: list = []
    features: list = []
    timestamp: float = None
    raw_job: dict = {}

INSIGHTS_DIR = os.getenv("INSIGHTS_DIR", "brain_insights")
os.makedirs(INSIGHTS_DIR, exist_ok=True)

@orchestrator_app.post("/ingest/insight")
async def ingest_insight(insight: Insight):
    try:
        file_path = os.path.join(INSIGHTS_DIR, f"{insight.id}.json")
        with open(file_path, "w") as f:
            f.write(insight.json())
        logging.info(f"[ORCHESTRATOR] Stored insight {insight.id} to {file_path}")
        # TODO: Add DB, vectorstore, or retraining logic here (meta-model trigger)
        return {"status": "success", "id": insight.id}
    except Exception as e:
        logging.error(f"[ORCHESTRATOR][ERROR] Failed to store insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@orchestrator_app.get("/")
def root():
    return {"status": "Quanta Unified Orchestrator is live"}

from quanta.ingest.resilience import start_poller

def start_background_poller():
    threading.Thread(target=start_poller, daemon=True).start()

if __name__ == "__main__":
    start_background_poller()
    uvicorn.run("quanta.realtime.main:orchestrator_app", host="0.0.0.0", port=11000, reload=False)
