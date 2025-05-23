import os
import redis
import time

def get_redis_connection():
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url, ssl=True, decode_responses=True)
    else:
        return redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=True,
            decode_responses=True,
        )

def worker_loop():
    r = get_redis_connection()
    print("ML Agent Worker is running and connected to Redis...")

    while True:
        job = r.brpop("quanta_jobs", timeout=10)
        if job:
            queue, data = job
            print(f"Processing job: {data}")
            # Placeholder: Insert ML logic here
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()
