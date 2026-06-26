"""RAG layer — copied/adapted from the rag-poc-langchain teaching POC.

Differences vs the POC (per the World Cup build plan, Phase 3):
- Embeddings: local ``all-MiniLM-L6-v2`` (HuggingFace) instead of OpenAI — no API cost.
- LLM: Google Gemini ``gemini-2.5-flash`` instead of OpenAI ``gpt-4o-mini``.
- Indexing: a multi-file **corpus** (data/corpus/*.txt) instead of a single active document.
"""
