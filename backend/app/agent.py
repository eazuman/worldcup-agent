"""LangChain agent for GoldenGoal — a World Cup soccer-coach assistant.

Built with ``langchain.agents.create_agent`` (LangChain 1.x), which returns a
compiled LangGraph state graph. The agent runs a tool-calling loop: the LLM
decides when to call the RAG retrieval tool, reads the returned context, and
writes a grounded answer.

The RAG knowledge base is exposed as an **in-process tool** (a direct call into
the vector store), and live football data is exposed via **MCP tools** loaded
from the standalone FastMCP server in ``mcp_server/`` through
``langchain-mcp-adapters``. The agent's LLM picks the right tool(s) per question.
"""

from __future__ import annotations

import sys
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.rag.store import CorpusVectorStore

# Path to the standalone FastMCP football server, launched over stdio by the
# langchain-mcp-adapters client. Uses the current interpreter so the subprocess
# shares this backend's virtualenv (where `mcp` is installed).
MCP_SERVER_PATH = Path(__file__).resolve().parents[2] / "mcp_server" / "football_tools.py"

# Directory of the curated "goldengoal-architecture" skill — verbatim docs about
# how THIS app is built (RAG, MCP, agent, models). Surfaced to the agent as an
# in-process tool so the coach can answer self/meta questions about its own setup.
SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "goldengoal-architecture"

# Persona + guardrails. The agent is a soccer coach: football only. It picks the
# right tool per question — RAG for historical/reference facts, the MCP football
# tools for live/current 2026 data — and may call BOTH when a question needs it.
COACH_SYSTEM_PROMPT = (
    "You are GoldenGoal, an expert soccer (football) coach who answers questions "
    "about the FIFA World Cup and football in general.\n\n"
    "You have two kinds of tools and must choose the right one(s):\n"
    "• search_worldcup_knowledge (RAG knowledge base): use for HISTORICAL and "
    "REFERENCE facts — tournament format and rules, hosts, stadiums, past "
    "winners and finals, team history, and previous World Cups.\n"
    "• Live football tools (get_standings, get_fixtures, get_live_scores, "
    "get_top_scorers): use for CURRENT / LIVE 2026 data — today's match "
    "schedule, current group standings, live scores, and the current top "
    "scorers.\n"
    "• read_skill_file (goldengoal-architecture skill): use for SELF / META "
    "questions about how YOU (the GoldenGoal assistant) are built — anything "
    "about this project's setup, architecture, the RAG pipeline, the "
    "data/ingestion pipeline, the MCP server and tools, the agent, LangChain, "
    "or which LLM/embeddings are used. Follow this skill workflow: first call "
    "read_skill_file('SKILL.md') to see what the skill covers and its list of "
    "reference files, then call read_skill_file on the matching reference file, "
    "then answer from what you read.\n\n"
    "Rules:\n"
    "1. Decide which tool fits the question and call it before answering. For a "
    "question that mixes history with live data (e.g. comparing a team's current "
    "form to a past campaign), call BOTH the relevant live tool and "
    "search_worldcup_knowledge, then combine the results.\n"
    "2. Base factual answers ONLY on what the tools return; do not rely on prior "
    "knowledge. If the tools return no relevant information, say: 'I don't know "
    "that based on my World Cup data.'\n"
    "3. If the question is NOT about football/soccer or the World Cup AND is not "
    "about how you (GoldenGoal) are built, refuse with: 'I'm your soccer coach — "
    "I only talk football and how I'm built. I don't know anything outside of "
    "that.'\n"
    "4. Keep answers concise, friendly and encouraging, like a coach talking to a "
    "player. You may cite the sources the tools return."
)

TOP_K = 4


def make_knowledge_tool(vector_store: CorpusVectorStore):
    """Build the in-process RAG retrieval tool bound to a vector store."""

    @tool
    def search_worldcup_knowledge(query: str) -> str:
        """Search the indexed FIFA World Cup knowledge base for HISTORICAL and
        REFERENCE facts and return relevant text passages. Use this for the
        tournament format and rules, hosts, stadiums, past winners and finals,
        team history, records, and previous World Cups. Do NOT use this for live
        scores, current standings or today's schedule — use the live football
        tools for those."""
        hits = vector_store.search(query=query, top_k=TOP_K)
        if not hits:
            return "NO_RESULTS"
        return "\n\n".join(
            f"[source: {hit['metadata'].get('source_file', 'unknown')}]\n{hit['text']}"
            for hit in hits
        )

    return search_worldcup_knowledge


def make_skill_tool():
    """Build the in-process tool that exposes the curated
    ``goldengoal-architecture`` skill. The agent reads ``SKILL.md`` to learn
    what the skill covers, then reads the relevant reference file itself —
    mirroring how a skill is followed, with no keyword routing in code."""

    @tool
    def read_skill_file(path: str = "SKILL.md") -> str:
        """Read a file from the goldengoal-architecture skill (curated docs about
        how THIS app is built). Start with 'SKILL.md' to see what it covers and
        the list of reference files, then read a specific one such as
        'reference/agent.md', 'reference/rag-pipeline.md', 'reference/mcp-tools.md',
        'reference/data-pipeline.md' or 'reference/architecture.md'. Returns the
        file's text verbatim."""
        target = (SKILL_DIR / path).resolve()
        # Path-traversal guard: only allow files inside the skill directory.
        if not str(target).startswith(str(SKILL_DIR.resolve())):
            return "INVALID_PATH"
        try:
            return target.read_text(encoding="utf-8")
        except OSError:
            return "NO_RESULTS"

    return read_skill_file


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


async def build_agent_async(vector_store: CorpusVectorStore, llm: BaseChatModel):
    """Assemble the compiled agent graph: LLM + RAG tool + MCP football tools.

    Returns a ``CompiledStateGraph`` that supports ``astream_events`` for
    token/tool streaming. An in-memory checkpointer keeps short-term conversation
    state keyed by ``thread_id``. If the MCP server fails to load, the agent is
    built with just the RAG tool.
    """
    knowledge_tool = make_knowledge_tool(vector_store)
    skill_tool = make_skill_tool()
    try:
        mcp_tools = await load_mcp_tools()
    except Exception as exc:  # noqa: BLE001 - degrade gracefully without live data
        print(f"[agent] MCP tools unavailable, RAG-only: {exc}")
        mcp_tools = []
    return create_agent(
        model=llm,
        tools=[knowledge_tool, skill_tool, *mcp_tools],
        system_prompt=COACH_SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
