# Data / ingestion pipeline

How text knowledge gets into the vector store.

## Pluggable sources (`backend/rag/sources.py`)

A single seam decides *where data comes from*. Every source returns LangChain
`Document` objects, so the rest of the pipeline never changes.

- `load_documents(source)` — entry point, dispatches to the source.
- `WikipediaSource(queries=[...])` — **implemented**. Uses LangChain's
  `WikipediaLoader`; sets a descriptive User-Agent (Wikipedia now requires one).
- `S3Source` / `FilesSource` — **stubbed** for later (object storage / local
  folder), same `Document` output.

## Building the corpus (`backend/scripts/build_corpus.py`)

- Fetches ~14 curated Wikipedia pages (2026 World Cup, format/qualification,
  hosts/stadiums, MetLife Stadium, 2022 & 2018 tournaments, several national
  teams).
- Writes one `.txt` per page into `data/corpus/`.
- The corpus `.txt` files are **committed to git** so the index can be rebuilt
  deterministically anywhere.

Run: `uv run python -m scripts.build_corpus`

## Ingesting into Chroma (`backend/rag/ingest.py`)

- `RecursiveCharacterTextSplitter` with `chunk_size=500`, `chunk_overlap=50`.
- `make_doc_id` derives a stable id from a sha256 prefix of the text.
- `index_text(store, filename, text)` chunks + adds one document.
- `ingest_corpus(store, corpus_dir)` resets the collection, then adds every
  `.txt` in `data/corpus/` (currently ~1,565 chunks across 14 files).

Run: `uv run python -m rag.ingest` (or `POST /ingest/corpus`).

## Adding a second knowledge set (e.g. "about the app")

Two clean options:
1. **Skill (chosen for architecture docs)** — curated `.md` read verbatim; not
   embedded. See this skill.
2. **Second Chroma collection** — author `.txt` files, ingest them into a store
   created with a different `collection_name` (e.g. `about_app`) so retrieval
   stays separated from the World Cup corpus.
