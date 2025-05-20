# quanta/mesh/scheduler.py

import time
import threading
import redis
from quanta.utils.logger import setup_logger
from quanta.mesh.orchestrator import AgentMeshOrchestrator

class MeshScheduler:
    def __init__(self, redis_url="rediss://default:AVe0AAIjcDFiNjY1Mjc1NDIwNDE0YjdkOWJhMjdmOWEzMzMzMzBiOXAxMA@driven-pangolin-22452.upstash.io:6379"):
        self.logger = setup_logger("MeshScheduler")
        self.redis = redis.Redis.from_url(redis_url)
        self.keep_running = True
        self.orchestrator = AgentMeshOrchestrator()  # Attach orchestrator

    def schedule_loop(self):
        self.logger.info("MeshScheduler started. Waiting for events...")
        while self.keep_running:
            event = self.redis.lpop("quanta:events")
            if event:
                event_data = event.decode()
                self.logger.info(f"Received event: {event_data}")
                # Event type: restart:<agent_name>
                if event_data.startswith("restart:"):
                    agent_name = event_data.split(":")[1]
                    try:
                        self.orchestrator.restart_agent(agent_name)
                        self.logger.info(f"Restarted agent: {agent_name}")
                    except Exception as e:
                        self.logger.error(f"Error restarting agent {agent_name}: {e}")
                else:
                    self.logger.info(f"No handler for event: {event_data}")
            time.sleep(1)

    def add_event(self, event_data):
        self.redis.rpush("quanta:events", event_data)
        self.logger.info(f"Added event to queue: {event_data}")

    def stop(self):
        self.keep_running = False

if __name__ == "__main__":
    scheduler = MeshScheduler()
    loop_thread = threading.Thread(target=scheduler.schedule_loop)
    loop_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        loop_thread.join()
