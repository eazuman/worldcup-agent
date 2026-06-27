# GoldenGoal backend — FastAPI + RAG (local MiniLM embeddings) + MCP football tools.
# Built for Hugging Face Spaces (Docker SDK); serves on port 7860.
#
# The whole repo is copied because code paths are relative to the repo root and
# the agent spawns mcp_server/football_tools.py as a subprocess. The Chroma index
# is gitignored and rebuilt from data/corpus on first boot (see main.py startup).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/user/.cache/huggingface

# Hugging Face Spaces runs the container as UID 1000 — create a matching user so
# the app can read its model cache and write the rebuilt index.
RUN useradd -m -u 1000 user
USER user
ENV PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

# Install CPU-only PyTorch first (much smaller than the default CUDA wheel),
# then the rest of the backend dependencies.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY --chown=user backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the application code (backend, mcp_server, data/corpus, skills).
COPY --chown=user . .

# Pre-download the MiniLM embedding model into the image so cold starts are fast.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

EXPOSE 7860
WORKDIR /home/user/app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
