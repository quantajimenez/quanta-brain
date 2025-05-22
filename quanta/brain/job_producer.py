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
        decode_responses=True
    )

def produce_jobs():
    r = connect_redis()
    print("Job Producer is running and connected to Redis...")
    job_id = 1
    while True:
        job_data = f"Job-{job_id} | payload: test-data"
        r.lpush("quanta_jobs", job_data)
        print(f"[Producer] Pushed job: {job_data}")
        job_id += 1
        time.sleep(5)  # Produce a new job every 5 seconds (adjust as needed)

if __name__ == "__main__":
    produce_jobs()
