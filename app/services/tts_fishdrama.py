"""Fish Audio Drama 3 TTS provider (local SGLang-Omni server, /v1/audio/speech).

Server: `sgl-omni serve --model-path /mnt/d/models/fishaudio/drama-3-int4`
(WSL2/Docker setup documented in docs/DECISIONS.md, 2026-10-19).
License: Fish Audio Community License v1.0 (non-commercial OK) — UI must keep
the "AI-generated voice" note.
"""
import threading

import httpx

from app.core.config import settings


class FishDramaProvider:
    """HTTP client to the local Drama 3 server. Requests are serialized with a
    lock (deterministic ordering for the voice pipeline; the server does its
    own concurrency). Any failure raises — tts.py handles the fallback chain.
    """

    def __init__(self):
        self._lock = threading.Lock()

    def _health_url(self) -> str:
        return settings.fish_tts_base_url.rstrip("/") + "/health"

    def _tts_url(self) -> str:
        return settings.fish_tts_base_url.rstrip("/") + "/v1/audio/speech"

    def available(self, timeout: float = 1.5) -> bool:
        """True only if the local server answers /health with 200."""
        try:
            r = httpx.get(self._health_url(), timeout=timeout)
            return r.status_code == 200
        except Exception:
            return False

    def synthesize_sync(self, text: str, language: str = "en",
                        voice: str | None = None, speed: float | None = None) -> bytes:
        """Text -> WAV bytes (PCM 44.1 kHz mono).

        voice/speed are accepted for TTSProvider-interface compatibility but
        ignored: Drama 3's API has no such parameters (only `input` plus the
        optional `references` cloning field, unused here).
        """
        with self._lock:
            r = httpx.post(
                self._tts_url(),
                json={"input": text},
                timeout=settings.fish_tts_timeout_s,
            )
        r.raise_for_status()
        return r.content


fishdrama_provider = FishDramaProvider()