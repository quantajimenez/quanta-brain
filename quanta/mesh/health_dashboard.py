# quanta/mesh/health_dashboard.py

from fastapi import FastAPI
from datetime import datetime
import redis
import json

app = FastAPI()
redis_conn = redis.Redis.from_url("redis://localhost:6379")

@app.get("/dashboard")
def get_dashboard():
    raw_data = redis_conn.hgetall("quanta:agent_health")
    parsed = {
        agent.decode(): json.loads(payload.decode())
        for agent, payload in raw_data.items()
    }
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "agents": parsed
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quanta.mesh.health_dashboard:app", host="0.0.0.0", port=8080)

