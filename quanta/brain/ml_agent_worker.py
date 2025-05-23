import os
import redis
import time

def worker_loop():
    REDIS_URL = os.getenv("REDIS_URL")
    r = redis.from_url(REDIS_URL)
    print("ML Agent Worker is running and connected to Redis...")

    while True:
        job = r.brpop("quanta_jobs", timeout=10)
        if job:
            _, job_data = job
            print(f"[ML AGENT] Got job: {job_data}")
            # Dummy ML step (replace with real ML logic)
            result = f"Processed: {job_data.decode()}"
            r.lpush("quanta_results", result)
        else:
            print("[ML AGENT] No job found, waiting...")

if __name__ == "__main__":
    worker_loop()
