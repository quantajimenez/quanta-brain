
from quanta.mesh.orchestrator import AgentMeshOrchestrator
from quanta.mesh.audit_log import MeshAuditLogger
from quanta.status_registry.status_tracker import update_status
from quanta.status_registry.timestamp_registry import update_timestamp
import threading
import time

class AgentHealthAudit:
    def __init__(self, check_interval=10):
        self.orchestrator = AgentMeshOrchestrator()
        self.audit = MeshAuditLogger()
        self.check_interval = check_interval
        self.keep_running = True
        self.thread = None

    def monitor_agents(self):
        while self.keep_running:
            for name, agent in self.orchestrator.agents.items():
                try:
                    alive = agent.ping()
                    status = "running" if alive else "failed"
                    update_status(name, status)
                    update_timestamp(name)
                    self.audit.log_event("heartbeat" if alive else "failure", name)
                    if not alive:
                        self.alert_admin(name)
                except Exception as e:
                    self.audit.log_event("error", name, str(e))
            time.sleep(self.check_interval)

    def log_event(self, event_type, agent, detail=""):
        self.audit.log_event(event_type, agent, detail)

    def alert_admin(self, agent_name):
        # For now, this just logs. In production, you might email/text/Slack alert.
        self.audit.log_event("escalation", agent_name, "Admin alert triggered")

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.monitor_agents)
        self.thread.start()

    def stop(self):
        self.keep_running = False
        if self.thread:
            self.thread.join()
