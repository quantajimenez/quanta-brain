# quanta/main.py

from quanta.brain import brain
from quanta.memory import memory
from quanta.voice import voice
from quanta.execution import execution
from quanta.clock import clock
from quanta.data import data_manager
from quanta.agents import agent_manager
from quanta.config import config
from quanta.tests import test_runner
from quanta.utils import utils

# Import the new webhook app and resilience poller
from quanta.ingest.webhook_listener import app as ingest_app
from quanta.ingest.resilience import start_poller

import threading

def start_brain():
    brain.init()
    memory.init()
    voice.init()
    execution.init()
    clock.init()
    data_manager.init()
    agent_manager.init()
    config.init()
    test_runner.init()
    utils.init()

def start_ingest_webhook():
    # If FastAPI: use uvicorn to serve the app
    import uvicorn
    uvicorn.run("quanta.ingest.webhook_listener:app", host="0.0.0.0", port=10000, reload=False)

if __name__ == "__main__":
    threading.Thread(target=start_brain).start()
    threading.Thread(target=start_poller).start()
    threading.Thread(target=start_ingest_webhook).start()
    # Add other agents/threads as needed
