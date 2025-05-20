# quanta/mesh/mesh_supervisor.py

import threading
import time
from quanta.mesh.orchestrator import AgentMeshOrchestrator
from quanta.mesh.audit_log import MeshAuditLogger  # Will create this in next step

class MeshSupervisor:
    def __init__(self, health_interval=5):
        self.orchestrator = AgentMeshOrchestrator()
        self.audit = MeshAuditLogger()
        self.health_interval = health_interval
        self.keep_running = True
        self.thread = None

    def monitor_health(self):
        while self.keep_running:
            for agent_name, agent in self.orchestrator.agents.items():
                try:
                    if not agent.ping():
                        self.audit.log_event('failure', agent_name, detail="Agent failed ping, triggering fallback")
                        self.orchestrator.restart_agent(agent_name)
                        self.audit.log_event('recovery', agent_name, detail="Agent restarted")
                    else:
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
