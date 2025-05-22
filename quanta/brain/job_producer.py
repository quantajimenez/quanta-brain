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

def produce_jobs():
    for i in range(10):
        job = f"ML_JOB_{i}"
        r.lpush("quanta_jobs", job)
        print(f"Produced job: {job}")
        time.sleep(1)  # Simulate staggered jobs

if __name__ == "__main__":
    produce_jobs()
