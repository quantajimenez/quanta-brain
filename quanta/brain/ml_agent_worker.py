import os
import time
import redis
import json
import boto3
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
HIST_BUCKET = os.getenv("S3_HIST_BUCKET", "quanta-historical-marketdata")
REDIS_URL = os.getenv("REDIS_URL")

from quanta.ingest.polygon_data_loader import load_bars

def upload_insight_to_s3(result_dict, ticker, date):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=AWS_REGION,
        )
        s3_key = f"insights/{ticker}_{date}_merged.json"
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=json.dumps(result_dict))
        # (Optional) Also upload per-model files
        for model_name, model_data in result_dict['models'].items():
            indiv_key = f"insights/{ticker}_{date}_{model_name}_v{model_data['version']}.json"
            model_record = {
                "id": result_dict["id"],
                "timestamp": result_dict["timestamp"],
                "raw_job": result_dict["raw_job"],
                "features": result_dict["features"],
                "model": model_name,
                **model_data
            }
            s3.put_object(Bucket=S3_BUCKET, Key=indiv_key, Body=json.dumps(model_record))
        logging.info(f"[ML AGENT] Uploaded merged and per-model insights to S3 for {ticker} {date}")
    except Exception as e:
        logging.error(f"[ML AGENT][ERROR] Failed to upload insight(s) to S3: {e}")

def multi_model_predict(features):
    X, y = make_classification(n_samples=100, n_features=4, n_classes=2, random_state=42)
    results = {}

    # Random Forest
    rf = RandomForestClassifier()
    rf.fit(X, y)
    rf_pred = int(rf.predict([features])[0])
    rf_proba = rf.predict_proba([features])[0].tolist()
    results['RandomForest'] = {'prediction': rf_pred, 'probabilities': rf_proba, 'version': '1.0'}

    # Logistic Regression
    lr = LogisticRegression()
    lr.fit(X, y)
    lr_pred = int(lr.predict([features])[0])
    lr_proba = lr.predict_proba([features])[0].tolist()
    results['LogisticRegression'] = {'prediction': lr_pred, 'probabilities': lr_proba, 'version': '1.0'}

    # Gradient Boosting
    gb = GradientBoostingClassifier()
    gb.fit(X, y)
    gb_pred = int(gb.predict([features])[0])
    gb_proba = gb.predict_proba([features])[0].tolist()
    results['GradientBoosting'] = {'prediction': gb_pred, 'probabilities': gb_proba, 'version': '1.0'}

    return results

def main():
    r = redis.from_url(REDIS_URL)
    logging.info("[ML AGENT] Worker is running and connected to Redis...")
    while True:
        job = r.brpop("quanta_jobs", timeout=5)
        if job:
            try:
                logging.info(f"[ML AGENT][DEBUG] Raw job from Redis: {job}")
                job_data = json.loads(job[1])
                logging.info(f"[ML AGENT][DEBUG] Decoded job_data: {job_data}")

                ticker = job_data.get("ticker")
                date = job_data.get("date")
                if ticker is None or date is None:
                    logging.error(f"[ML AGENT][ERROR] Missing ticker or date in job_data: {job_data}")
                    continue

                bars = load_bars(ticker, date)
                logging.info(f"[ML AGENT] Loaded bars: {bars[:3]} (total: {len(bars)})")
                if not bars or len(bars) < 4:
                    logging.warning("[ML AGENT] Not enough data for features.")
                    continue

                first_bar = bars[0]
                features = [
                    first_bar.get("open", 0),
                    first_bar.get("high", 0),
                    first_bar.get("low", 0),
                    first_bar.get("close", 0)
                ]

                model_results = multi_model_predict(features)
                result_dict = {
                    "id": job_data.get("id"),
                    "timestamp": time.time(),
                    "raw_job": job_data,
                    "features": features,
                    "models": model_results
                }

                upload_insight_to_s3(result_dict, ticker, date)
                logging.info(f"[ML AGENT] Processed job: {job_data.get('id')}")

            except Exception as e:
                logging.error(f"[ML AGENT][ERROR] Failed to process job: {e}")

if __name__ == "__main__":
    main()
