"""Build the World Cup corpus and write it to ``data/corpus``.

Manual, on-demand job — nothing triggers it automatically. Run from ``backend/``:

    uv run python -m scripts.build_corpus

Re-run to refresh the pages or change ``WIKI_QUERIES`` (each run overwrites the
``.txt`` files); then commit them. Swap ``build_source()`` for an ``S3Source`` /
``FilesSource`` to change where the data comes from.
"""

from __future__ import annotations

import re
from pathlib import Path

from rag.sources import WikipediaSource, load_documents

# backend/ is one level up from backend/scripts/.
BASE_DIR = Path(__file__).resolve().parents[1]
CORPUS_DIR = BASE_DIR / "data" / "corpus"

# Curated, minimal POC set (~14 pages): the 2026 tournament, its format and hosts,
# recent past tournaments, and a few leading national teams.
WIKI_QUERIES = [
    "2026 FIFA World Cup",
    "2026 FIFA World Cup qualification",
    "FIFA World Cup",
    "FIFA World Cup hosts",
    "List of FIFA World Cup stadiums",
    "MetLife Stadium",
    "2022 FIFA World Cup",
    "2018 FIFA World Cup",
    "Argentina national football team",
    "France national football team",
    "Brazil national football team",
    "Germany national football team",
    "England national football team",
    "United States men's national soccer team",
]


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "page"


def build_source() -> WikipediaSource:
    return WikipediaSource(queries=WIKI_QUERIES)


def main() -> None:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    documents = load_documents(build_source())
    if not documents:
        print("No documents fetched — check network access to Wikipedia.")
        return

    written = 0
    for doc in documents:
        title = doc.metadata.get("title") or doc.metadata.get("query") or "page"
        slug = slugify(str(title))
        out_path = CORPUS_DIR / f"{slug}.txt"
        out_path.write_text(doc.page_content, encoding="utf-8")
        written += 1
        print(f"  wrote {out_path.relative_to(BASE_DIR)} ({len(doc.page_content):,} chars)")

    print(f"\nDone. {written} file(s) written to {CORPUS_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    main()
