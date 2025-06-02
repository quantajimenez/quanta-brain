# quanta/realtime/main.py

from fastapi import FastAPI, APIRouter
import threading
import uvicorn

# Sub-app FastAPI instances
from quanta.mesh.api import app as mesh_api
from quanta.ingest.webhook_listener import app as ingest_api
from quanta.mesh.health_dashboard import app as health_api

# Routers (lightweight, like YouTube)
from quanta.brain.youtube_router import router as youtube_router

# Main orchestrator app
orchestrator_app = FastAPI(title="Quanta Unified Orchestrator")

# Mount full sub-apps
orchestrator_app.mount("/mesh", mesh_api)
orchestrator_app.mount("/ingest", ingest_api)
orchestrator_app.mount("/health", health_api)

# Mount lightweight routers using a shared router (recommended style)
api_router = APIRouter()
api_router.include_router(youtube_router, prefix="/youtube")

# Attach to app
orchestrator_app.include_router(api_router)

# Root healthcheck
@orchestrator_app.get("/")
def root():
    return {"status": "Quanta Unified Orchestrator is live"}

# Background poller (optional)
from quanta.ingest.resilience import start_poller

def start_background_poller():
    threading.Thread(target=start_poller, daemon=True).start()

if __name__ == "__main__":
    start_background_poller()
    uvicorn.run("quanta.realtime.main:orchestrator_app", host="0.0.0.0", port=11000, reload=False)
