
FROM python:3.12-slim

# uv for dependency management (pinned to the version used locally).
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/home/user/.cache/huggingface \
    UV_NO_CACHE=1

# HF Spaces runs the container as UID 1000 — create a matching user.
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

# Put the project venv on PATH (used by python/uvicorn and the MCP subprocess).
ENV VIRTUAL_ENV=/home/user/app/backend/.venv \
    PATH=/home/user/app/backend/.venv/bin:/home/user/.local/bin:$PATH

COPY --chown=user backend/pyproject.toml backend/uv.lock ./backend/

RUN cd backend && uv sync --frozen --no-dev

COPY --chown=user . .

# Pre-download the MiniLM embedding model so cold starts are fast.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Build the RAG index at image-build time so cold starts just LOAD it instead
# of rebuilding ~1,565 chunks on every boot. The startup hook sees a non-empty
# store and skips the rebuild, shaving several seconds off the first request.
RUN cd backend && python -m rag.ingest

EXPOSE 7860
WORKDIR /home/user/app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
