from quanta.crews.crew_init import crew_boot
from quanta.crews.langchain_boot import boot_langchain_memory
from quanta.utils.logger import setup_logger

logger = setup_logger("integration_test")

def run_sample_workflow():
    logger.info("Booting Crew agents...")
    agents = crew_boot()
    logger.info("Booting LangChain memory (FAISS)...")
    llm, embeddings, vectorstore = boot_langchain_memory()

    # Step 1: Strategist generates a mock trade idea
    trade_idea = "Buy AAPL at market open"
    logger.info(f"Strategist generated trade idea: {trade_idea}")
    result1 = agents['strategist'].run_task(trade_idea)
    logger.info(f"StrategistAgent result: {result1}")

    # Step 2: Ingestor 'fetches' the idea and stores in memory
    logger.info("Ingestor storing idea in vectorstore (simulated)...")
    try:
        vectorstore.add_texts([trade_idea])
        logger.info("IngestorAgent stored trade idea in vectorstore.")
    except Exception as e:
        logger.error(f"Failed to store in vectorstore: {e}")
    result2 = agents['ingestor'].run_task(trade_idea)
    logger.info(f"IngestorAgent result: {result2}")

    # Step 3: Executor 'executes' the idea
    logger.info("Executor executing trade idea (simulated)...")
    result3 = agents['executor'].run_task(trade_idea)
    logger.info(f"ExecutorAgent result: {result3}")

if __name__ == "__main__":
    run_sample_workflow()
