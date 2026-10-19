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
                        voice: str | None = None, speed: float | None = None,
                        mode: str = "tutor") -> bytes:
        """Text -> WAV bytes (PCM 44.1 kHz mono).

        voice = mode name ("tutor" | "coach" | "mixed"): clones that mode's
        fixed reference voice so the timbre stays stable across turns.
        Unknown voice -> no reference (random timbre, previous behaviour).
        speed is accepted for TTSProvider-interface compatibility but ignored:
        Drama 3's API has no such parameter.
        """
        payload: dict = {"input": text}
        reference = self._mode_reference(mode if voice is None else voice)
        if reference is not None:
            audio_path, ref_text = reference
            payload["references"] = [{"audio_path": audio_path, "text": ref_text}]
        with self._lock:
            r = httpx.post(
                self._tts_url(),
                json=payload,
                timeout=settings.fish_tts_timeout_s,
            )
        r.raise_for_status()
        return r.content

    @staticmethod
    def _mode_reference(voice: str):
        """(audio_path, transcript) for a mode, or None if unknown/missing.

        audio_path is container-visible: the Windows D: drive is mounted into
        the server container at /mnt/d. Config value wins; readable local file
        is required.
        """
        try:
            entry = settings.fish_tts_mode_voices.get(str(voice), "")
        except Exception:
            return None
        if "|" not in entry:
            return None
        fname, ref_text = entry.split("|", 1)
        # NOTE: D: drive layout is deployment-specific; the path is sent to
        # the TTS server, never to the cloud (localhost only, offline-first).
        host_path = settings.fish_voice_base_dir.rstrip("\\/") + "\\" + fname
        import os
        if not os.path.isfile(host_path):
            return None
        container_path = "file://" + host_path.replace("\\", "/").replace("D:/", "/mnt/d/")
        return container_path, ref_text.strip()


fishdrama_provider = FishDramaProvider()