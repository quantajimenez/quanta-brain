import os
import redis
import time
import logging
import ast

# Configure robust logging
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

def worker_loop():
    r = get_redis_connection()
    logging.info("ML Agent Worker is running and connected to Redis...")
    while True:
        try:
            job = r.brpop("quanta_jobs", timeout=10)
            if job:
                job_data = ast.literal_eval(job[1].decode("utf-8"))
                logging.info(f"[ML AGENT] Got job: {job_data}")
                # Simulate processing time
                time.sleep(3)
                # Add a log to show job completion
                logging.info(f"[ML AGENT] Processed job: {job_data['id']}")
            else:
                logging.info("[ML AGENT] No jobs in queue, waiting...")
        except Exception as e:
            logging.error(f"[ML AGENT] Error processing job: {e}")
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()
