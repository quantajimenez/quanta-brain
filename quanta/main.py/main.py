from brain import brain
from memory import memory
from voice import voice
from execution import execution
from clock import clock
from data import data_manager
from agents import agent_manager
from config import config
from utils import utils

def start_quanta():
    brain.init()
    memory.init()
    voice.init()
    execution.init()
    clock.init()
    data_manager.init()
    agent_manager.init()
    config.init()
    utils.init()
    print("✅ Quanta Brain Started Successfully!")

if __name__ == "__main__":
    start_quanta()
