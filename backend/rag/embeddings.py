from __future__ import annotations

from langchain_huggingface import HuggingFaceEmbeddings

# Local sentence-transformers model — 384 dims, runs on-device, no API key and no
# per-call cost. 
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings(model_name: str = DEFAULT_EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    """Return the local MiniLM embedding function used by the vector store."""
    return HuggingFaceEmbeddings(model_name=model_name)
