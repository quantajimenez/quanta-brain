# quanta/mesh/api.py

from fastapi import FastAPI
from quanta.mesh.orchestrator import AgentMeshOrchestrator

app = FastAPI()
orchestrator = AgentMeshOrchestrator()

@app.get("/agents")
def get_agents():
    return {"agents": list(orchestrator.agents.keys()), "status": orchestrator.status}

@app.get("/health")
def get_health():
    return {"status": orchestrator.status}

@app.post("/control/restart/{agent_name}")
def restart_agent(agent_name: str):
    # Placeholder: add restart logic as method in orchestrator
    return {"result": f"Restart requested for {agent_name}"}

# Add more endpoints as needed (metrics, logs, etc.)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quanta.mesh.api:app", host="0.0.0.0", port=12000, reload=True)
