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

def main():
    r = get_redis_connection()
    print("Job Producer is running and connected to Redis...")

    # Dummy: Add jobs for 10 agents
    for i in range(10):
        job = {"agent_id": i, "task": "run_ml"}
        r.lpush("quanta_jobs", str(job))
        print(f"Pushed job for agent {i}")
        time.sleep(1)

if __name__ == "__main__":
    main()
