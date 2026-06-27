"""High-priority tests for the coach agent's system prompt guardrails.

These assert the persona/guardrail contract without building the agent (no LLM
or MCP needed): the prompt must keep football scoped to soccer, refuse
off-topic, protect PII, and cap answer length for cost.
"""

from __future__ import annotations

from app.agent import COACH_SYSTEM_PROMPT


def test_prompt_disambiguates_soccer_from_american_football():
    text = COACH_SYSTEM_PROMPT.lower()
    assert "association football" in text
    assert "american" in text and "nfl" in text


def test_prompt_lists_each_tool():
    assert "search_worldcup_knowledge" in COACH_SYSTEM_PROMPT
    assert "read_skill_file" in COACH_SYSTEM_PROMPT
    assert "get_standings" in COACH_SYSTEM_PROMPT


def test_prompt_has_greeting_and_refusal_rules():
    text = COACH_SYSTEM_PROMPT.lower()
    assert "greet" in text or "small talk" in text
    assert "refuse" in text


def test_prompt_protects_personal_information():
    text = COACH_SYSTEM_PROMPT.lower()
    assert "email" in text
    assert "phone" in text or "personal" in text


def test_prompt_caps_answer_length_for_cost():
    assert "150 words" in COACH_SYSTEM_PROMPT
