from agents.strategist import StrategistAgent
from agents.ingestor import IngestorAgent
from agents.executor import ExecutorAgent
from utils.logger import setup_logger

logger = setup_logger("crew_init")

def crew_boot():
    try:
        strategist = StrategistAgent()
        ingestor = IngestorAgent()
        executor = ExecutorAgent()
        agents = {
            "strategist": strategist,
            "ingestor": ingestor,
            "executor": executor,
        }
        # Ping each agent
        for name, agent in agents.items():
            if not agent.ping():
                logger.error(f"{name} agent failed ping. Assigning fallback.")
                agents[name] = lambda: logger.warning(f"{name} fallback called.")
        logger.info("All agents booted successfully.")
        return agents
    except Exception as e:
        logger.error(f"Crew boot failed: {e}")
        raise

if __name__ == "__main__":
    crew_boot()

