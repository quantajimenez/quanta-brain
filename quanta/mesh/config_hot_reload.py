# quanta/mesh/config_hot_reload.py

import os
import json
import boto3
import redis

class MeshConfigLoader:
    def __init__(self, config_key=None):
        self.s3_bucket = os.getenv("QUANTA_CONFIG_S3_BUCKET", "quanta-mesh-config")
        self.s3_key = config_key or os.getenv("QUANTA_CONFIG_S3_KEY", "agent_config.json")
        self.s3 = boto3.client("s3")
        self.redis_url = os.getenv("QUANTA_CONFIG_REDIS_URL", "redis://localhost:6379")
        self.redis = redis.Redis.from_url(self.redis_url)

    def load_config(self):
        # Prefer Redis, fall back to S3
        config = self.redis.get("mesh_config")
        if config:
            return json.loads(config)
        try:
            obj = self.s3.get_object(Bucket=self.s3_bucket, Key=self.s3_key)
            config = json.loads(obj["Body"].read())
            self.redis.set("mesh_config", json.dumps(config))
            return config
        except Exception:
            return {}

    def save_config(self, config_dict):
        self.redis.set("mesh_config", json.dumps(config_dict))
        self.s3.put_object(Bucket=self.s3_bucket, Key=self.s3_key, Body=json.dumps(config_dict, indent=2))
