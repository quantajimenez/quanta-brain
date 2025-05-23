import os
import redis
import time
import uuid

def get_redis_connection():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url)
    else:
        raise Exception("REDIS_URL not found in environment variables.")

def main():
    r = get_redis_connection()
    print("Job Producer is running and connected to Redis...")
    while True:
        job = {"id": str(uuid.uuid4()), "task": "analyze_data"}
        r.lpush("quanta_jobs", str(job))
        print(f"Pushed job: {job}")
        time.sleep(5)  # Every 5 seconds, push a job (adjust as needed)

if __name__ == "__main__":
    main()
