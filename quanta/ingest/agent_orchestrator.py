
import logging
import subprocess
import time

logger = logging.getLogger("ProcessOrchestrator")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

AGENTS = [
    "quanta.ingest.polygon_s3_ingest",
    "quanta.diagnostics.monitoring_agent"
    # Add more agents here as you scale (e.g., "quanta.analyze.stock_analyzer")
]

def start_agent(module):
    logger.info(f"Starting agent: {module}")
    try:
        process = subprocess.Popen(["python", "-m", module])
        logger.info(f"Started {module} (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"Failed to start {module}: {e}")
        return None

def main():
    logger.info("Launching all core agents via orchestrator...")
    processes = []
    for agent in AGENTS:
        proc = start_agent(agent)
        if proc:
            processes.append(proc)
    # Monitor processes
    try:
        while True:
            for i, proc in enumerate(processes):
                if proc.poll() is not None:  # Process died
                    logger.warning(f"Agent {AGENTS[i]} terminated unexpectedly. Restarting...")
                    processes[i] = start_agent(AGENTS[i])
            time.sleep(60)  # Monitor every 1 minute
    except KeyboardInterrupt:
        logger.info("Shutting down all agents...")
        for proc in processes:
            proc.terminate()

if __name__ == "__main__":
    main()
