import os
import redis
import time

def get_redis_connection():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url)
    else:
        raise Exception("REDIS_URL not found in environment variables.")

def worker_loop():
    r = get_redis_connection()
    print("ML Agent Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            print(f"Processing job: {job[1].decode()}")
            # Simulate work (replace with real ML logic later)
            time.sleep(2)
        else:
            print("No job found, waiting...")

if __name__ == "__main__":
    worker_loop()
