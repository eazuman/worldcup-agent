# RAG pipeline

Code lives in `backend/rag/` and is exposed by `backend/app/main.py`.

## Two stages: build vs serve

RAG here splits into an **offline build** (done by hand, occasionally) and an
**online serve** (automatic, every request):

1. **Build the corpus (offline, manual)** — fetch source text and commit it.
   - `scripts/build_corpus.py` → `uv run python -m scripts.build_corpus`
   - Pulls ~14 curated Wikipedia pages via LangChain's `WikipediaLoader`
     (`rag/sources.py`) and writes one `data/corpus/<slug>.txt` per page.
   - The `.txt` files are **committed to git** = durable source of truth.
   - Re-run only to refresh/change the pages, then commit the new `.txt` files.
2. **Index + serve (automatic)** — chunk, embed, store, retrieve, generate.
   - The Chroma index (`data/chroma_db/`) is **gitignored** and rebuilt from the
     committed `.txt` files, so deploys are deterministic.

### How we load the Wikipedia data (manual trigger)

- **Trigger:** purely **manual / on-demand**. Nothing runs it automatically — not
  the Dockerfile, not app startup, not CI. You run it by hand:
  `uv run python -m scripts.build_corpus` (from `backend/`).
- **When to run:** occasionally — when refreshing the pages (Wikipedia changed) or
  editing the `WIKI_QUERIES` list. It is **re-runnable**, not strictly one-time; each
  run **overwrites** `data/corpus/*.txt`. Commit the result afterwards.
- **How it fetches:** `scripts/build_corpus.py` calls `load_documents(WikipediaSource(
  queries=WIKI_QUERIES))`. `WikipediaSource` (`rag/sources.py`) uses LangChain's
  `WikipediaLoader`, one best-match page per query, and sets a required descriptive
  User-Agent (Wikipedia policy). Each page → `data/corpus/<slug>.txt`.
- **Not used at runtime:** the live app never calls Wikipedia; it only reads the
  committed `.txt` files. Only this manual script hits Wikipedia.

## End-to-end flow

```
Wikipedia ──WikipediaLoader──▶ data/corpus/*.txt   (Stage 1, manual)
   *.txt ──RecursiveCharacterTextSplitter──▶ ~1,565 chunks (500 chars / 50 overlap)
   chunks ──HuggingFaceEmbeddings (MiniLM)──▶ 384-dim vectors
   vectors ──Chroma.add_documents──▶ data/chroma_db (text + vector + metadata)
   question ──MiniLM embeds──▶ Chroma.similarity_search (top_k=3)
   top-3 chunks ──prompt | Gemini | StrOutputParser──▶ grounded answer + sources
```

**When each part runs:**

- **Chunk + embed + store** runs at **app startup** via `_ensure_index()` in
  `main.py` (`@app.on_event("startup")`) — but only when the store is empty
  (`vector_store.count() == 0`). On HF Spaces the disk is ephemeral, so a cold
  start always rebuilds (~1,565 chunks). Can also be forced with
  `POST /ingest/corpus` or `uv run python -m rag.ingest`.
  - Caveat: locally the Chroma DB persists, so a refreshed `data/corpus/` is
    **not** re-indexed on startup (count > 0); force it with `/ingest/corpus`.
- **Retrieve + generate** runs at **request time**, on every `/ask` (and is also
  exposed as a tool to the `/agent/chat` agent).

**Chunking** (`ingest.py`): `RecursiveCharacterTextSplitter(chunk_size=500,
chunk_overlap=50)` — splits on natural boundaries (paragraph → line → sentence),
overlapping 50 chars so a fact split across a boundary isn't lost. Each chunk is
stored as a `Document` with metadata `{chunk_id, doc_id, chunk_index,
source_file}` and a deterministic id (`<file>-<sha256[:8]>-<n>`), so re-ingesting
overwrites instead of duplicating.

**Embedding is implicit:** `CorpusVectorStore` builds `Chroma(embedding_function=
MiniLM)` once in `__init__`, so `add_documents()` auto-embeds every chunk and
`search()` auto-embeds the query — the same model must embed both sides.

**Retrieval = vector similarity, not keyword match:** the question becomes 384
numbers; Chroma compares it against all stored chunk vectors by cosine similarity
and returns the `top_k` nearest. So "who lifted the trophy in Qatar" can match
"Argentina won the 2022 final" with no shared keywords.

## LangChain's role at each phase

LangChain is the common "glue" — a standard interface around each external tool so
pieces snap together and engines can be swapped in one line.

| Phase | LangChain piece | File | What it does / why it helps |
|---|---|---|---|
| Fetch | `WikipediaLoader` | `sources.py` | Downloads pages → uniform `Document` objects |
| Standardize | `Document` | all | One shape (`page_content` + `metadata`) so later steps are source-agnostic |
| Chunk | `RecursiveCharacterTextSplitter` | `ingest.py` | Boundary-aware splitting with overlap |
| Embed | `HuggingFaceEmbeddings` | `embeddings.py` | Wraps `sentence-transformers` (HF does the real math) → swappable to OpenAI etc. |
| Store + Search | `Chroma` | `store.py` | Wraps ChromaDB; auto-embeds on add, cosine search on query |
| Generate | `ChatGoogleGenerativeAI` + LCEL `prompt \| llm \| StrOutputParser` | `service.py`, `main.py` | Wraps Gemini and pipes prompt → model → text |

Note: LangChain does **not** contain the embedding model or the vector math — it
calls down to HuggingFace `sentence-transformers` (MiniLM) and to ChromaDB. Its
value is the standard, swappable interface, not the underlying compute.

## How the result is produced (the final step)

`RAGService.answer_question(question, top_k=3)` in `service.py`:

1. Guard: if `count() == 0` → "No corpus indexed yet"; if no hits → "could not
   find relevant context".
2. `vector_store.search(question, top_k=3)` → top-3 chunks (text + score + metadata).
3. Pack them into a single `context` string (`Chunk 1:\n... Chunk 2:\n...`).
4. `self.chain.invoke({question, context})` — the LCEL chain `prompt | llm |
   StrOutputParser` sends the question + context to Gemini under a grounding system
   prompt, then extracts plain text.
5. Returns `{ "answer", "sources" }` — the answer **plus** the exact chunks used,
   so the UI can cite sources.

The grounding system prompt forces Gemini to answer **only** from the retrieved
context and to reply "I do not know based on the indexed World Cup corpus" when the
context lacks the answer — this is the anti-hallucination guardrail.

## Components

- **Sources** (`sources.py`): pluggable corpus sources returning LangChain
  `Document` objects. `WikipediaSource` (implemented, uses `WikipediaLoader` with a
  required User-Agent); `S3Source` / `FilesSource` are stubs for later. Single entry
  point `load_documents(source)` so swapping the data origin touches nothing else.
- **Ingest / chunking** (`ingest.py`): `RecursiveCharacterTextSplitter`
  (`chunk_size=500`, `chunk_overlap=50`). `index_text()` chunks + adds one doc;
  `ingest_corpus()` resets then re-indexes every `data/corpus/*.txt` (~1,565 chunks
  across 14 files). Stable ids via `make_doc_id` (sha256 prefix).
- **Embeddings** (`embeddings.py`): `HuggingFaceEmbeddings` with
  `sentence-transformers/all-MiniLM-L6-v2`. Runs locally, needs no API key,
  produces 384-dimensional vectors.
- **Vector store** (`store.py`): `CorpusVectorStore` wraps LangChain's `Chroma`.
  - Persistent on disk at `data/chroma_db/` (gitignored; rebuilt from the corpus).
  - Collection name: `worldcup_corpus`.
  - Methods: `reset()`, `add_documents()`, `search()` (uses
    `similarity_search_with_relevance_scores`), `peek()`, `count()`.
- **Service** (`service.py`): `RAGService`.
  - A grounding system prompt forces answers to come only from retrieved context;
    otherwise it replies "I do not know based on the indexed World Cup corpus."
  - LCEL chain: `prompt | llm | StrOutputParser`.
  - `answer_question(question, top_k=3)` returns `{ "answer", "sources" }`, where
    `sources` are the retrieved chunks (text, score, metadata).

## Where the LLM is called

- The Gemini model is built lazily in `main.py` `get_rag_service()`:
  `ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)`.
- The actual call happens in `service.py` at `self.chain.invoke(...)`.
- Retrieval (embeddings + Chroma search) needs no key; only generation needs
  `GOOGLE_API_KEY` (read from the repo-root `.env`).

## API endpoints (`main.py`)

- `POST /ask` — `{question}` -> grounded answer + sources.
- `POST /ingest/corpus` — rebuild the index from `data/corpus/*.txt`.
- `POST /ingest` — add a single uploaded `.txt` (legacy/manual helper).
- `GET /health` — status + indexed chunk count.
- `GET /debug/chunks` — inspect stored chunks / embeddings.
- `DELETE /reset` — clear the vector store.

## How to verify an answer is grounded (not from the LLM's memory)

1. Inspect the `sources` array returned by `/ask`.
2. Ask an off-corpus question (e.g. "capital of France") — it should refuse.
3. `DELETE /reset` then `/ask` — the answer disappears; rebuild with
   `/ingest/corpus`.
