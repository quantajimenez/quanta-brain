# quanta/realtime/main.py

from fastapi import FastAPI
import threading
import uvicorn

# Import all routers/apps you want to expose under the unified orchestrator
from quanta.mesh.api import app as mesh_api
from quanta.ingest.webhook_listener import app as ingest_api
from quanta.mesh.health_dashboard import app as health_api

# (Add other routers here as your platform grows, e.g., insights, brain, etc.)

orchestrator_app = FastAPI(title="Quanta Unified Orchestrator")

# Mount all relevant sub-APIs under their own prefixes
orchestrator_app.mount("/mesh", mesh_api)
orchestrator_app.mount("/ingest", ingest_api)
orchestrator_app.mount("/health", health_api)

# Health check root endpoint
@orchestrator_app.get("/")
def root():
    return {"status": "Quanta Unified Orchestrator is live"}

# Background service example: start resilience poller thread
from quanta.ingest.resilience import start_poller

def start_background_poller():
    threading.Thread(target=start_poller, daemon=True).start()

if __name__ == "__main__":
    start_background_poller()
    uvicorn.run("quanta.realtime.main:orchestrator_app", host="0.0.0.0", port=11000, reload=False)
