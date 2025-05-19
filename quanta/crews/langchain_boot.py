from langchain.vectorstores import FAISS
from langchain_core.documents import Document

def boot_langchain_memory():
    # ... your OpenAI key and embeddings code ...

    # Initialize FAISS with a dummy document (required for the API)
    vectorstore = FAISS.from_documents(
        [Document(page_content="init")],
        embedding=embeddings
    )
    logger.info("LangChain memory store (FAISS) booted.")
    return llm, embeddings, vectorstore
