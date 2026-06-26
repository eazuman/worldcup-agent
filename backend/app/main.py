from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.rag.embeddings import get_embeddings
from app.rag.ingest import index_text, ingest_corpus
from app.rag.service import RAGService
from app.rag.store import CorpusVectorStore

load_dotenv()

TOP_K = 3
LLM_MODEL = "gemini-2.5-flash"

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR.parent / "data" / "chroma_db"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Embeddings + store need no API key, so they initialise eagerly. The Gemini LLM
# needs GOOGLE_API_KEY, so the RAG service is built lazily on first /ask — that
# lets /health and /ingest work in a fresh checkout without a key configured.
embeddings = get_embeddings()
vector_store = CorpusVectorStore(path=str(CHROMA_DIR), embeddings=embeddings)
_rag_service: RAGService | None = None

app = FastAPI(title="GoldenGoal RAG API", version="0.1.0")


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise HTTPException(
                status_code=500,
                detail="langchain-google-genai is not installed.",
            ) from exc
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
        _rag_service = RAGService(vector_store=vector_store, llm=llm)
    return _rag_service


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    """Chunk, embed, and add a single .txt file to the corpus index."""
    filename = file.filename or "uploaded.txt"
    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded text",
        ) from exc

    chunks = index_text(vector_store, filename=filename, text=text)
    if chunks == 0:
        raise HTTPException(status_code=400, detail="No text content found to index")

    return {
        "status": "success",
        "source_file": filename,
        "chunks_created": chunks,
        "characters_processed": len(text),
    }


@app.post("/ingest/corpus")
async def ingest_corpus_endpoint() -> dict:
    """Rebuild the index from every .txt file committed under data/corpus."""
    return ingest_corpus(vector_store)


@app.post("/ask")
async def ask(payload: AskRequest) -> dict:
    """Answer a question using top-K retrieved chunks from the indexed corpus."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question cannot be empty")

    rag_service = get_rag_service()
    try:
        return rag_service.answer_question(question=question, top_k=TOP_K)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(
            status_code=502,
            detail=f"Failed to answer question via Gemini: {exc}",
        ) from exc


@app.get("/health")
async def health() -> dict:
    """Return basic service health and the number of indexed chunks."""
    return {"status": "ok", "chunks_indexed": vector_store.count()}


@app.get("/debug/chunks")
async def debug_chunks(
    limit: int = 10,
    snippet_length: int = 200,
    include_embeddings: bool = False,
    embedding_preview: int = 8,
) -> dict:
    """Inspect stored chunks (and optionally embeddings) for debugging."""
    items = vector_store.peek(limit=limit, include_embeddings=include_embeddings)
    for item in items:
        text = item.get("text") or ""
        if snippet_length > 0 and len(text) > snippet_length:
            item["text"] = text[:snippet_length] + "..."

        if include_embeddings and "embedding" in item and embedding_preview > 0:
            vector = item["embedding"]
            if len(vector) > embedding_preview:
                item["embedding"] = vector[:embedding_preview]
                item["embedding_truncated"] = True
    return {"chunks_indexed": vector_store.count(), "returned": len(items), "chunks": items}


@app.delete("/reset")
async def reset() -> dict:
    """Clear the vector store, removing all indexed chunks."""
    vector_store.reset()
    return {"status": "success", "message": "Vector store reset"}
