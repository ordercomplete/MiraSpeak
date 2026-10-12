import asyncio

from app.services import llm_service, stt_service, tts_service
from app.services.prompt import (
    build_system_prompt,
    language_directive,
    build_coach_system_prompt,
)


class PipelineService:
    """Повний цикл: аудіо → текст → LLM → текст+аудіо відповіді.

    Два режими:
    - tutor: англійський тьютор (відповідає мовою користувача, виправлення 📌).
    - coach: україномовний помічник-коуч (завжди українською), який час від часу
      дає короткий дрил «🎯 Repeat: <англ. фраза> — <переклад>» для тренування вимови.
    """

    async def voice_turn(
        self,
        audio_bytes: bytes,
        *,
        language: str = "auto",
        mode: str = "tutor",
        level: str = "B1",
        scenario: str = "free talk",
        drill_target: str | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        # 1) STT (CPU/GPU-bound → у потік, щоб не блокувати event loop)
        transcript = await asyncio.to_thread(
            stt_service.transcribe, audio_bytes, language
        )
        if not transcript:
            return {"ok": False, "error": "empty_transcript"}
        # 2) LLM у вибраному режимі
        return await self.process_text(
            transcript, mode=mode, level=level, scenario=scenario,
            drill_target=drill_target, history=history,
        )

    async def text_turn(
        self,
        message: str,
        *,
        mode: str = "tutor",
        level: str = "B1",
        scenario: str = "free talk",
        drill_target: str | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        return await self.process_text(
            message, mode=mode, level=level, scenario=scenario,
            drill_target=drill_target, history=history,
        )

    async def process_text(
        self,
        user_text: str,
        *,
        mode: str = "tutor",
        level: str = "B1",
        scenario: str = "free talk",
        drill_target: str | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        if mode == "coach":
            return await self._coach_turn(user_text, level, scenario, history, drill_target)
        return await self._tutor_turn(user_text, level, scenario, history)

    # ---------------- Тьютор (англійська, з виправленнями) ----------------
    async def _tutor_turn(self, user_text, level, scenario, history) -> dict:
        messages = [{"role": "system", "content": build_system_prompt(level, scenario)}]
        messages.extend(history or [])
        messages.append({"role": "system", "content": language_directive(user_text)})
        messages.append({"role": "user", "content": user_text})
        try:
            reply = await llm_service.chat(messages)
        except Exception as e:
            return {"ok": False, "error": f"llm_error: {e}", "transcript": user_text}

        spoken, correction = self._split_reply(reply)
        audio = b""
        if spoken:
            try:
                audio = await tts_service.synthesize(spoken, tts_service.detect_language(spoken))
            except Exception:
                audio = b""
        return {
            "ok": True,
            "transcript": user_text,
            "reply_text": reply,
            "reply_spoken": spoken,
            "correction": correction,
            "drill": None,
            "audio": audio,
            "drill_audio": b"",
        }

    # ---------------- Коуч (українська + дрили) ----------------
    async def _coach_turn(self, user_text, level, scenario, history, drill_target=None) -> dict:
        messages = [{"role": "system", "content": build_coach_system_prompt(level, scenario)}]
        messages.extend(history or [])
        user_content = user_text
        # Якщо це «перевірка» дрилу — інструктуємо коуча порівняти вимову зі зразком.
        if drill_target:
            user_content = (
                f"{user_text}\n\n"
                f"[SYSTEM NOTE: The learner just tried to repeat this English phrase: "
                f"\"{drill_target}\". Compare their attempt (the message above, likely "
                f"mangled by speech recognition) to the target. In Ukrainian, briefly "
                f"praise or gently correct the pronunciation, then continue the conversation. "
                f"Do NOT output a new 🎯 Repeat line this turn.]"
            )
        messages.append({"role": "user", "content": user_content})
        try:
            reply = await llm_service.chat(messages)
        except Exception as e:
            return {"ok": False, "error": f"llm_error: {e}", "transcript": user_text}

        spoken, drill_en, drill_uk = self._split_coach_reply(reply)
        audio = b""
        if spoken:
            try:
                audio = await tts_service.synthesize(spoken, "uk")
            except Exception:
                audio = b""
        drill_audio = b""
        if drill_en:
            try:
                drill_audio = await tts_service.synthesize(drill_en, "en")
            except Exception:
                drill_audio = b""
        return {
            "ok": True,
            "transcript": user_text,
            "reply_text": reply,
            "reply_spoken": spoken,
            "correction": "",
            "drill": {"en": drill_en, "uk": drill_uk} if drill_en else None,
            "audio": audio,
            "drill_audio": drill_audio,
        }

    # ---------------- Парсери відповіді ----------------
    @staticmethod
    def _split_reply(reply: str) -> tuple[str, str]:
        marker = "\n📌"
        if marker in reply:
            spoken, correction = reply.split(marker, 1)
            return spoken.strip(), ("📌" + correction).strip()
        return reply.strip(), ""

    @staticmethod
    def _split_coach_reply(reply: str) -> tuple[str, str, str]:
        """Відокремлює рядок «🎯 Repeat: …» від української частини відповіді.
        Повертає (український_текст, англійська_фраза_дрилу, переклад_дрилу)."""
        spoken_lines, drill_line = [], ""
        for ln in reply.split("\n"):
            if ln.strip().startswith("🎯"):
                drill_line = ln.strip()
            else:
                spoken_lines.append(ln)
        spoken = "\n".join(spoken_lines).strip()
        drill_en = drill_uk = ""
        if drill_line:
            body = drill_line
            for pref in ("🎯", "Repeat:", "repeat:", "Повтори:", "повтори:"):
                body = body.replace(pref, " ")
            for sep in ("—", "–", " - "):
                if sep in body:
                    drill_en, drill_uk = body.split(sep, 1)
                    break
            else:
                drill_en = body
            drill_en = drill_en.strip()
            drill_uk = drill_uk.strip()
        return spoken, drill_en, drill_uk


pipeline_service = PipelineService()

