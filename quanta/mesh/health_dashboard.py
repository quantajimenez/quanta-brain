# quanta/mesh/health_dashboard.py

from fastapi import FastAPI
from quanta.mesh.health_registry import agent_health_cache
from datetime import datetime

app = FastAPI()

@app.get("/dashboard")
def get_dashboard():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": agent_health_cache
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quanta.mesh.health_dashboard:app", host="0.0.0.0", port=8080)

