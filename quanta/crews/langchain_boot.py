import os
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from quanta.utils.logger import setup_logger

logger = setup_logger("langchain_boot")

def boot_langchain_memory():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        logger.error("No OPENAI_API_KEY found.")
        raise Exception("Missing OpenAI API key.")

    # Use the updated OpenAI and OpenAIEmbeddings
    llm = OpenAI(openai_api_key=openai_key, model="gpt-4-1106-preview")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)

    # FAISS now requires at least one document to initialize
    vectorstore = FAISS.from_documents(
        [Document(page_content="init")],
        embedding=embeddings
    )

    logger.info("LangChain memory store (FAISS) booted.")
    return llm, embeddings, vectorstore

if __name__ == "__main__":
    boot_langchain_memory()
