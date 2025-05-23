import os
import redis
import time
import logging
import ast
import random  # (simulates ML output; replace with real model later)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def get_redis_connection():
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url)
    else:
        raise Exception("REDIS_URL not found in environment variables.")

# Dummy ML function (replace with real ML model later)
def dummy_ml_predict(job_data):
    # Simulate a prediction
    pred = random.choice(["buy", "hold", "sell"])
    prob = round(random.uniform(0.7, 0.99), 3)
    return {"prediction": pred, "confidence": prob}

def worker_loop():
    r = get_redis_connection()
    logging.info("ML Agent Worker is running and connected to Redis...")
    while True:
        try:
            job = r.brpop("quanta_jobs", timeout=10)
            if job:
                job_data = ast.literal_eval(job[1].decode("utf-8"))
                logging.info(f"[ML AGENT] Got job: {job_data}")
                # Step 1: Run ML prediction
                ml_result = dummy_ml_predict(job_data)
                logging.info(f"[ML AGENT] ML Prediction: {ml_result}")
                # Step 2: Simulate job completion
                time.sleep(2)
                logging.info(f"[ML AGENT] Processed job: {job_data['id']}")
            else:
                logging.info("[ML AGENT] No jobs in queue, waiting...")
        except Exception as e:
            logging.error(f"[ML AGENT] Error processing job: {e}")
            time.sleep(2)

if __name__ == "__main__":
    worker_loop()
