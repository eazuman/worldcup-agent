# RAG corpus

Committed plain-text corpus the RAG index is rebuilt from on every deploy (Phase 3).

Populate with `backend/scripts/scrape_corpus.py`:
- ~48 participating-team Wikipedia pages
- past World Cup tournament pages (1930–2022)
- host-stadium pages
- the 2026 format / rules page

The generated vector index lives in `../chroma_db/` (gitignored).
