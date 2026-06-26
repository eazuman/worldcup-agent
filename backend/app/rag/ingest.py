from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.store import CorpusVectorStore

# Chunking parameters carried over from the rag-poc-langchain POC.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

BASE_DIR = Path(__file__).resolve().parents[3]
CORPUS_DIR = BASE_DIR / "data" / "corpus"


def make_doc_id(filename: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    safe_name = Path(filename).name.replace(" ", "_")
    return f"{safe_name}-{digest}"


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)


def index_text(
    store: CorpusVectorStore,
    *,
    filename: str,
    text: str,
) -> int:
    """Chunk and add a single document's text to the store. Returns chunk count."""
    chunks = chunk_text(text)
    if not chunks:
        return 0

    doc_id = make_doc_id(filename=filename, text=text)
    ids = [f"{doc_id}-{idx}" for idx in range(len(chunks))]
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "chunk_id": ids[idx],
                "doc_id": doc_id,
                "chunk_index": idx,
                "source_file": filename,
            },
        )
        for idx, chunk in enumerate(chunks)
    ]
    store.add_documents(documents=documents, ids=ids)
    return len(chunks)


def ingest_corpus(store: CorpusVectorStore, corpus_dir: Path = CORPUS_DIR) -> dict:
    """Rebuild the index from every ``.txt`` file in the committed corpus directory.

    The index is dropped first so a deploy can rebuild it deterministically from git.
    """
    files = sorted(corpus_dir.glob("*.txt"))
    if not files:
        return {"status": "empty", "files": 0, "chunks": 0, "corpus_dir": str(corpus_dir)}

    store.reset()
    total_chunks = 0
    indexed: list[dict] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        chunks = index_text(store, filename=path.name, text=text)
        total_chunks += chunks
        indexed.append({"file": path.name, "chunks": chunks})

    return {
        "status": "success",
        "files": len(files),
        "chunks": total_chunks,
        "indexed": indexed,
        "corpus_dir": str(corpus_dir),
    }


if __name__ == "__main__":
    from app.rag.embeddings import get_embeddings

    chroma_dir = BASE_DIR / "data" / "chroma_db"
    chroma_dir.mkdir(parents=True, exist_ok=True)
    vector_store = CorpusVectorStore(path=str(chroma_dir), embeddings=get_embeddings())
    result = ingest_corpus(vector_store)
    print(result)
