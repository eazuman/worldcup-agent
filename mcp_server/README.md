# MCP server (Phase 4)

A standalone **FastMCP** server exposing World Cup football tools, runnable on its own and
pluggable into any MCP client (Claude Desktop, etc.).

Planned tools (backed by football-data.org, cached):
- `get_fixtures(competition="WC", status=None)`
- `get_standings(competition="WC")`
- `get_top_scorers(competition="WC")`
- `get_results_on_date(date)` — via TheSportsDB

Run (once built):

```bash
python football_tools.py   # serves streamable-http on :8001/mcp
```
