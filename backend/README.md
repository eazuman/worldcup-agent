# Backend (Phases 2–6)

FastAPI + RAG + the agent layer.

**Phase 3 (RAG) is now scaffolded** — the RAG layer under `app/rag/` is **copied/adapted from the
`rag-poc-langchain` teaching POC** and re-pointed at the World Cup free-tier stack:

- **Embeddings:** local `all-MiniLM-L6-v2` (HuggingFace) — no API key, no per-call cost
  (POC used OpenAI `text-embedding-3-small`).
- **LLM:** Google Gemini `gemini-2.5-flash` (POC used OpenAI `gpt-4o-mini`).
- **Indexing:** a multi-file **corpus** under `data/corpus/*.txt` (POC indexed a single document).
- **Vector store:** Chroma (persistent, local) — unchanged from the POC.

## Current structure

```
backend/
  app/
    __init__.py
    main.py            # FastAPI: /ask, /ingest, /ingest/corpus, /health, /debug/chunks, /reset
    rag/
      __init__.py
      embeddings.py    # local MiniLM (langchain-huggingface)
      store.py         # Chroma persistent client (CorpusVectorStore)
      service.py       # RAGService — retrieve + grounded Gemini answer (LCEL chain)
      ingest.py        # chunk + (re)build the index from data/corpus
      sources.py       # pluggable corpus sources (Wikipedia now; S3/files later)
  scripts/
    build_corpus.py    # fetch curated Wikipedia pages -> data/corpus/*.txt
  pyproject.toml       # project + dependencies (uv)
  uv.lock              # pinned, reproducible lockfile (uv)
```

> Still **planned** (later phases): `app/agent.py` (Phase 5 agent loop) and `app/tools/` (Phase 4 MCP
> client + football-data client).

## Run locally

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

```bash
cd backend
uv sync                       # create .venv from the lockfile

# (one-off) refresh the corpus from Wikipedia
uv run python -m scripts.build_corpus

# Build the index from the committed corpus (data/corpus/*.txt)
uv run python -m app.rag.ingest

# Serve the API (needs GOOGLE_API_KEY in ../.env for /ask)
uv run uvicorn app.main:app --reload --port 8000
```

Endpoints:
- `POST /ingest` — add a single `.txt` file to the corpus index
- `POST /ingest/corpus` — rebuild the index from every `.txt` in `data/corpus`
- `POST /ask` — `{ "question": "..." }` → grounded answer + retrieved sources
- `GET /health` — service status + indexed chunk count
- `GET /debug/chunks` — inspect stored chunks/embeddings
- `DELETE /reset` — clear the vector store

Secrets come from the repo-root `.env` (see `.env.example`); `GOOGLE_API_KEY` is required for `/ask`.

The RAG code in `app/rag/` is **copied/adapted** from the `rag-poc-langchain` teaching POC in Phase 3.
