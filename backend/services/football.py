"""Structured football data for the Standings & Schedule UI views.

Mirrors the MCP football tools but returns **structured JSON** (not LLM text) so
the frontend can render tables and fixture cards. Calls football-data.org for
standings and API-Football for the schedule; when no API key is configured it
reports ``source: "sample"`` and returns empty data so the frontend falls back
to its built-in sample dataset.
"""

from __future__ import annotations

import os
import re
from datetime import date, timedelta

import httpx

# football-data.org (standings) — competition WC.
FD_BASE = "https://api.football-data.org/v4"
FD_COMP = os.getenv("FOOTBALL_COMPETITION", "WC")
FD_KEY = os.getenv("FOOTBALL_DATA_KEY", "").strip()
USE_FD = bool(FD_KEY) and not FD_KEY.lower().startswith("your")

# API-Football (schedule / results) — World Cup is league 1.
AF_BASE = "https://v3.football.api-sports.io"
AF_KEY = os.getenv("API_FOOTBALL_KEY", "").strip()
AF_LEAGUE = os.getenv("API_FOOTBALL_LEAGUE", "1")
AF_SEASON = os.getenv("API_FOOTBALL_SEASON", "2026")
USE_AF = bool(AF_KEY) and not AF_KEY.lower().startswith("your")

# How many days of fixtures to pull (today + N-1 days).
SCHEDULE_DAYS = 5

# Best-effort country → flag emoji (falls back to a neutral flag).
_FLAGS = {
    "Algeria": "🇩🇿", "Argentina": "🇦🇷", "Australia": "🇦🇺", "Austria": "🇦🇹",
    "Belgium": "🇧🇪", "Bosnia-Herzegovina": "🇧🇦", "Brazil": "🇧🇷",
    "Cameroon": "🇨🇲", "Canada": "🇨🇦", "Cape Verde": "🇨🇻", "Cape Verde Islands": "🇨🇻",
    "Colombia": "🇨🇴", "Congo DR": "🇨🇩", "Croatia": "🇭🇷", "Curaçao": "🇨🇼",
    "Czechia": "🇨🇿", "Denmark": "🇩🇰", "Ecuador": "🇪🇨", "Egypt": "🇪🇬",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "France": "🇫🇷", "Germany": "🇩🇪", "Ghana": "🇬🇭",
    "Haiti": "🇭🇹", "Iran": "🇮🇷", "Iraq": "🇮🇶", "Italy": "🇮🇹",
    "Ivory Coast": "🇨🇮", "Japan": "🇯🇵", "Jordan": "🇯🇴", "Mexico": "🇲🇽",
    "Morocco": "🇲🇦", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nigeria": "🇳🇬",
    "Norway": "🇳🇴", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Peru": "🇵🇪",
    "Poland": "🇵🇱", "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Saudi Arabia": "🇸🇦",
    "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Senegal": "🇸🇳", "South Africa": "🇿🇦", "South Korea": "🇰🇷",
    "Spain": "🇪🇸", "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Tunisia": "🇹🇳",
    "Turkey": "🇹🇷", "USA": "🇺🇸", "United States": "🇺🇸", "Uruguay": "🇺🇾",
    "Uzbekistan": "🇺🇿", "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
}


def _flag(name: str) -> str:
    return _FLAGS.get(name, "🏳️")


def get_standings_data() -> dict:
    """Return {source, groups:[{name, table:[TeamRow]}]} from football-data.org."""
    if not USE_FD:
        return {"source": "sample", "groups": []}
    resp = httpx.get(
        f"{FD_BASE}/competitions/{FD_COMP}/standings",
        headers={"X-Auth-Token": FD_KEY},
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    groups: list[dict] = []
    for entry in data.get("standings", []):
        if entry.get("type") != "TOTAL":
            continue
        g = re.sub(r"group[_\s]*", "", entry.get("group") or "", flags=re.I).strip()
        table = []
        for r in entry.get("table", []):
            name = (r.get("team") or {}).get("name", "?")
            table.append(
                {
                    "team": name,
                    "flag": _flag(name),
                    "played": r.get("playedGames", 0),
                    "won": r.get("won", 0),
                    "drawn": r.get("draw", 0),
                    "lost": r.get("lost", 0),
                    "gf": r.get("goalsFor", 0),
                    "ga": r.get("goalsAgainst", 0),
                    "points": r.get("points", 0),
                }
            )
        groups.append({"name": g or "—", "table": table})
    return {"source": "live", "groups": groups}


def _af_status(short: str) -> str:
    if short in ("1H", "2H", "HT", "ET", "P", "BT", "LIVE"):
        return "LIVE"
    if short in ("FT", "AET", "PEN"):
        return "FINISHED"
    return "SCHEDULED"


def _fd_status(status: str) -> str:
    if status in ("IN_PLAY", "PAUSED", "SUSPENDED"):
        return "LIVE"
    if status in ("FINISHED", "AWARDED"):
        return "FINISHED"
    return "SCHEDULED"


def _fd_stage(stage: str) -> str:
    return (stage or "GROUP_STAGE").replace("_", " ").title()


def get_schedule_data() -> dict:
    """Return {source, fixtures:[Fixture]} from football-data.org over a window.

    Uses the same provider/key as standings (which has 2026 World Cup access),
    pulling matches from today through today + SCHEDULE_DAYS.
    """
    if not USE_FD:
        return {"source": "sample", "fixtures": []}
    today = date.today()
    # Start a day early in UTC so we don't miss matches that fall on the
    # viewer's local "today" but land on the previous UTC date; the frontend
    # filters to local-today onwards.
    start = today - timedelta(days=1)
    end = today + timedelta(days=SCHEDULE_DAYS)
    resp = httpx.get(
        f"{FD_BASE}/competitions/{FD_COMP}/matches",
        headers={"X-Auth-Token": FD_KEY},
        params={"dateFrom": start.isoformat(), "dateTo": end.isoformat()},
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    fixtures: list[dict] = []
    for m in data.get("matches", []):
        status = _fd_status(m.get("status", ""))
        home = (m.get("homeTeam") or {}).get("name") or "TBD"
        away = (m.get("awayTeam") or {}).get("name") or "TBD"
        utc = m.get("utcDate") or ""
        group = (m.get("group") or "")
        group = group.replace("GROUP_", "").strip() or None
        fixture = {
            "id": m.get("id"),
            "date": utc[:10],
            "time": utc[11:16],
            "kickoff": utc,
            "stage": _fd_stage(m.get("stage", "")),
            "group": group,
            "home": {"team": home, "flag": _flag(home)},
            "away": {"team": away, "flag": _flag(away)},
            "venue": m.get("venue") or "",
            "status": status,
        }
        if status in ("LIVE", "FINISHED"):
            ft = (m.get("score") or {}).get("fullTime") or {}
            fixture["score"] = {
                "home": ft.get("home") or 0,
                "away": ft.get("away") or 0,
            }
        fixtures.append(fixture)
    return {"source": "live", "fixtures": fixtures}


def get_scorers_data() -> dict:
    """Return {source, scorers:[{player, team, goals, flag}]} from football-data.org.

    Used by the champion-prediction heuristic to credit each team's golden-boot
    striker. Degrades to ``source: "sample"`` with no key configured.
    """
    if not USE_FD:
        return {"source": "sample", "scorers": []}
    resp = httpx.get(
        f"{FD_BASE}/competitions/{FD_COMP}/scorers",
        headers={"X-Auth-Token": FD_KEY},
        params={"limit": 10},
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    scorers: list[dict] = []
    for s in data.get("scorers", []):
        player = (s.get("player") or {}).get("name", "?")
        team = (s.get("team") or {}).get("name", "?")
        scorers.append(
            {
                "player": player,
                "team": team,
                "goals": s.get("goals", 0) or 0,
                "flag": _flag(team),
            }
        )
    return {"source": "live", "scorers": scorers}

