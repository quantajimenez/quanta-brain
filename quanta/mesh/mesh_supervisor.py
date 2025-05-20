# quanta/mesh/mesh_supervisor.py

import threading
import time
from quanta.mesh.orchestrator import AgentMeshOrchestrator
from quanta.mesh.audit_log import MeshAuditLogger

class MeshSupervisor:
    def __init__(self, health_interval=5):
        self.orchestrator = AgentMeshOrchestrator()
        self.audit = MeshAuditLogger()
        self.health_interval = health_interval
        self.keep_running = True
        self.thread = None
        # Track consecutive agent failures for escalation logic
        self.failure_count = {name: 0 for name in self.orchestrator.agents}

    def monitor_health(self):
        while self.keep_running:
            for agent_name, agent in self.orchestrator.agents.items():
                try:
                    if not agent.ping():
                        self.failure_count[agent_name] += 1
                        self.audit.log_event(
                            'failure', agent_name,
                            detail=f"Agent failed ping, count={self.failure_count[agent_name]}"
                        )
                        if self.failure_count[agent_name] >= 3:
                            self.audit.log_event(
                                'escalation', agent_name,
                                detail="Agent marked unavailable after 3 failures"
                            )
                            self.orchestrator.status[agent_name] = "unavailable"
                            continue  # Do not restart anymore for this agent
                        self.orchestrator.restart_agent(agent_name)
                        self.audit.log_event('recovery', agent_name, detail="Agent restarted")
                    else:
                        self.failure_count[agent_name] = 0  # Reset on success
                        self.audit.log_event('heartbeat', agent_name, detail="Agent healthy")
                except Exception as e:
                    self.audit.log_event('error', agent_name, detail=f"Health check error: {str(e)}")
            time.sleep(self.health_interval)

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.monitor_health)
        self.thread.start()

    def stop(self):
        self.keep_running = False
        if self.thread:
            self.thread.join()
