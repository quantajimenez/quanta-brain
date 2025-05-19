from quanta.utils.logger import setup_logger

class StrategistAgent:
    def __init__(self):
        self.logger = setup_logger("StrategistAgent")

    def ping(self):
        self.logger.info("StrategistAgent ping successful.")
        return True

    def run_task(self, task):
        self.logger.info(f"Strategist running task: {task}")
        # Placeholder for real logic
        return f"Strategist ran {task}"
