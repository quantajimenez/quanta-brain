# quanta/brain/ml_snapshot_log.py

def log_ml_snapshot(model_name, metric, value, status="EVALUATED"):
    print(f"[ML SNAPSHOT] Model: {model_name} | Metric: {metric} | Value: {value} | Status: {status}")
