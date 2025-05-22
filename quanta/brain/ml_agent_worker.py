import redis
import os
import time

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    ssl=True
)

def worker_loop():
    while True:
        job = r.brpop("quanta_jobs", timeout=10)
        if job:
            job_name = job[1].decode()
            print(f"[Worker] Processing job: {job_name}")
            # Insert real ML task or placeholder here
            time.sleep(2)
        else:
            print("[Worker] No jobs in queue. Waiting...")

if __name__ == "__main__":
    worker_loop()
