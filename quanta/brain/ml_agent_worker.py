import os
import redis
import time

def connect_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        username=os.getenv("REDIS_USERNAME"),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=True,
        decode_responses=True  # So you don't get b'strings'
    )

def worker_loop():
    r = connect_redis()
    print("ML Agent Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=10)
        if job:
            _, job_data = job
            print(f"[Worker] Picked up job: {job_data}")
            # --- Dummy ML logic; replace with real model inference ---
            result = f"ML processed: {job_data}"
            r.lpush("quanta_results", result)
            print(f"[Worker] Job complete, result pushed to quanta_results.")
        else:
            print("[Worker] No jobs found, waiting...")

if __name__ == "__main__":
    worker_loop()
