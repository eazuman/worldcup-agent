# GoldenGoal backend — FastAPI + RAG (local MiniLM embeddings) + MCP football tools.
# Built for Hugging Face Spaces (Docker SDK); serves on port 7860.
#
# The whole repo is copied because code paths are relative to the repo root and
# the agent spawns mcp_server/football_tools.py as a subprocess. The Chroma index
# is gitignored and rebuilt from data/corpus on first boot (see main.py startup).
FROM python:3.12-slim

# uv binary (matches the version used locally) for dependency management.
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/home/user/.cache/huggingface \
    UV_NO_CACHE=1

# Hugging Face Spaces runs the container as UID 1000 — create a matching user so
# the app can read its model cache and write the rebuilt index.
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

# Put the project venv on PATH so `python`/`uvicorn` (and the MCP subprocess via
# sys.executable) all use it.
ENV VIRTUAL_ENV=/home/user/app/backend/.venv \
    PATH=/home/user/app/backend/.venv/bin:/home/user/.local/bin:$PATH

# Dependency manifests first for better layer caching.
COPY --chown=user backend/pyproject.toml backend/uv.lock ./backend/

# Install the locked dependencies (torch resolves to the CPU-only wheel via the
# pytorch-cpu index configured in pyproject.toml) into backend/.venv.
RUN cd backend && uv sync --frozen --no-dev

# Copy the application code (backend, mcp_server, data/corpus, skills).
COPY --chown=user . .

# Pre-download the MiniLM embedding model into the image so cold starts are fast.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

EXPOSE 7860
WORKDIR /home/user/app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
