import os
import redis
import time
import uuid
import logging

# Configure robust logging with timestamp and log level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def get_redis_connection():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url)
    else:
        raise Exception("REDIS_URL not found in environment variables.")

def main():
    r = get_redis_connection()
    logging.info("Job Producer is running and connected to Redis...")
    while True:
        job = {"id": str(uuid.uuid4()), "task": "analyze_data"}
        try:
            r.lpush("quanta_jobs", str(job))
            queue_len = r.llen("quanta_jobs")
            logging.info(f"[PRODUCER] Pushed job: {job} | Queue length: {queue_len}")
        except Exception as e:
            logging.error(f"[PRODUCER] Error pushing job: {job} | {e}")
        time.sleep(5)  # Every 5 seconds, push a job (adjust as needed)

if __name__ == "__main__":
    main()
