# RAG pipeline

Code lives in `backend/app/rag/` and is exposed by `backend/app/main.py`.

## Components

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
