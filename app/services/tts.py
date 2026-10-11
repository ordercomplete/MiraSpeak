import asyncio
import hashlib
import os
import tempfile

import edge_tts

from app.core.config import settings


class TTSService:
    """TTS: edge-tts (за замовчуванням, мережа) або Piper (локально, офлайн, EN)."""

    def __init__(self):
        self._cache_dir = settings.base_dir / "data" / "tts_cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _voice(self, language: str) -> str:
        return settings.tts_voice_en if language.startswith("en") else settings.tts_voice_uk

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        key = hashlib.sha1(f"{language}|{text}".encode()).hexdigest()
        cache_file = self._cache_dir / f"{key}.mp3"
        if cache_file.exists():
            return cache_file.read_bytes()

        if settings.tts_provider == "piper":
            data = await asyncio.to_thread(self._piper_sync, text)
        else:
            data = await self._edge(text, language)

        cache_file.write_bytes(data)
        return data

    async def _edge(self, text: str, language: str) -> bytes:
        communicate = edge_tts.Communicate(text, self._voice(language))
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            await communicate.save(tmp_path)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            os.unlink(tmp_path)

    def _piper_sync(self, text: str) -> bytes:
        # Офлайн-опція: pip install piper-tts + завантажений голос (PIPER_VOICE_EN)
        try:
            from piper import PiperVoice
        except ImportError as e:
            raise RuntimeError(
                "TTS_PROVIDER=piper, але piper-tts не встановлено: python -m pip install piper-tts"
            ) from e
        if not settings.piper_voice_en:
            raise RuntimeError("TTS_PROVIDER=piper вимагає PIPER_VOICE_EN (шлях до .onnx голосу)")
        voice = PiperVoice.load(settings.piper_voice_en)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            voice.synthesize(text, tmp_path)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            os.unlink(tmp_path)


tts_service = TTSService()
