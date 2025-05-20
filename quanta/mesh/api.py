# quanta/mesh/api.py

from fastapi import FastAPI, Query
from quanta.mesh.orchestrator import AgentMeshOrchestrator
from quanta.mesh.mesh_supervisor import MeshSupervisor
from quanta.mesh.audit_log import MeshAuditLogger

app = FastAPI()
orchestrator = AgentMeshOrchestrator()
supervisor = MeshSupervisor()
audit = MeshAuditLogger()

@app.get("/agents")
def get_agents():
    return {
        "agents": list(orchestrator.agents.keys()),
        "status": orchestrator.status
    }

@app.get("/mesh/health")
def get_mesh_health():
    return {
        "mesh_status": orchestrator.status,
        "escalations": {
            name: "unavailable"
            for name, status in orchestrator.status.items()
            if status == "unavailable"
        },
        "supervisor_running": supervisor.keep_running
    }

@app.get("/audit/logs")
def get_audit_logs(n: int = Query(20, description="Number of log lines")):
    logs = audit.query(last_n=n)
    return {
        "lines": logs
    }

@app.post("/control/restart/{agent_name}")
def restart_agent(agent_name: str):
    try:
        orchestrator.restart_agent(agent_name)
        return {"result": f"Restarted {agent_name}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quanta.mesh.api:app", host="0.0.0.0", port=12000, reload=True)
