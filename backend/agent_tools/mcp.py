"""Live football tools — loaded from the standalone FastMCP server.

The agent reaches live 2026 data (standings, fixtures, scores, top scorers) via
``langchain-mcp-adapters``, which launches ``mcp_server/football_tools.py`` as a
stdio subprocess and surfaces its MCP tools as ordinary LangChain tools.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Path to the standalone FastMCP football server, launched over stdio. Uses the
# current interpreter so the subprocess shares this backend's virtualenv (where
# `mcp` is installed).
MCP_SERVER_PATH = Path(__file__).resolve().parents[1] / "mcp_server" / "football_tools.py"


async def load_mcp_tools() -> list:
    """Load the FastMCP football tools as LangChain tools via stdio adapters.

    Returns an empty list if the MCP server cannot be reached, so the agent
    still works with just the RAG tool.
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient(
        {
            "football": {
                "command": sys.executable,
                "args": [str(MCP_SERVER_PATH)],
                "transport": "stdio",
            }
        }
    )
    return await client.get_tools()
