import logging
import subprocess
import time
import requests

logger = logging.getLogger("ProcessOrchestrator")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ✅ All agents managed by the orchestrator
AGENTS = [
    "quanta.ingest.polygon_s3_ingest",
    "quanta.diagnostics.monitoring_agent",
    "quanta.ingest.youtube_pattern_agent"  # ✅ Your batch-mode agent
]

# ✅ Agents that are expected to exit cleanly
AGENTS_BATCH = [
    "quanta.ingest.youtube_pattern_agent"
]

HEALTH_URL = "http://localhost:8181/health"  # Health check endpoint

def start_agent(module):
    logger.info(f"Starting agent: {module}")
    try:
        process = subprocess.Popen(["python", "-m", module])
        logger.info(f"Started {module} (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"Failed to start {module}: {e}")
        return None

def report_orchestrator_health():
    try:
        requests.get(HEALTH_URL, timeout=2)
        logger.info("Health check: orchestrator is alive.")
    except Exception as e:
        logger.warning(f"Orchestrator health check failed: {e}")

def main():
    logger.info("Launching all core agents via orchestrator...")
    processes = []
    for agent in AGENTS:
        proc = start_agent(agent)
        processes.append(proc)

    try:
        while True:
            for i, (agent_name, proc) in enumerate(zip(AGENTS, processes)):
                if proc is None:
                    continue

                if proc.poll() is not None:  # Agent exited
                    if agent_name in AGENTS_BATCH:
                        logger.info(f"✅ Batch agent {agent_name} completed successfully.")
                        processes[i] = None  # Mark as intentionally done
                    else:
                        logger.warning(f"❌ Agent {agent_name} terminated unexpectedly. Restarting...")
                        processes[i] = start_agent(agent_name)

            report_orchestrator_health()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down all agents...")
        for proc in processes:
            if proc:
                proc.terminate()

if __name__ == "__main__":
    main()
