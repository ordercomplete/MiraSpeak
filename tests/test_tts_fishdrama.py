"""Tests for the Fish Audio Drama 3 provider (no real network, no real server).

Network is never touched: URLs point at a closed local port and httpx calls
are mocked. See docs/plans/tts-drama3-fishaudio.md (Крок 6).
"""
import asyncio

import pytest

from app.core.config import settings


# A port with nothing listening: connection refused instantly, no packets out.
CLOSED_URL = "http://127.0.0.1:9"


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setattr(settings, "fish_tts_base_url", CLOSED_URL)
    from app.services.tts_fishdrama import FishDramaProvider
    return FishDramaProvider()


def test_available_false_when_server_down(provider):
    assert provider.available(timeout=0.5) is False


def test_synthesize_raises_when_server_down(provider):
    with pytest.raises(Exception):
        provider.synthesize_sync("Hello", "en")


def test_payload_and_response_mocked(provider, monkeypatch):
    """Payload is {"input": text}; response bytes pass through unchanged."""
    import app.services.tts_fishdrama as mod

    captured = {}

    class FakeResp:
        status_code = 200
        content = b"RIFF....fake-wav"

        def raise_for_status(self):
            return None

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResp()

    monkeypatch.setattr(mod.httpx, "post", fake_post)
    data = provider.synthesize_sync("Привіт, світе!", "uk")
    assert data == b"RIFF....fake-wav"
    assert captured["json"] == {"input": "Привіт, світе!"}
    assert captured["url"] == CLOSED_URL + "/v1/audio/speech"
    assert captured["timeout"] == settings.fish_tts_timeout_s


def test_tts_service_falls_back_when_fishdrama_down(monkeypatch, tmp_path):
    """provider=fishdrama + dead server -> piper/edge fallback still returns audio."""
    monkeypatch.setattr(settings, "fish_tts_base_url", CLOSED_URL)

    from app.core import user_settings
    monkeypatch.setattr(user_settings, "load", lambda: {
        "tts_provider": "fishdrama", "supertonic_voice": "F1", "supertonic_speed": 1.05,
    })

    from app.services.tts import tts_service
    # keep the real cache dir clean: write test artifacts into tmp
    monkeypatch.setattr(tts_service, "_cache_dir", tmp_path / "tts_cache")
    (tmp_path / "tts_cache").mkdir(parents=True, exist_ok=True)

    async def fake_edge(text, language):
        return b"RIFF....edge"

    def fake_piper(text, language="en"):
        return b"RIFF....piper"

    monkeypatch.setattr(tts_service, "_edge", fake_edge)
    monkeypatch.setattr(tts_service, "_piper_sync", fake_piper)

    # uk -> piper fallback, en -> edge fallback
    out_uk = asyncio.run(tts_service.synthesize("Привіт", "uk"))
    out_en = asyncio.run(tts_service.synthesize("Hello", "en"))
    assert out_uk == b"RIFF....piper"
    assert out_en == b"RIFF....edge"


def test_settings_providers_include_fishdrama():
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).get("/api/settings")
    assert r.status_code == 200
    assert "fishdrama" in r.json()["providers"]


def test_settings_reject_unknown_provider():
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).post("/api/settings", json={"tts_provider": "nope"})
    assert r.status_code == 422
