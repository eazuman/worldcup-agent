"""High-priority unit tests for the RAG layer (no embeddings / no network).

The chunking and id helpers are pure. ``RAGService`` is exercised with a tiny
stub store and a fake chat model so no Chroma index or Gemini key is needed.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from rag.ingest import chunk_text, ingest_corpus, make_doc_id
from rag.service import RAGService


def test_chunk_text_splits_long_text():
    chunks = chunk_text("word " * 600)
    assert len(chunks) > 1
    assert all(isinstance(c, str) and c for c in chunks)


def test_make_doc_id_is_stable_and_filename_safe():
    a = make_doc_id("My File.txt", "hello world")
    b = make_doc_id("My File.txt", "hello world")
    assert a == b
    assert " " not in a
    assert a.startswith("My_File.txt-")
    # Different content yields a different id.
    assert make_doc_id("My File.txt", "different") != a


def test_ingest_corpus_empty_dir(tmp_path: Path):
    result = ingest_corpus(store=None, corpus_dir=tmp_path)
    assert result["status"] == "empty"
    assert result["files"] == 0
    assert result["chunks"] == 0


class _StubStore:
    """Minimal stand-in for CorpusVectorStore used by RAGService tests."""

    def __init__(self, hits):
        self._hits = hits

    def count(self):
        return len(self._hits)

    def search(self, query, top_k=3):
        return self._hits[:top_k]


def test_rag_service_returns_message_when_index_empty():
    service = RAGService(vector_store=_StubStore([]), llm=FakeListChatModel(responses=["x"]))
    result = service.answer_question("Who won in 1930?")
    assert result["sources"] == []
    assert "index" in result["answer"].lower() or "corpus" in result["answer"].lower()


def test_rag_service_answers_from_context():
    hits = [{"text": "Uruguay won the first World Cup in 1930.", "metadata": {}, "score": 0.9}]
    llm = FakeListChatModel(responses=["Uruguay won the 1930 World Cup."])
    service = RAGService(vector_store=_StubStore(hits), llm=llm)
    result = service.answer_question("Who won the first World Cup?")
    assert result["answer"] == "Uruguay won the 1930 World Cup."
    assert result["sources"] == hits
