---
name: goldengoal-architecture
description: >-
  How the GoldenGoal World Cup 2026 assistant is built. USE FOR questions about
  the system architecture, the backend, the RAG pipeline, the data/ingestion
  pipeline, the MCP tools/server, the agent, which LLM/embeddings are used, and
  how RAG and MCP tools connect to the agent. Read the matching reference file
  under reference/ for details before answering.
---

# GoldenGoal Architecture Skill

Authoritative, curated knowledge about how **this application** is built. When a
user asks how GoldenGoal works (architecture, RAG, MCP, agent, data pipeline,
models), answer from these files rather than guessing. If a detail is not covered
here, say so instead of inventing it.

## When to use this skill

Use it for self-referential / "meta" questions about the app, e.g.:

- "How is this app built?" / "What's the architecture?"
- "How does the RAG pipeline work? Which embeddings and vector store?"
- "How is the World Cup corpus built and ingested?"
- "Which LLM is used and where is it called?"
- "What MCP tools/server are used and how do they connect to the agent?"
- "How are RAG and the MCP tools wired into the agent?"

Do **not** use it for World Cup facts (those come from the RAG corpus) or live
match data (those come from MCP tools).

## Reference files

Read the file that matches the question:

| Topic | File |
|---|---|
| Whole-system overview, components, request flow | [reference/architecture.md](reference/architecture.md) |
| RAG: embeddings, Chroma store, retrieval, `/ask` | [reference/rag-pipeline.md](reference/rag-pipeline.md) |
| Data: pluggable sources, corpus build, ingestion | [reference/data-pipeline.md](reference/data-pipeline.md) |
| MCP server + tools (live football data) | [reference/mcp-tools.md](reference/mcp-tools.md) |
| Agent: LLM, routing RAG vs MCP, how it's wired | [reference/agent.md](reference/agent.md) |

## Status note

The RAG pipeline and data pipeline are **implemented**. The MCP tools and the
orchestrating agent are **planned** (Phases 4–5); their reference files describe
the intended design and are marked accordingly.
