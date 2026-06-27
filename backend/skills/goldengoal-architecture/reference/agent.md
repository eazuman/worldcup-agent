# Agent

> Status: **implemented**. The agent is built with `langchain.agents.create_agent`
> in `backend/app/agent.py` and exposed over `POST /agent/chat` (SSE streaming).

## Role

A single LangChain agent orchestrates all knowledge sources and decides, per
question, which to use and how to combine them.

## Model

- **LLM**: Google Gemini `gemini-2.5-flash` via `langchain-google-genai`
  (the same model used by the RAG service today).

## Tools the agent will have

1. **RAG retrieval tool** — wraps `RAGService` / `CorpusVectorStore` to answer
   stable World Cup knowledge questions from the indexed corpus.
2. **MCP tools** — live football data, loaded from the FastMCP server via
   `langchain-mcp-adapters`.
3. **Architecture self-docs** — the `explain_goldengoal_setup` tool, backed by
   this skill, for questions about how the app itself is built.

## Routing logic (intended)

- Stable World Cup facts ("explain the 48-team format") -> RAG tool.
- Live data ("who is winning right now?", "today's fixtures") -> MCP tool.
- "How is this app built?" -> consult the `goldengoal-architecture` skill.
- Mixed questions -> call multiple tools and compose
  ("Is the 2022 winner playing today?" -> RAG for the winner + MCP for fixtures).

## How the system prompt references this skill

When the agent is built, its system prompt will instruct it: for questions about
the application's own architecture, consult the `goldengoal-architecture` skill
(`skills/goldengoal-architecture/SKILL.md`) and read the matching reference file
before answering, rather than inventing details.
