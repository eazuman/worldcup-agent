"""Pluggable corpus sources for the World Cup RAG pipeline.

The rest of the pipeline (``ingest`` -> ``store`` -> ``service``) only ever sees
LangChain :class:`~langchain_core.documents.Document` objects. This module is the
single seam where *where the data comes from* is decided, so a new source can be
added without touching ingest, the vector store, or retrieval.

Today we acquire pages from Wikipedia. ``S3Source`` and ``FilesSource`` are stubbed
so the same ``load_documents`` entry point can later read from object storage or a
local folder by swapping the source object only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.documents import Document


@dataclass
class WikipediaSource:
    """Load one Wikipedia article per query via LangChain's ``WikipediaLoader``."""

    queries: list[str] = field(default_factory=list)
    lang: str = "en"
    load_max_docs: int = 1

    # Wikipedia now rejects requests without a descriptive User-Agent (policy
    # T400119), so we identify this POC client per their robot policy.
    user_agent: str = (
        "GoldenGoal-WorldCup-RAG/0.1 (https://github.com/eazuman/worldcup-agent; "
        "demo POC)"
    )

    def load(self) -> list[Document]:
        # Imported lazily so the dependency is only required when this source runs.
        import wikipedia
        from langchain_community.document_loaders import WikipediaLoader

        wikipedia.set_user_agent(self.user_agent)

        documents: list[Document] = []
        for query in self.queries:
            loader = WikipediaLoader(
                query=query,
                lang=self.lang,
                load_max_docs=self.load_max_docs,
                doc_content_chars_max=1_000_000,
            )
            docs = loader.load()
            if not docs:
                continue
            # Keep the first (best) match and tag it with the query we asked for.
            doc = docs[0]
            metadata = dict(doc.metadata or {})
            metadata["query"] = query
            metadata.setdefault("source", "wikipedia")
            documents.append(Document(page_content=doc.page_content, metadata=metadata))
        return documents


@dataclass
class S3Source:
    """Stub: load documents from an S3 bucket/prefix (e.g. via ``S3DirectoryLoader``).

    Implement with ``langchain_community.document_loaders.S3DirectoryLoader`` plus AWS
    credentials when object storage is needed. Left unimplemented for the POC.
    """

    bucket: str = ""
    prefix: str = ""

    def load(self) -> list[Document]:
        raise NotImplementedError(
            "S3Source is not implemented yet. Use WikipediaSource for the POC."
        )


@dataclass
class FilesSource:
    """Stub: load documents from a local directory of files.

    Implement with ``DirectoryLoader``/``TextLoader`` when reading hand-curated files.
    """

    directory: str = ""
    glob: str = "**/*.txt"

    def load(self) -> list[Document]:
        raise NotImplementedError(
            "FilesSource is not implemented yet. Use WikipediaSource for the POC."
        )


def load_documents(source: WikipediaSource | S3Source | FilesSource) -> list[Document]:
    """Single entry point: load documents from any pluggable source.

    Every source returns the same ``Document`` shape, so callers downstream never
    need to know which backend produced the data.
    """
    return source.load()
