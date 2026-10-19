"""Supertonic 3 TTS provider (offline, ONNX, uk + en in one engine).

Ref: Agent-brief.MD section 1. Weights: D:\\models\\tts\\supertonic-3
(SHA-256 in models/MANIFEST.json), license: BigScience OpenRAIL-M —
UI must show an "AI-generated voice" note.
"""
import io
import threading
import wave

from app.core.config import settings


class SupertonicProvider:
    """Lazy-loaded Supertonic 3 engine. Thread-safe: one TTS instance + lock
    (onnxruntime sessions are not safe to call concurrently from many threads)."""

    def __init__(self):
        self._tts = None
        self._voices: dict = {}
        self._lock = threading.Lock()

    def _ensure(self):
        if self._tts is None:
            import supertonic as st
            self._tts = st.TTS(
                model=settings.supertonic_model,
                model_dir=settings.supertonic_model_dir,
                auto_download=False,          # offline-first: weights pre-downloaded
            )
        return self._tts

    def _get_voice(self, voice: str):
        tts = self._ensure()
        if voice not in self._voices:
            self._voices[voice] = tts.get_voice_style(voice)
        return self._voices[voice]

    @staticmethod
    def available() -> bool:
        try:
            import supertonic  # noqa: F401
            return True
        except ImportError:
            return False

    def synthesize_sync(self, text: str, language: str = "en",
                        voice: str | None = None, speed: float | None = None) -> bytes:
        """Text -> WAV bytes (44.1 kHz). language: 'uk' | 'en'.
        voice: style name (F1-F5/M1-M5); speed: 0.5-2.0 (None = settings)."""
        tts = self._ensure()
        voice_style = self._get_voice(voice or settings.supertonic_voice)
        lang = "uk" if str(language).lower().startswith("uk") else "en"
        spd = speed if speed else settings.supertonic_speed
        with self._lock:
            wav, _dur = tts.synthesize(
                text,
                voice_style=voice_style,
                speed=spd,
                lang=lang,
            )
        # wav: np.ndarray shape (1, N) float in [-1, 1] -> 16-bit PCM WAV bytes
        import numpy as np
        pcm = np.clip(wav[0] if wav.ndim == 2 else wav, -1.0, 1.0)
        pcm = (pcm * 32767.0).astype("<i2")
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(pcm.tobytes())
        return buf.getvalue()


supertonic_provider = SupertonicProvider()
