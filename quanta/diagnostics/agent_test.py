from crews.crew_init import crew_boot
from utils.logger import setup_logger

logger = setup_logger("agent_test")

def run_agent_diagnostics():
    logger.info("Running agent diagnostics...")
    agents = crew_boot()
    results = {}
    for name, agent in agents.items():
        try:
            status = agent.ping()
            results[name] = status
            logger.info(f"{name} agent ping: {'✅' if status else '❌'}")
        except Exception as e:
            logger.error(f"Error pinging {name}: {e}")
            results[name] = False
    logger.info(f"Diagnostics results: {results}")
    return results

if __name__ == "__main__":
    run_agent_diagnostics()

