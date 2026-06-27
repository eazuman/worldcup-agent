"""RAG retrieval tool — an in-process LangChain tool over the vector store.

Exposed to the agent as ``search_worldcup_knowledge``; it queries the Chroma
store directly (no network) and returns the most relevant corpus passages.
"""

from __future__ import annotations

from langchain_core.tools import tool

from rag.store import CorpusVectorStore

# Number of chunks the retrieval tool returns per query.
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
