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

    @staticmethod
    def audio_format(data: bytes) -> str:
        """WAV починається з RIFF, MP3 — з ID3 або sync-слова 0xFF."""
        if data[:4] == b"RIFF":
            return "wav"
        return "mp3"

    @staticmethod
    def mime_for(data: bytes) -> str:
        return "audio/wav" if TTSService.audio_format(data) == "wav" else "audio/mpeg"

    @staticmethod
    def detect_language(text: str) -> str:
        """Автовизначення мови озвучування: якщо в тексті переважає кирилиця →
        українська, інакше англійська. Щоб Mira озвучувала українську відповідь
        українським голосом, а англійську — англійським."""
        cyr = sum(1 for ch in text if "\u0400" <= ch <= "\u04FF")
        lat = sum(1 for ch in text if ch.isascii() and ch.isalpha())
        return "uk" if cyr > lat else "en"

    async def synthesize(self, text: str, language: str = "en",
                         voice: str | None = None, speed: float | None = None) -> bytes:
        """Повертає MP3 (edge) або WAV (piper/supertonic).
        voice/speed — тимчасовий override (тест голосу), без збереження."""
        from app.core import user_settings
        us = user_settings.load()
        provider = us.get("tts_provider") or settings.tts_provider
        voice = voice or us.get("supertonic_voice") or "F1"
        speed = speed or us.get("supertonic_speed") or 1.05
        # Кеш враховує провайдер/голос/швидкість — після зміни голосу
        # старі доріжки не віддаються.
        key = hashlib.sha1(
            f"{language}|{provider}|{voice}|{speed}|{text}".encode()
        ).hexdigest()
        cache_file = self._cache_dir / f"{key}.bin"
        if cache_file.exists():
            return cache_file.read_bytes()

        # Маршрут за мовою (UK-голос edge заблоковано 403, тому UK завжди Piper):
        # - українська → Piper uk_UA (офлайн)
        # - англійська → edge (онлайн, якість), запасний Piper en_US
        # provider=supertonic → один офлайн-рушій для uk і en (Agent-brief.MD).
        if provider == "supertonic":
            try:
                from app.services.tts_supertonic import supertonic_provider
                data = await asyncio.to_thread(
                    supertonic_provider.synthesize_sync, text, language,
                    voice=voice, speed=speed,
                )
            except Exception:
                # fallback: uk → piper, en → edge/piper
                if language.startswith("uk"):
                    data = await asyncio.to_thread(self._piper_sync, text, language)
                else:
                    try:
                        data = await self._edge(text, language)
                    except Exception:
                        data = await asyncio.to_thread(self._piper_sync, text, language)
        elif language.startswith("uk"):
            data = await asyncio.to_thread(self._piper_sync, text, language)
        elif provider == "piper":
            try:
                data = await asyncio.to_thread(self._piper_sync, text, language)
            except Exception:
                data = await self._edge(text, language)
        else:
            try:
                data = await self._edge(text, language)
            except Exception:
                data = await asyncio.to_thread(self._piper_sync, text, language)

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

    def _piper_sync(self, text: str, language: str = "en") -> bytes:
        # Офлайн-синтез через piper-tts. Для EN — PIPER_VOICE_EN (.onnx),
        # для UK окремого якісного офлайн-голосу поки немає, тому пробуємо
        # той самий EN-голос (вимова буде з акцентом, але звук буде).
        try:
            from piper import PiperVoice
        except ImportError as e:
            raise RuntimeError(
                "TTS_PROVIDER=piper, але piper-tts не встановлено: python -m pip install piper-tts"
            ) from e
        model = settings.piper_voice_en or r"D:\models\piper\en_US-lessac-medium.onnx"
        if language.startswith("uk"):
            model = (getattr(settings, "piper_voice_uk", "")
                     or r"D:\models\piper\uk_UA-ukrainian_tts-medium.onnx")
        voice = PiperVoice.load(model)
        # ВАЖЛИВО: phoneme_id_map у .onnx.json містить ЛИШЕ маленькі літери.
        # Великі (П, Я, М…) дають "Missing phoneme from id map" і калічать
        # вимову (звучить як беззмістовний набір слогів). Тому малим. +
        # прибираємо зайві пробіли/перенесення рядків.
        text = " ".join(text.split()).lower()
        import wave as _wave
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with _wave.open(tmp_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            os.unlink(tmp_path)


tts_service = TTSService()
