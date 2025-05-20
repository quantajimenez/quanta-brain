# quanta/mesh/config_hot_reload.py

import json
import os

class MeshConfigLoader:
    def __init__(self, config_path=None):
        # Default config path inside quanta/mesh/agent_config.json
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "agent_config.json")

    def load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            return json.load(f)
    
    def save_config(self, config_dict):
        with open(self.config_path, "w") as f:
            json.dump(config_dict, f, indent=2)
