"""High-priority API tests for the FastAPI app.

Covers the SSE/stream helpers and request validation at the boundary. The
TestClient is used without a lifespan context so the startup corpus ingest does
not run — these tests stay fast and offline (no Gemini key, no live data).
"""

from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import _chunk_text, _sse, app

client = TestClient(app)


def test_sse_frames_are_valid_json_lines():
    frame = _sse({"type": "token", "content": "hi"})
    assert frame.startswith("data: ")
    assert frame.endswith("\n\n")
    assert '"type": "token"' in frame


def test_chunk_text_handles_str_and_parts():
    assert _chunk_text(SimpleNamespace(content="hello")) == "hello"
    parts = SimpleNamespace(content=[{"text": "a"}, "b", {"notext": 1}])
    assert _chunk_text(parts) == "ab"
    assert _chunk_text(SimpleNamespace(content=None)) == ""


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "chunks_indexed" in body


def test_agent_chat_requires_question():
    assert client.post("/agent/chat", json={}).status_code == 422
    assert client.post("/agent/chat", json={"question": ""}).status_code == 422


def test_predict_play_validates_guess_length():
    assert client.post("/predict/play", json={"guess": ""}).status_code == 422
    assert client.post("/predict/play", json={"guess": "x" * 61}).status_code == 422
