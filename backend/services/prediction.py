"""World Cup champion prediction — a transparent heuristic for the Predict game.

Combines settled history (how many World Cups a nation has won) with current
2026 form (goals scored this tournament + the team of the golden-boot leader)
into a single explainable score. Live form comes from the football service;
when no live data is available it falls back to a baked-in sample so the game
still works offline.
"""

from __future__ import annotations

import re

# Settled history fallback — World Cup titles per nation (1930–2022). Used when
# the live Wikidata lookup is unavailable (offline / network error).
FALLBACK_TITLES: dict[str, int] = {
    "Brazil": 5,
    "Germany": 4,
    "Italy": 4,
    "Argentina": 3,
    "France": 2,
    "Uruguay": 2,
    "England": 1,
    "Spain": 1,
}

# Wikidata SPARQL: count World Cup wins per national team. Each edition is a
# "sports season of" (P3450) the FIFA World Cup (Q19317) and names its winner
# via P1346. Wikidata already merges West Germany into Germany.
_WIKIDATA_SPARQL = """
SELECT ?teamLabel (COUNT(?edition) AS ?titles) WHERE {
  ?edition wdt:P3450 wd:Q19317 ; wdt:P1346 ?team .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?teamLabel
ORDER BY DESC(?titles)
"""

# Cached titles for the process lifetime (settled data — fetched at most once).
_titles_cache: dict[str, int] | None = None


def _country_from_team(label: str) -> str:
    """'Brazil men's national football team' -> 'Brazil'."""
    return re.sub(
        r"\s+(men's\s+)?national\s+(association\s+)?football\s+team$",
        "",
        label,
        flags=re.I,
    ).strip()


def _fetch_titles_from_wikidata() -> dict[str, int]:
    """Live World Cup title counts per country from Wikidata; {} on any error."""
    try:
        import httpx

        resp = httpx.get(
            "https://query.wikidata.org/sparql",
            params={"query": _WIKIDATA_SPARQL, "format": "json"},
            headers={"User-Agent": "GoldenGoal/0.1 (World Cup demo)"},
            timeout=15.0,
        )
        resp.raise_for_status()
        titles: dict[str, int] = {}
        for row in resp.json().get("results", {}).get("bindings", []):
            country = _country_from_team(row["teamLabel"]["value"])
            count = int(row["titles"]["value"])
            if country:
                titles[country] = titles.get(country, 0) + count
        return titles
    except Exception:  # noqa: BLE001 - degrade to the static fallback
        return {}


def get_titles() -> dict[str, int]:
    """World Cup titles per nation — live from Wikidata, cached, with fallback."""
    global _titles_cache
    if _titles_cache is None:
        _titles_cache = _fetch_titles_from_wikidata() or dict(FALLBACK_TITLES)
    return _titles_cache

# Offline fallback for current-tournament form (goals scored + star striker) so
# the Predict game still works without live API keys configured.
SAMPLE_FORM: dict[str, dict] = {
    "Argentina": {"goals": 9, "star": "Lautaro Martínez", "star_goals": 4},
    "France": {"goals": 8, "star": "Kylian Mbappé", "star_goals": 5},
    "Brazil": {"goals": 8, "star": "Vinícius Jr", "star_goals": 4},
    "Spain": {"goals": 7, "star": "Lamine Yamal", "star_goals": 3},
    "England": {"goals": 6, "star": "Harry Kane", "star_goals": 4},
    "Portugal": {"goals": 6, "star": "Bernardo Silva", "star_goals": 3},
    "Germany": {"goals": 5, "star": "Florian Wirtz", "star_goals": 2},
    "Netherlands": {"goals": 5, "star": "Cody Gakpo", "star_goals": 3},
}

# Heuristic weights — titles reward pedigree, goals reward current attack, and
# the golden-boot striker adds a star bonus.
W_TITLE = 1.5
W_GOALS = 1.0
W_STAR = 1.2

# Country-name aliases → canonical name used in the tables above.
_ALIASES = {
    "united states": "USA",
    "usa": "USA",
    "us": "USA",
    "holland": "Netherlands",
    "the netherlands": "Netherlands",
    "korea": "South Korea",
    "south korea": "South Korea",
}


def _flag(team: str) -> str:
    """Country flag emoji, reusing the football service's lookup."""
    try:
        from services.football import _flag as fb_flag

        return fb_flag(team)
    except Exception:  # noqa: BLE001 - flag is cosmetic
        return "🏳️"


def _live_form() -> dict[str, dict]:
    """Best-effort current form from live data; returns {} if unavailable."""
    form: dict[str, dict] = {}
    try:
        from services.football import get_scorers_data, get_standings_data

        standings = get_standings_data()
        if standings.get("source") != "live":
            return {}
        for group in standings.get("groups", []):
            for row in group.get("table", []):
                team = row.get("team")
                if team:
                    form.setdefault(team, {})["goals"] = row.get("gf", 0) or 0

        scorers = get_scorers_data()
        if scorers.get("source") == "live":
            for s in scorers.get("scorers", []):
                team = s.get("team")
                if team and team in form and "star_goals" not in form[team]:
                    form[team]["star"] = s.get("player")
                    form[team]["star_goals"] = s.get("goals", 0) or 0
    except Exception:  # noqa: BLE001 - degrade to sample on any error
        return {}
    return form


def _score(name: str, form: dict[str, dict], titles_map: dict[str, int]) -> tuple[float, dict]:
    """Return (score, factor-breakdown) for one nation."""
    titles = titles_map.get(name, 0)
    f = form.get(name, {})
    goals = f.get("goals", 0)
    star = f.get("star")
    star_goals = f.get("star_goals", 0)
    score = W_TITLE * titles + W_GOALS * goals + W_STAR * star_goals
    return score, {
        "team": name,
        "flag": _flag(name),
        "titles": titles,
        "goals": goals,
        "star": star,
        "star_goals": star_goals,
        "score": round(score, 1),
    }


def predict_champion() -> dict:
    """Compute the agent's predicted champion + a top-5 leaderboard."""
    live = _live_form()
    form = live if live else SAMPLE_FORM
    source = "live" if live else "sample"
    titles_map = get_titles()

    candidates = set(titles_map) | set(form)
    ranked = [_score(name, form, titles_map)[1] for name in candidates]
    ranked.sort(key=lambda r: r["score"], reverse=True)

    predicted = ranked[0]
    return {
        "source": source,
        "predicted": predicted["team"],
        "factors": predicted,
        "leaderboard": ranked[:5],
    }


def _match_guess(guess: str, names: list[str]) -> str | None:
    """Resolve a free-text guess to a known nation, or None if no match."""
    g = (guess or "").strip().lower()
    if not g:
        return None
    pool = {n.lower(): n for n in names}
    alias = _ALIASES.get(g)
    if alias and alias.lower() in pool:
        return pool[alias.lower()]
    if g in pool:
        return pool[g]
    for low, original in pool.items():
        if g in low or low in g:
            return original
    return None


def play(guess: str) -> dict:
    """Compare the user's guess to the agent's pick and report win/lose."""
    result = predict_champion()
    predicted = result["predicted"]
    known = list({*get_titles(), *(r["team"] for r in result["leaderboard"])})
    matched = _match_guess(guess, known)
    win = matched is not None and matched == predicted

    factors = result["factors"]
    bits = [f"{factors['titles']} World Cup title(s)"]
    if factors.get("goals"):
        bits.append(f"{factors['goals']} goals so far in 2026")
    if factors.get("star") and factors.get("star_goals"):
        bits.append(f"{factors['star']} firing ({factors['star_goals']} goals)")
    why = ", ".join(bits)

    if win:
        reasoning = f"🏆 Spot on! I also back {predicted} — {why}. You win!"
    elif matched:
        reasoning = (
            f"Close! You picked {matched}, but my model favours {predicted} — {why}. "
            "Better luck next time!"
        )
    else:
        reasoning = (
            f"I couldn't match '{guess}' to a contender. My pick is {predicted} — "
            f"{why}."
        )

    return {
        "guess": guess,
        "matched": matched,
        "predicted": predicted,
        "win": win,
        "reasoning": reasoning,
        "factors": factors,
        "leaderboard": result["leaderboard"],
        "source": result["source"],
    }
