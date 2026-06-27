# MCP tools / server

> Status: **implemented**. A FastMCP server in `mcp_server/football_tools.py`
> exposes the football tools, loaded into the agent via `langchain-mcp-adapters`.

## Purpose

MCP (Model Context Protocol) tools provide **live / structured** data that does
not belong in RAG — primarily live football data: scores, standings, fixtures,
top scorers. This data changes constantly, so it is fetched per request rather
than embedded.

## Design

- **Server**: a **FastMCP** server in `mcp_server/` exposing tools such as:
  - `get_standings(competition)`
  - `get_fixtures(team_or_date)`
  - `get_live_scores()`
  - `get_top_scorers(competition)`
- **Data source**: football-data.org REST API (key `FOOTBALL_DATA_KEY` in
  `.env`).
- **Transport**: MCP over stdio (or HTTP), consumed by the agent.

## How it connects to the agent

- The agent (backend, Phase 5) uses **`langchain-mcp-adapters`** to load the
  FastMCP server's tools as LangChain tools.
- The agent then treats each MCP tool like any other tool and calls it when a
  question needs live data.

```
Agent --(langchain-mcp-adapters)--> FastMCP server --(football-data.org)--> live data
```

## Why MCP and not RAG for this

Live scores are structured and change every minute. Embedding them would be
stale instantly and wasteful. A tool call returns fresh, exact data on demand.
