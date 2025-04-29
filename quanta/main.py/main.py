# main.py
from brain import brain
from memory import memory
from voice import voice
from execution import execution
from clock import clock
from data import data_manager
from agents import agent_manager
from config import config
from tests import test_runner
from utils import utils
from webhook import app  # ✅ Import the real webhook app
from wasabi_connector import wasabi_init  # 🆕 NEW LINE (import wasabi connection)

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
    wasabi_init()  # 🆕 NEW LINE (initialize wasabi connection)

def start_webhook():
    app.run(host="0.0.0.0", port=10000)  # ✅ Matching port 10000

if __name__ == "__main__":
    threading.Thread(target=start_brain).start()
    threading.Thread(target=start_webhook).start()
