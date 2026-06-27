"""Skill tool — exposes the curated ``goldengoal-architecture`` skill.

Lets the agent answer self/meta questions about how THIS app is built by reading
verbatim docs: it reads ``SKILL.md`` to see what the skill covers, then reads the
matching reference file itself — mirroring how a skill is followed, with no
keyword routing in code.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

# Directory of the curated "goldengoal-architecture" skill — verbatim docs about
# how THIS app is built (RAG, MCP, agent, models).
SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "goldengoal-architecture"


def make_skill_tool():
    """Build the in-process tool that reads files from the skill directory."""

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
