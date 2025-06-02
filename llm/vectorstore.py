import os
from langchain_chroma import Chroma
from .embedder import embedding_function

vectorstore = None
retriever = None
COLLECTION_NAME = "my_rag_collection"
PERSIST_DIR = "./chroma_store"


def build_vectorstore():
    global vectorstore, retriever
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        try:
            vectorstore = Chroma(
                persist_directory=PERSIST_DIR,
                collection_name=COLLECTION_NAME,
                embedding_function=embedding_function
            )
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            return " Loaded existing vectorstore."
        except Exception as e:
            return f" Failed to load vectorstore: {str(e)}"
    else:
        return " No persisted vectorstore found. Please upload files first."
