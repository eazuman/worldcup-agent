"""GoldenGoal MCP server — live football data tools.

A standalone **FastMCP** server exposing 2026 FIFA World Cup *live* data tools:
current standings, the match schedule/fixtures, in-progress scores and the
golden-boot race. The agent loads these via ``langchain-mcp-adapters`` and calls
them whenever a question needs real-time data rather than historical facts.

Data is **mock** for this POC — swap the ``MOCK_*`` tables for real
football-data.org API calls later (key ``FOOTBALL_DATA_KEY`` in ``.env``). The
tool *descriptions* are what the agent's LLM reads to decide when to call each
tool, so they are written to clearly signal "live / current" data.

Run standalone (stdio transport, for any MCP client):

    python football_tools.py
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load FOOTBALL_DATA_KEY from the repo-root .env and the local mcp_server/.env.
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")
load_dotenv(_HERE / ".env")

# football-data.org REST API. The free tier covers the FIFA World Cup
# (competition code "WC"). Set FOOTBALL_DATA_KEY in .env to enable live data.
API_BASE = "https://api.football-data.org/v4"
COMPETITION = os.getenv("FOOTBALL_COMPETITION", "WC")
API_KEY = os.getenv("FOOTBALL_DATA_KEY", "").strip()
USE_REAL = bool(API_KEY) and not API_KEY.lower().startswith("your")

# API-Football (api-sports.io) — richest World Cup coverage for today's games,
# live scores and results. Set API_FOOTBALL_KEY in .env to enable. World Cup is
# league id 1; season is the tournament year.
AF_BASE = "https://v3.football.api-sports.io"
AF_KEY = os.getenv("API_FOOTBALL_KEY", "").strip()
AF_LEAGUE = os.getenv("API_FOOTBALL_LEAGUE", "1")
AF_SEASON = os.getenv("API_FOOTBALL_SEASON", "2026")
USE_AF = bool(AF_KEY) and not AF_KEY.lower().startswith("your")

mcp = FastMCP("goldengoal-football")


def _af_get(path: str, params: dict | None = None) -> dict:
    """GET an API-Football endpoint and return parsed JSON (raises on error)."""
    resp = httpx.get(
        f"{AF_BASE}{path}",
        headers={"x-apisports-key": AF_KEY},
        params=params,
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(str(data["errors"]))
    return data


def _api_get(path: str, params: dict | None = None) -> dict:
    """GET a football-data.org endpoint and return parsed JSON (raises on error)."""
    resp = httpx.get(
        f"{API_BASE}{path}",
        headers={"X-Auth-Token": API_KEY},
        params=params,
        timeout=15.0,
    )
    resp.raise_for_status()
    return resp.json()


def _note(text: str, sample: bool, err: str = "", live_label: str = "football-data.org live") -> str:
    """Append a provenance note so the agent (and user) knows the data source."""
    if sample:
        reason = f" (live API error: {err})" if err else ""
        return text + f"\n\n[source: sample data{reason} — set the API key for live data]"
    return text + f"\n\n[source: {live_label}]"


# ── Sample fallback data (used when no FOOTBALL_DATA_KEY is configured) ───────
MOCK_STANDINGS: dict[str, list[dict]] = {
    "A": [
        {"team": "Mexico", "P": 2, "W": 2, "D": 0, "L": 0, "GD": 4, "Pts": 6},
        {"team": "Netherlands", "P": 2, "W": 1, "D": 1, "L": 0, "GD": 2, "Pts": 4},
        {"team": "Ecuador", "P": 2, "W": 0, "D": 1, "L": 1, "GD": -1, "Pts": 1},
        {"team": "Qatar", "P": 2, "W": 0, "D": 0, "L": 2, "GD": -5, "Pts": 0},
    ],
    "D": [
        {"team": "Brazil", "P": 2, "W": 2, "D": 0, "L": 0, "GD": 5, "Pts": 6},
        {"team": "Switzerland", "P": 2, "W": 1, "D": 0, "L": 1, "GD": 0, "Pts": 3},
        {"team": "Serbia", "P": 2, "W": 0, "D": 1, "L": 1, "GD": -2, "Pts": 1},
        {"team": "Cameroon", "P": 2, "W": 0, "D": 1, "L": 1, "GD": -3, "Pts": 1},
    ],
    "F": [
        {"team": "Argentina", "P": 2, "W": 2, "D": 0, "L": 0, "GD": 3, "Pts": 6},
        {"team": "Croatia", "P": 2, "W": 1, "D": 0, "L": 1, "GD": 1, "Pts": 3},
        {"team": "Morocco", "P": 2, "W": 1, "D": 0, "L": 1, "GD": 0, "Pts": 3},
        {"team": "Japan", "P": 2, "W": 0, "D": 0, "L": 2, "GD": -4, "Pts": 0},
    ],
}

MOCK_FIXTURES_TODAY = [
    {"match": "Brazil vs Serbia", "group": "D", "kickoff": "16:00 ET", "venue": "MetLife Stadium, NJ"},
    {"match": "USA vs Wales", "group": "B", "kickoff": "19:00 ET", "venue": "SoFi Stadium, LA"},
    {"match": "Argentina vs Croatia", "group": "F", "kickoff": "22:00 ET", "venue": "Estadio Azteca, Mexico City"},
]

MOCK_FIXTURES_UPCOMING = [
    {"match": "France vs Denmark", "group": "C", "date": "2026-06-28", "kickoff": "16:00 ET"},
    {"match": "England vs Senegal", "group": "E", "date": "2026-06-28", "kickoff": "19:00 ET"},
    {"match": "Germany vs Mexico", "group": "A", "date": "2026-06-29", "kickoff": "16:00 ET"},
]

MOCK_LIVE_SCORES = [
    {"match": "Brazil vs Serbia", "group": "D", "score": "2-0", "minute": "67'", "scorers": "Vinícius Jr 23', Rodrygo 58'"},
    {"match": "USA vs Wales", "group": "B", "score": "1-1", "minute": "54'", "scorers": "Pulisic 31'; Bale 49' (pen)"},
]

MOCK_TOP_SCORERS = [
    {"player": "Kylian Mbappé", "team": "France", "goals": 4},
    {"player": "Vinícius Jr", "team": "Brazil", "goals": 3},
    {"player": "Harry Kane", "team": "England", "goals": 3},
    {"player": "Lionel Messi", "team": "Argentina", "goals": 2},
]

MOCK_RESULTS = [
    {"home": "France", "away": "Poland", "hg": 2, "ag": 1},
    {"home": "England", "away": "Senegal", "hg": 3, "ag": 0},
    {"home": "Portugal", "away": "Uruguay", "hg": 1, "ag": 1},
]


# ── Sample-data formatters ───────────────────────────────────────────────────
def _mock_standings(group: str) -> str:
    key = group.strip().upper().replace("GROUP", "").strip()
    if key and key not in MOCK_STANDINGS:
        return f"NO_DATA: no standings available for group '{group}'."
    groups = {key: MOCK_STANDINGS[key]} if key in MOCK_STANDINGS else MOCK_STANDINGS
    lines: list[str] = []
    for g, rows in groups.items():
        lines.append(f"Group {g} (current standings):")
        lines.append("Pos  Team            P  W  D  L  GD  Pts")
        for i, r in enumerate(rows, 1):
            lines.append(
                f"{i:<4} {r['team']:<14} {r['P']}  {r['W']}  {r['D']}  {r['L']}  "
                f"{r['GD']:>2}  {r['Pts']}"
            )
        lines.append("")
    return "\n".join(lines).strip()


def _mock_fixtures(when: str) -> str:
    if when.strip().lower() == "upcoming":
        return "Upcoming World Cup fixtures:\n" + "\n".join(
            f"- {r['date']} {r['kickoff']}: {r['match']} (Group {r['group']})"
            for r in MOCK_FIXTURES_UPCOMING
        )
    return "Today's World Cup fixtures:\n" + "\n".join(
        f"- {r['kickoff']}: {r['match']} (Group {r['group']}) — {r['venue']}"
        for r in MOCK_FIXTURES_TODAY
    )


def _mock_live() -> str:
    if not MOCK_LIVE_SCORES:
        return "NO_LIVE_MATCHES: no World Cup matches are in progress right now."
    return "Live now:\n" + "\n".join(
        f"- {m['match']} (Group {m['group']}): {m['score']} [{m['minute']}] — {m['scorers']}"
        for m in MOCK_LIVE_SCORES
    )


def _mock_scorers() -> str:
    return "Golden Boot race (current):\n" + "\n".join(
        f"{i}. {s['player']} ({s['team']}) — {s['goals']} goals"
        for i, s in enumerate(MOCK_TOP_SCORERS, 1)
    )


def _mock_todays_matches() -> str:
    lines = [
        f"- LIVE [{m['minute']}]: {m['match']} {m['score']}" for m in MOCK_LIVE_SCORES
    ]
    lines += [
        f"- {r['kickoff']}: {r['match']} (not started)" for r in MOCK_FIXTURES_TODAY
    ]
    return "World Cup matches today:\n" + "\n".join(lines)


def _mock_results(match_date: str) -> str:
    d = match_date.strip() or "today"
    return f"World Cup results ({d}):\n" + "\n".join(
        f"- {r['home']} {r['hg']}-{r['ag']} {r['away']}" for r in MOCK_RESULTS
    )


# ── Live football-data.org fetchers ──────────────────────────────────────────
def _live_standings(group: str) -> str:
    data = _api_get(f"/competitions/{COMPETITION}/standings")
    want = group.strip().upper().replace("GROUP", "").strip()
    blocks: list[str] = []
    for entry in data.get("standings", []):
        if entry.get("type") != "TOTAL":
            continue
        g = (entry.get("group") or "").replace("GROUP_", "").replace("GROUP ", "").strip()
        if want and g and want != g:
            continue
        title = f"Group {g}" if g else (data.get("competition", {}).get("name", "Standings"))
        rows = ["Pos  Team            P  W  D  L  GD  Pts"]
        for r in entry.get("table", []):
            t = (r.get("team") or {}).get("name", "?")
            rows.append(
                f"{r.get('position', 0):<4} {t[:14]:<14} {r.get('playedGames', 0)}  "
                f"{r.get('won', 0)}  {r.get('draw', 0)}  {r.get('lost', 0)}  "
                f"{r.get('goalDifference', 0):>2}  {r.get('points', 0)}"
            )
        blocks.append(f"{title} (current standings):\n" + "\n".join(rows))
    if not blocks:
        return f"NO_DATA: no standings returned for group '{group}'."
    return "\n\n".join(blocks)


def _fmt_match(m: dict) -> str:
    home = (m.get("homeTeam") or {}).get("name", "TBD")
    away = (m.get("awayTeam") or {}).get("name", "TBD")
    when = (m.get("utcDate") or "")[:16].replace("T", " ") + " UTC"
    grp = (m.get("group") or "").replace("GROUP_", "Group ")
    tail = f" ({grp})" if grp else ""
    return f"- {when}: {home} vs {away}{tail}"


def _live_fixtures(when: str) -> str:
    if when.strip().lower() == "upcoming":
        data = _api_get(f"/competitions/{COMPETITION}/matches", {"status": "SCHEDULED"})
        matches = data.get("matches", [])[:10]
        header = "Upcoming World Cup fixtures:"
    else:
        today = date.today().isoformat()
        data = _api_get(
            f"/competitions/{COMPETITION}/matches", {"dateFrom": today, "dateTo": today}
        )
        matches = data.get("matches", [])
        header = f"World Cup fixtures for {today}:"
    if not matches:
        return "NO_DATA: no fixtures found for that window."
    return header + "\n" + "\n".join(_fmt_match(m) for m in matches)


def _live_live_scores() -> str:
    data = _api_get(f"/competitions/{COMPETITION}/matches", {"status": "LIVE"})
    matches = data.get("matches", [])
    if not matches:
        return "NO_LIVE_MATCHES: no World Cup matches are in progress right now."
    out = []
    for m in matches:
        home = (m.get("homeTeam") or {}).get("name", "?")
        away = (m.get("awayTeam") or {}).get("name", "?")
        ft = m.get("score", {}).get("fullTime", {})
        out.append(f"- {home} {ft.get('home', 0)}-{ft.get('away', 0)} {away} [{m.get('status')}]")
    return "Live now:\n" + "\n".join(out)


def _live_scorers() -> str:
    data = _api_get(f"/competitions/{COMPETITION}/scorers", {"limit": 10})
    scorers = data.get("scorers", [])
    if not scorers:
        return "NO_DATA: no top-scorer data available."
    out = []
    for i, s in enumerate(scorers, 1):
        p = (s.get("player") or {}).get("name", "?")
        t = (s.get("team") or {}).get("name", "?")
        out.append(f"{i}. {p} ({t}) — {s.get('goals', 0)} goals")
    return "Golden Boot race (current):\n" + "\n".join(out)


# ── Live API-Football fetchers (today's games + results) ─────────────────────
def _af_fixtures(match_date: str) -> list[dict]:
    return _af_get(
        "/fixtures",
        {"league": AF_LEAGUE, "season": AF_SEASON, "date": match_date},
    ).get("response", [])


def _af_todays_matches() -> str:
    today = date.today().isoformat()
    rows = _af_fixtures(today)
    if not rows:
        return f"NO_DATA: no World Cup matches scheduled for {today}."
    out = []
    for r in rows:
        home = r["teams"]["home"]["name"]
        away = r["teams"]["away"]["name"]
        short = r["fixture"]["status"]["short"]
        elapsed = r["fixture"]["status"].get("elapsed")
        gh, ga = r["goals"]["home"], r["goals"]["away"]
        if short == "NS":
            kick = (r["fixture"].get("date") or "")[11:16]
            out.append(f"- {kick} UTC: {home} vs {away} (not started)")
        elif short in ("FT", "AET", "PEN"):
            out.append(f"- FT: {home} {gh}-{ga} {away}")
        else:
            mins = f"{elapsed}'" if elapsed else short
            out.append(f"- LIVE {mins}: {home} {gh}-{ga} {away}")
    return f"World Cup matches today ({today}):\n" + "\n".join(out)


def _af_results(match_date: str) -> str:
    d = match_date.strip() or date.today().isoformat()
    rows = [
        r for r in _af_fixtures(d)
        if r["fixture"]["status"]["short"] in ("FT", "AET", "PEN")
    ]
    if not rows:
        return f"NO_DATA: no finished World Cup results for {d}."
    out = [
        f"- {r['teams']['home']['name']} {r['goals']['home']}-{r['goals']['away']} "
        f"{r['teams']['away']['name']}"
        for r in rows
    ]
    return f"World Cup results for {d}:\n" + "\n".join(out)


# ── MCP tools (try live football-data.org, fall back to sample data) ──────────
@mcp.tool()
def get_standings(group: str = "") -> str:
    """Get the CURRENT, LIVE FIFA World Cup group standings table (played, won,
    drawn, lost, goal difference and points as of right now). Use this for any
    question about the current standings, group tables, who is topping or
    leading a group, or qualification scenarios in the ongoing tournament.
    Optionally pass a single group letter (e.g. 'D') to return just that group;
    leave it empty to return all available groups."""
    if USE_REAL:
        try:
            return _note(_live_standings(group), sample=False)
        except Exception as exc:  # noqa: BLE001 - fall back to sample data
            return _note(_mock_standings(group), sample=True, err=str(exc)[:120])
    return _note(_mock_standings(group), sample=True)


@mcp.tool()
def get_fixtures(when: str = "today") -> str:
    """Get the FIFA World Cup match SCHEDULE / fixtures. Use this for questions
    about what matches are on today, upcoming games, kickoff times, or the
    schedule. Pass 'today' for today's matches or 'upcoming' for the next
    scheduled fixtures."""
    if USE_REAL:
        try:
            return _note(_live_fixtures(when), sample=False)
        except Exception as exc:  # noqa: BLE001 - fall back to sample data
            return _note(_mock_fixtures(when), sample=True, err=str(exc)[:120])
    return _note(_mock_fixtures(when), sample=True)


@mcp.tool()
def get_live_scores() -> str:
    """Get LIVE scores for FIFA World Cup matches currently in progress (current
    scoreline and status). Use this for questions about live scores, what the
    score is right now, or which matches are being played at this moment."""
    if USE_REAL:
        try:
            return _note(_live_live_scores(), sample=False)
        except Exception as exc:  # noqa: BLE001 - fall back to sample data
            return _note(_mock_live(), sample=True, err=str(exc)[:120])
    return _note(_mock_live(), sample=True)


@mcp.tool()
def get_top_scorers() -> str:
    """Get the CURRENT FIFA World Cup top scorers / golden boot race (players
    ranked by goals scored so far in the ongoing tournament). Use this for
    questions about who is the top scorer, the golden boot leader, or goal
    counts right now."""
    if USE_REAL:
        try:
            return _note(_live_scorers(), sample=False)
        except Exception as exc:  # noqa: BLE001 - fall back to sample data
            return _note(_mock_scorers(), sample=True, err=str(exc)[:120])
    return _note(_mock_scorers(), sample=True)


@mcp.tool()
def get_todays_matches() -> str:
    """Get TODAY'S FIFA World Cup matches with their current status and score:
    not-started kickoff times, live in-progress scores, and today's finished
    results. Use this for 'what games are on today', 'what's the score right
    now', or which matches are being played today. (Live source: API-Football.)"""
    if USE_AF:
        try:
            return _note(_af_todays_matches(), sample=False, live_label="API-Football live")
        except Exception as exc:  # noqa: BLE001 - fall back to sample data
            return _note(_mock_todays_matches(), sample=True, err=str(exc)[:120])
    return _note(_mock_todays_matches(), sample=True)


@mcp.tool()
def get_results(match_date: str = "") -> str:
    """Get FINAL FIFA World Cup match RESULTS for a given date (defaults to
    today). Pass a date as 'YYYY-MM-DD'. Use this for questions about results,
    final scores, or who won on a particular day. (Live source: API-Football.)"""
    if USE_AF:
        try:
            return _note(_af_results(match_date), sample=False, live_label="API-Football live")
        except Exception as exc:  # noqa: BLE001 - fall back to sample data
            return _note(_mock_results(match_date), sample=True, err=str(exc)[:120])
    return _note(_mock_results(match_date), sample=True)


if __name__ == "__main__":
    mcp.run(transport="stdio")
