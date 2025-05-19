import os
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from quanta.utils.logger import setup_logger

logger = setup_logger("langchain_boot")

def boot_langchain_memory():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        logger.error("No OPENAI_API_KEY found.")
        raise Exception("Missing OpenAI API key.")
    llm = OpenAI(openai_api_key=openai_key, model="gpt-4-1106-preview")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
    vectorstore = FAISS(embedding_function=embeddings)
    logger.info("LangChain memory store (FAISS) booted.")
    return llm, embeddings, vectorstore

if __name__ == "__main__":
    boot_langchain_memory()
