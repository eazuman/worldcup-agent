"""High-priority unit tests for the Predict game heuristic.

These cover the pure, deterministic logic (guess matching, scoring, ranking,
win/lose) without any network calls: the Wikidata title lookup is short-circuited
by seeding the module cache and live form is forced off via monkeypatch.
"""

from __future__ import annotations

import pytest

from services import prediction


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Force offline, deterministic data: fixed titles + no live form."""
    monkeypatch.setattr(prediction, "_titles_cache", dict(prediction.FALLBACK_TITLES))
    monkeypatch.setattr(prediction, "_live_form", lambda: {})


def test_match_guess_alias_partial_and_none():
    names = ["USA", "Netherlands", "Brazil"]
    assert prediction._match_guess("holland", names) == "Netherlands"
    assert prediction._match_guess("united states", names) == "USA"
    assert prediction._match_guess("BRAZIL", names) == "Brazil"
    assert prediction._match_guess("Atlantis", names) is None


def test_score_applies_weights():
    score, factors = prediction._score(
        "Brazil", {"Brazil": {"goals": 4, "star_goals": 3}}, {"Brazil": 5}
    )
    expected = prediction.W_TITLE * 5 + prediction.W_GOALS * 4 + prediction.W_STAR * 3
    assert score == pytest.approx(expected)
    assert factors["team"] == "Brazil"


def test_predict_champion_ranks_top_five():
    result = prediction.predict_champion()
    scores = [r["score"] for r in result["leaderboard"]]
    assert len(result["leaderboard"]) == 5
    assert scores == sorted(scores, reverse=True)
    assert result["predicted"] == result["leaderboard"][0]["team"]


def test_play_win_and_lose():
    predicted = prediction.predict_champion()["predicted"]
    assert prediction.play(predicted)["win"] is True

    other = "France" if predicted != "France" else "Brazil"
    lost = prediction.play(other)
    assert lost["win"] is False
    assert lost["matched"] == other
