# Architecture overview

GoldenGoal is a World Cup 2026 assistant. It is a monorepo with three parts:

- **frontend/** — Vue 3 + Vite + TypeScript single-page app (chat, standings,
  schedule). Currently renders mock data; talks to the backend over HTTP.
- **backend/** — FastAPI service exposing the RAG API and (later) the agent.
  Dependencies are managed with `uv` (`pyproject.toml` + `uv.lock`), Python 3.12.
- **mcp_server/** — a FastMCP server exposing live football data as MCP tools.

## Knowledge sources (the core idea)

The assistant separates knowledge by *shape*:

- **RAG** = stable, unstructured **text** knowledge (World Cup rules, history,
  host cities, teams). Retrieved by semantic similarity.
- **MCP tools** = **live / structured** data and actions (scores, standings,
  fixtures) fetched from an API at query time.
- **Architecture self-docs** = this skill — curated text read verbatim, not
  embedded.

An orchestrating **agent** decides which source to use per question and composes
the answer.

## Request flow (today, RAG API)

```
Client -> FastAPI POST /ask
       -> RAGService.answer_question()
       -> CorpusVectorStore.search()  (MiniLM embeddings, top-3 chunks)
       -> LCEL chain: prompt | Gemini | StrOutputParser
       -> { answer, sources }
```

## Target flow (with agent + MCP)

```
Client -> Agent
       -> decides: RAG tool (knowledge)  AND/OR  MCP tool (live data)
       -> composes a grounded answer
```

## Key technologies

- FastAPI, LangChain (LCEL + agent), Chroma vector store
- Embeddings: local `sentence-transformers/all-MiniLM-L6-v2` (no API key)
- LLM: Google Gemini `gemini-2.5-flash` via `langchain-google-genai`
- MCP: FastMCP + `langchain-mcp-adapters`
- Tooling: `uv`, Python 3.12
