# Quanta Agent Mesh Audit & Health API

## Audit Log Schema

Each log line looks like:

```
YYYY-MM-DDTHH:MM:SS.ssssss | EVENT_TYPE | AGENT_NAME | DETAILS
```

**Examples:**
```
2025-05-21T21:41:36.985834 | HEARTBEAT | strategist | StrategistAgent ping successful.
2025-05-21T21:41:38.998022 | STOP | ingestor | Ingestor agent stopped.
```

## Key API Endpoints

- `GET /agents`  
  Returns: List of all agents and their status.

- `GET /mesh/health`  
  Returns: Full mesh status, including escalations/unavailable agents.

- `GET /audit/logs?n=20`  
  Returns: Last N audit log lines.

- `GET /agents/health`  
  Returns: Last heartbeat timestamp for each agent.

- `POST /control/restart/{agent_name}`  
  Action: Restarts the named agent.

- `POST /control/start/{agent_name}`  
  Action: Starts the named agent.

- `POST /control/stop/{agent_name}`  
  Action: Stops the named agent.
