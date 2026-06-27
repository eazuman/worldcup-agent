from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
_agent = None  # compiled LangGraph agent, built lazily (needs GOOGLE_API_KEY)

app = FastAPI(title="GoldenGoal RAG API", version="0.1.0")

# Allowed browser origins for the API. Defaults cover local dev; in production
# set FRONTEND_ORIGINS (comma-separated). Any Cloudflare Pages / Vercel / HF
# Spaces deploy is also allowed via regex so previews work without reconfiguring.
_DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("FRONTEND_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.(pages\.dev|workers\.dev|vercel\.app|hf\.space)",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _ensure_index() -> None:
    """Rebuild the RAG index from the committed corpus on first boot.

    The Chroma index is gitignored and rebuilt on deploy, so a fresh container
    starts with an empty store — ingest the corpus once so RAG works immediately.
    """
    if vector_store.count() == 0:
        ingest_corpus(vector_store)


def _build_llm():
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:  # pragma: no cover - dependency missing
        raise HTTPException(
            status_code=500,
            detail="langchain-google-genai is not installed.",
        ) from exc
    return ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        llm = _build_llm()
        _rag_service = RAGService(vector_store=vector_store, llm=llm)
    return _rag_service


async def get_agent():
    """Lazily build the compiled coach agent (needs GOOGLE_API_KEY).

    Async because it loads the MCP football tools over stdio adapters.
    """
    global _agent
    if _agent is None:
        from app.agent import build_agent_async

        _agent = await build_agent_async(vector_store=vector_store, llm=_build_llm())
    return _agent


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AgentChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    thread_id: str = Field(default="default")


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


def _sse(payload: dict) -> str:
    """Format a Server-Sent Events data frame."""
    return f"data: {json.dumps(payload)}\n\n"


def _chunk_text(chunk) -> str:
    """Extract plain text from an AIMessageChunk (content may be str or parts)."""
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(part.get("text", "") or "")
        return "".join(parts)
    return ""


@app.post("/agent/chat")
async def agent_chat(payload: AgentChatRequest) -> StreamingResponse:
    """Stream the coach agent's response token-by-token over Server-Sent Events.

    Emits JSON frames: {type: "token", content}, {type: "tool_start"|"tool_end",
    name}, {type: "done"}, or {type: "error", detail}.
    """
    agent = await get_agent()
    config = {"configurable": {"thread_id": payload.thread_id}}
    inputs = {"messages": [{"role": "user", "content": payload.question}]}

    async def event_stream():
        try:
            async for event in agent.astream_events(inputs, config=config, version="v2"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    text = _chunk_text(event["data"]["chunk"])
                    if text:
                        yield _sse({"type": "token", "content": text})
                elif kind == "on_tool_start":
                    yield _sse({"type": "tool_start", "name": event.get("name", "")})
                elif kind == "on_tool_end":
                    yield _sse({"type": "tool_end", "name": event.get("name", "")})
            yield _sse({"type": "done"})
        except Exception as exc:  # noqa: BLE001 - surface a clean error frame
            yield _sse({"type": "error", "detail": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health() -> dict:
    """Return basic service health and the number of indexed chunks."""
    return {"status": "ok", "chunks_indexed": vector_store.count()}


@app.get("/standings")
async def standings() -> dict:
    """Structured World Cup group standings for the Standings view.

    Returns {source: "live"|"sample", groups: [...]}. On any API error it
    degrades to sample so the frontend can fall back to its built-in data.
    """
    from app.football import get_standings_data

    try:
        return get_standings_data()
    except Exception as exc:  # noqa: BLE001 - degrade to sample on any error
        return {"source": "sample", "groups": [], "error": str(exc)[:160]}


@app.get("/schedule")
async def schedule() -> dict:
    """Structured World Cup fixtures for the Schedule view.

    Returns {source: "live"|"sample", fixtures: [...]}. On any API error it
    degrades to sample so the frontend can fall back to its built-in data.
    """
    from app.football import get_schedule_data

    try:
        return get_schedule_data()
    except Exception as exc:  # noqa: BLE001 - degrade to sample on any error
        return {"source": "sample", "fixtures": [], "error": str(exc)[:160]}


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
