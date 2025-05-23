import os
import redis
import time

def main():
    REDIS_URL = os.getenv("REDIS_URL")
    r = redis.from_url(REDIS_URL)
    print("Job Producer is running and connected to Redis...")

    job_id = 0
    while True:
        job = {"job_id": job_id, "payload": f"task-{job_id}"}
        r.lpush("quanta_jobs", str(job))
        print(f"[PRODUCER] Pushed job: {job}")
        job_id += 1
        time.sleep(5)

if __name__ == "__main__":
    main()
