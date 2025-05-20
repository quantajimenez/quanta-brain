# quanta/mesh/orchestrator.py

from quanta.crews.crew_init import crew_boot
from quanta.status_registry.status_tracker import update_status, get_status
from quanta.utils.logger import setup_logger
import threading
import time

class AgentMeshOrchestrator:
    def __init__(self):
        self.logger = setup_logger("AgentMeshOrchestrator")
        self.agents = crew_boot()  # Leverages existing agent bootstrap
        self.status = {name: "initialized" for name in self.agents}
        for name in self.agents:
            update_status(name, "initialized")

    def register_agent(self, agent_name, agent_instance):
        self.agents[agent_name] = agent_instance
        self.status[agent_name] = "registered"
        update_status(agent_name, "registered")
        self.logger.info(f"Registered agent: {agent_name}")

    def monitor_agents(self):
        while True:
            for name, agent in self.agents.items():
                try:
                    alive = agent.ping()
                    new_status = "running" if alive else "failed"
                    if self.status[name] != new_status:
                        self.status[name] = new_status
                        update_status(name, new_status)
                        self.logger.info(f"Agent {name} status updated to {new_status}")
                except Exception as e:
                    self.status[name] = "error"
                    update_status(name, "error")
                    self.logger.error(f"Agent {name} error: {e}")
            time.sleep(10)

    def restart_agent(self, agent_name):
        self.logger.info(f"Restarting agent: {agent_name}")
        if agent_name in self.agents:
            agent_class = type(self.agents[agent_name])
            self.agents[agent_name] = agent_class()
            self.status[agent_name] = "restarted"
            self.logger.info(f"Agent {agent_name} restarted successfully.")
        else:
            self.logger.error(f"Agent {agent_name} not found for restart.")

    def start_agent(self, agent_name):
        self.logger.info(f"Starting agent: {agent_name}")
        if agent_name in self.agents:
            self.status[agent_name] = "running"
            self.logger.info(f"Agent {agent_name} started.")
        else:
            self.logger.error(f"Cannot start unknown agent: {agent_name}")

    def stop_agent(self, agent_name):
        self.logger.info(f"Stopping agent: {agent_name}")
        if agent_name in self.agents:
            self.status[agent_name] = "stopped"
            self.logger.info(f"Agent {agent_name} stopped.")
        else:
            self.logger.error(f"Agent {agent_name} not found for stop.")

if __name__ == "__main__":
    orchestrator = AgentMeshOrchestrator()
    threading.Thread(target=orchestrator.monitor_agents).start()
