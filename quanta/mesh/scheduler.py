# quanta/mesh/scheduler.py

import time
import threading
import redis
from quanta.utils.logger import setup_logger

class MeshScheduler:
    def __init__(self, redis_url="rediss://default:AVe0AAIjcDFiNjY1Mjc1NDIwNDE0YjdkOWJhMjdmOWEzMzMzMzBiOXAxMA@driven-pangolin-22452.upstash.io:6379"):
        self.logger = setup_logger("MeshScheduler")
        self.redis = redis.Redis.from_url(redis_url)
        self.keep_running = True

    def schedule_loop(self):
        self.logger.info("MeshScheduler started. Waiting for events...")
        while self.keep_running:
            # Check Redis queue for new events (simple blocking pop)
            event = self.redis.lpop("quanta:events")
            if event:
                self.logger.info(f"Received event: {event.decode()}")
                # TODO: Dispatch to mesh orchestrator here
            time.sleep(1)  # Check every second

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
