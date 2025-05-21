# quanta/mesh/mesh_supervisor.py

import threading
from quanta.mesh.agent_health_audit import AgentHealthAudit

class MeshSupervisor:
    def __init__(self, health_interval=5):
        # Initialize the AgentHealthAudit with the provided interval
        self.health_audit = AgentHealthAudit(check_interval=health_interval)
        self.keep_running = True
        self.thread = None

    def monitor_health(self):
        # Delegate all monitoring to AgentHealthAudit's monitor_agents method
        self.health_audit.monitor_agents()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        # Start the AgentHealthAudit monitoring in its own thread
        self.thread = threading.Thread(target=self.monitor_health)
        self.thread.start()

    def stop(self):
        self.keep_running = False
        if self.thread:
            self.health_audit.stop()
            self.thread.join()

if __name__ == "__main__":
    supervisor = MeshSupervisor(health_interval=5)
    supervisor.start()
    print("MeshSupervisor is running. Press Ctrl+C to stop.")
    try:
        while True:
            pass  # Keep the script alive
    except KeyboardInterrupt:
        print("\nStopping MeshSupervisor...")
        supervisor.stop()
        print("Supervisor stopped.")
