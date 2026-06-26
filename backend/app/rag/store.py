from __future__ import annotations

from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class CorpusVectorStore:
    """Persistent Chroma store (via LangChain) for the World Cup RAG corpus.

    Adapted from the POC's ``SingleDocVectorStore``. The POC kept exactly one
    active document and reset on every ingest; here the store holds a whole
    **corpus** of committed ``.txt`` files, so callers add many documents and
    call :meth:`reset` only when rebuilding the index from scratch.
    """

    def __init__(
        self,
        path: str,
        embeddings: Embeddings,
        collection_name: str = "worldcup_corpus",
    ) -> None:
        self._path = path
        self._embeddings = embeddings
        self._collection_name = collection_name
        self._store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=path,
        )

    def reset(self) -> None:
        # Drop all indexed content — used when rebuilding the index from the corpus.
        self._store.reset_collection()

    def add_documents(self, documents: list[Document], ids: list[str]) -> None:
        self._store.add_documents(documents=documents, ids=ids)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if self.count() == 0:
            return []

        results = self._store.similarity_search_with_relevance_scores(query, k=top_k)

        hits: list[dict[str, Any]] = []
        for document, score in results:
            metadata = dict(document.metadata or {})
            hits.append(
                {
                    "chunk_id": metadata.get("chunk_id", ""),
                    "text": document.page_content,
                    "score": round(float(score), 4),
                    "metadata": metadata,
                }
            )
        return hits

    def peek(self, limit: int = 10, include_embeddings: bool = False) -> list[dict[str, Any]]:
        if self.count() == 0:
            return []

        include = ["documents", "metadatas"]
        if include_embeddings:
            include.append("embeddings")

        # Drop to the underlying Chroma collection: LangChain's high-level API
        # does not expose raw stored embeddings, which /debug/chunks needs.
        result = self._collection.get(limit=limit, include=include)

        ids = result.get("ids") or []
        documents = result.get("documents")
        metadatas = result.get("metadatas")
        embeddings = result.get("embeddings")

        documents = documents if documents is not None else []
        metadatas = metadatas if metadatas is not None else []
        embeddings = embeddings if embeddings is not None else []

        items: list[dict[str, Any]] = []
        for idx, chunk_id in enumerate(ids):
            item: dict[str, Any] = {
                "chunk_id": chunk_id,
                "text": documents[idx] if idx < len(documents) else "",
                "metadata": metadatas[idx] if idx < len(metadatas) else {},
            }
            if include_embeddings and idx < len(embeddings):
                vector = list(embeddings[idx])
                item["embedding_dim"] = len(vector)
                item["embedding"] = vector
            items.append(item)

        return items

    def count(self) -> int:
        return self._collection.count()

    @property
    def _collection(self) -> Any:
        # Private Chroma collection handle (acceptable for a POC).
        return self._store._collection
