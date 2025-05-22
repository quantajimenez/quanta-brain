"""
Model Store: Handles saving, loading, and versioning of ML models.
"""
import os
import pickle
from datetime import datetime

def store_model_version(model, meta=None):
    """
    Store model and associated metadata with versioning.
    """
    dir_path = "model_versions"
    os.makedirs(dir_path, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(dir_path, f"model_{timestamp}.pkl")
    with open(path, "wb") as f:
        pickle.dump({"model": model, "meta": meta}, f)
    print(f"[MODEL STORE] Stored model version at {path}")
