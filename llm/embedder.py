from langchain_huggingface.embeddings import HuggingFaceEmbeddings

embedding_function = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True}
)
