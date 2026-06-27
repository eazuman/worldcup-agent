"""LangChain agent for GoldenGoal — a World Cup soccer-coach assistant.

Built with ``langchain.agents.create_agent`` (LangChain 1.x), which returns a
compiled LangGraph state graph. The agent runs a tool-calling loop: the LLM
decides when to call the RAG retrieval tool, reads the returned context, and
writes a grounded answer.

The RAG knowledge base is exposed as an **in-process tool** (a direct call into
the vector store), not an HTTP/MCP hop — RAG is a local capability of this
backend. MCP tools (live football data) will be added alongside this tool later.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.rag.store import CorpusVectorStore

# Persona + guardrails. The agent is a soccer coach: football only, grounded in
# the retrieved corpus, and it refuses anything off-topic.
COACH_SYSTEM_PROMPT = (
    "You are GoldenGoal, an expert soccer (football) coach who answers questions "
    "about the FIFA World Cup and football in general.\n\n"
    "Rules:\n"
    "1. For ANY factual question, first call the `search_worldcup_knowledge` tool "
    "and base your answer ONLY on the text it returns. Do not rely on prior "
    "knowledge for facts.\n"
    "2. If the tool returns no relevant information, say: 'I don't know that based "
    "on my World Cup knowledge base.'\n"
    "3. If the question is NOT about football/soccer or the World Cup, refuse with: "
    "'I'm your soccer coach — I only talk football. I don't know anything outside "
    "of that.'\n"
    "4. Keep answers concise, friendly, and encouraging, like a coach talking to a "
    "player. You may cite the source files the tool returns."
)

TOP_K = 4


def make_knowledge_tool(vector_store: CorpusVectorStore):
    """Build the in-process RAG retrieval tool bound to a vector store."""

    @tool
    def search_worldcup_knowledge(query: str) -> str:
        """Search the indexed FIFA World Cup knowledge base and return relevant
        text passages. Use this for every factual question about the World Cup,
        teams, players, history, hosts, stadiums, or tournament format."""
        hits = vector_store.search(query=query, top_k=TOP_K)
        if not hits:
            return "NO_RESULTS"
        return "\n\n".join(
            f"[source: {hit['metadata'].get('source_file', 'unknown')}]\n{hit['text']}"
            for hit in hits
        )

    return search_worldcup_knowledge


def build_agent(vector_store: CorpusVectorStore, llm: BaseChatModel):
    """Assemble the compiled agent graph: LLM + RAG tool + coach system prompt.

    Returns a ``CompiledStateGraph`` that supports ``astream_events`` for
    token/tool streaming. An in-memory checkpointer keeps short-term conversation
    state keyed by ``thread_id``.
    """
    knowledge_tool = make_knowledge_tool(vector_store)
    return create_agent(
        model=llm,
        tools=[knowledge_tool],
        system_prompt=COACH_SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
