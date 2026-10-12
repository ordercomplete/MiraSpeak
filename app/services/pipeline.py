import asyncio

from app.services import llm_service, stt_service, tts_service
from app.services.prompt import build_system_prompt


class PipelineService:
    """Повний цикл: аудіо → текст → LLM → текст+аудіо відповіді."""

    async def voice_turn(
        self,
        audio_bytes: bytes,
        *,
        language: str = "en",
        level: str = "B1",
        scenario: str = "free talk",
        history: list[dict] | None = None,
    ) -> dict:
        # 1) STT (CPU/GPU-bound → у потік, щоб не блокувати event loop)
        transcript = await asyncio.to_thread(
            stt_service.transcribe, audio_bytes, language
        )
        if not transcript:
            return {"ok": False, "error": "empty_transcript"}

        # 2) LLM
        messages = [{"role": "system", "content": build_system_prompt(level, scenario)}]
        messages.extend(history or [])
        messages.append({"role": "user", "content": transcript})
        try:
            reply = await llm_service.chat(messages)
        except Exception as e:
            return {"ok": False, "error": f"llm_error: {e}", "transcript": transcript}

        # 3) TTS — озвучуємо лише англійську частину відповіді (частину з 📌 не озвучуємо)
        spoken_part, correction_part = self._split_reply(reply)
        audio_out = b""
        if spoken_part:
            try:
                audio_out = await tts_service.synthesize(spoken_part, "en")
            except Exception:
                audio_out = b""  # немає мережі → показуємо текст без голосу

        return {
            "ok": True,
            "transcript": transcript,
            "reply_text": reply,
            "reply_spoken": spoken_part,
            "correction": correction_part,
            "audio": audio_out,
        }

    @staticmethod
    def _split_reply(reply: str) -> tuple[str, str]:
        marker = "\n📌"
        if marker in reply:
            spoken, correction = reply.split(marker, 1)
            return spoken.strip(), ("📌" + correction).strip()
        return reply.strip(), ""


pipeline_service = PipelineService()
