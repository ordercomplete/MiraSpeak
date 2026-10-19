from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.core import db
from app.core import user_settings
from app.core.config import settings
from app.services import curriculum
from app.services.pipeline import pipeline_service
from app.services.prompt import (
    available_levels,
    available_scenarios,
    available_target_languages,
    CEFR_LEVELS,
    SCENARIOS,
)

router = APIRouter(prefix="/api")


class TextTurnRequest(BaseModel):
    message: str
    language: str = "en"
    mode: str = "tutor"
    level: str = "B1"
    scenario: str = "free talk"
    target_lang: str = "en"
    history: list[dict] = []
    session_id: int = 0


@router.post("/voice")
async def voice_turn(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    mode: str = Form("tutor"),
    level: str = Form("B1"),
    scenario: str = Form("free talk"),
    target_lang: str = Form("en"),
    drill_target: str = Form(""),
    session_id: int = Form(0),
):
    """Голосовий цикл: multipart аудіофайл (webm/wav/mp3) → JSON з відповіддю + base64 mp3."""
    raw = await audio.read()
    if not raw:
        raise HTTPException(status_code=400, detail="порожній аудіофайл")
    result = await pipeline_service.voice_turn(
        raw, language=language, mode=mode, level=level, scenario=scenario,
        drill_target=drill_target or None,
        target_lang=target_lang,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=422, detail=result.get("error"))
    audio_bytes = result.pop("audio", b"")
    drill_audio = result.pop("drill_audio", b"")
    # Автозбереження кожного чату: якщо фронт не передав session_id —
    # заводимо/перевикористовуємо сесію самі, хід зберігається завжди.
    db.init_db()
    sid = session_id or db.ensure_open_session(level, scenario)
    db.add_message(sid, "user", result.get("transcript", ""))
    db.add_message(sid, "assistant", result.get("reply_text", ""), result.get("correction", ""))
    return {
        **result,
        "session_id": sid,
        "audio_b64": _b64(audio_bytes),
        "drill_audio_b64": _b64(drill_audio),
    }


@router.post("/text")
async def text_turn(req: TextTurnRequest):
    """Текстовий цикл (без мікрофона) — для тестів і швидкого чату."""
    result = await pipeline_service.text_turn(
        req.message, mode=req.mode, level=req.level, scenario=req.scenario,
        target_lang=req.target_lang, history=req.history
    )
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result.get("error"))
    audio = result.pop("audio", b"")
    drill_audio = result.pop("drill_audio", b"")
    db.init_db()
    sid = req.session_id or db.ensure_open_session(req.level, req.scenario)
    db.add_message(sid, "user", req.message)
    db.add_message(sid, "assistant", result.get("reply_text", ""), result.get("correction", ""))
    return {
        **result,
        "session_id": sid,
        "audio_b64": _b64(audio),
        "drill_audio_b64": _b64(drill_audio),
    }


@router.get("/voice/sample")
async def voice_sample():
    """Демо-голос тьютора (для екрана привітання)."""
    from app.services import tts_service
    audio = await tts_service.synthesize("Hi! I'm Mira, your English tutor. Let's talk!", "en")
    return Response(content=audio, media_type="audio/mpeg")


class TtsRequest(BaseModel):
    text: str
    lang: str = "en"


@router.post("/tts")
async def tts(req: TtsRequest):
    """Озвучити довільний текст (лексика/фрази у картках навчання)."""
    from app.services import tts_service
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="порожній текст")
    try:
        audio = await tts_service.synthesize(text, req.lang)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"tts_error: {e}")
    if not audio:
        raise HTTPException(status_code=502, detail="tts_unavailable")
    return {"audio_b64": _b64(audio)}


@router.get("/meta")
async def meta():
    """Рівні, сценарії та поточні налаштування — для UI."""
    return {
        "levels": available_levels(),
        "scenarios": available_scenarios(),
        "target_languages": available_target_languages(),
        "profile": settings.model_profile,
        "llm_provider": settings.llm_provider,
        "tts_provider": settings.tts_provider,
    }


@router.get("/sessions")
async def list_sessions(limit: int = 20):
    """Історія чатів: останні сесії з кількістю реплік (для екрана «Історія»)."""
    db.init_db()
    return {"sessions": db.recent_sessions(limit)}


@router.get("/sessions/{session_id}")
async def session_messages(session_id: int, limit: int = 100):
    """Репліки одного чату (для перегляду/продовження історії)."""
    db.init_db()
    return {"session_id": session_id, "messages": db.get_history(session_id, limit)}


@router.post("/session")
async def new_session(level: str = Form("B1"), scenario: str = Form("free talk")):
    """Створити нову сесію розмови (для збереження історії/прогресу)."""
    db.init_db()
    sid = db.create_session(level, scenario)
    return {"session_id": sid}


@router.get("/progress")
async def progress():
    db.init_db()
    return db.progress_summary()


# --- Навчальний план A1–A2 та перевірка знань ---
class QuizGradeRequest(BaseModel):
    answers: list = []


@router.get("/curriculum")
async def curriculum_overview():
    """Список юнітів A1–A2 + прогрес користувача (для екрана «Навчання»)."""
    db.init_db()
    overview = curriculum.curriculum_overview()
    overview["progress"] = db.curriculum_progress()
    return overview


@router.get("/curriculum/progress")
async def curriculum_progress_endpoint():
    """Агрегована статистика навчання + історія тестів."""
    db.init_db()
    return {
        "progress": db.curriculum_progress(),
        "history": db.quiz_history(limit=20),
    }


@router.get("/curriculum/{unit_id}")
async def curriculum_unit(unit_id: str):
    """Повний контент юніта (лексика, граматика, фрази, цілі) для вивчення."""
    unit = curriculum.get_unit(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Юніт не знайдено")
    # Не віддаємо quiz тут — контент і тест розділені.
    return {k: v for k, v in unit.items() if k != "quiz"}


@router.get("/curriculum/{unit_id}/quiz")
async def curriculum_quiz(unit_id: str):
    """Питання тесту БЕЗ відповідей."""
    payload = curriculum.quiz_payload(unit_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Юніт не знайдено")
    return payload


@router.post("/curriculum/{unit_id}/grade")
async def curriculum_grade(unit_id: str, req: QuizGradeRequest):
    """Перевірити відповіді, зберегти результат у БД, повернути детальний розбір."""
    unit = curriculum.get_unit(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Юніт не знайдено")
    result = curriculum.grade_quiz(unit_id, req.answers)
    db.init_db()
    db.record_quiz_attempt(unit_id, unit["level"], result)
    return result



@router.post("/words")
async def add_word_endpoint(
    word: str = Form(...), translation: str = Form(""), example: str = Form("")
):
    db.add_word(word, translation, example)
    return {"ok": True}


@router.get("/words/due")
async def words_due():
    return {"words": db.due_words()}


@router.post("/words/{word_id}/review")
async def review(word_id: int, quality: int = Form(...)):
    db.review_word(word_id, quality)
    return {"ok": True}



@router.get("/settings")
async def get_settings():
    """Поточні налаштування користувача + списки голосів/провайдерів/рівнів/сценаріїв/мів/режимів."""
    us = user_settings.load()
    return {
        "settings": us,
        "voices": ["F1", "F2", "F3", "F4", "F5", "M1", "M2", "M3", "M4", "M5"],
        "providers": ["supertonic", "piper", "edge"],
        "levels": available_levels(),
        "scenarios": available_scenarios(),
        "target_languages": available_target_languages(),
        "modes": ["tutor", "coach", "mixed"],
    }


class SettingsSaveRequest(BaseModel):
    tts_provider: str | None = None
    supertonic_voice: str | None = None
    supertonic_speed: float | None = None
    coach_template: str | None = None
    default_level: str | None = None
    default_scenario: str | None = None
    default_mode: str | None = None
    default_target_lang: str | None = None


@router.post("/settings")
async def save_settings(req: SettingsSaveRequest):
    """Оновити runtime-налаштування (без перезапуску сервера)."""
    updates = req.model_dump(exclude_unset=True)

    if "supertonic_speed" in updates and updates["supertonic_speed"] is not None:
        v = float(updates["supertonic_speed"])
        if not (0.5 <= v <= 2.0):
            raise HTTPException(status_code=422, detail="швидкість мови має бути в межах 0.5–2.0")
        updates["supertonic_speed"] = v

    if "coach_template" in updates and updates["coach_template"] is not None:
        if not updates["coach_template"].strip():
            raise HTTPException(status_code=422, detail="шаблон коуча не може бути порожнім")

    if "default_level" in updates and updates["default_level"] is not None:
        if updates["default_level"].upper() not in CEFR_LEVELS:
            raise HTTPException(status_code=422, detail="невідомий рівень знань")

    if "default_scenario" in updates and updates["default_scenario"] is not None:
        if updates["default_scenario"] not in SCENARIOS:
            raise HTTPException(status_code=422, detail="невідомий сценарій")

    if "default_mode" in updates and updates["default_mode"] is not None:
        if updates["default_mode"] not in ("tutor", "coach", "mixed"):
            raise HTTPException(status_code=422, detail="невідомий режим розмови")

    if "default_target_lang" in updates and updates["default_target_lang"] is not None:
        codes = {l["code"] for l in available_target_languages()}
        if updates["default_target_lang"] not in codes:
            raise HTTPException(status_code=422, detail="невідома мова вивчення")

    data = user_settings.save(updates)
    return {"ok": True, "settings": data}


@router.post("/settings/test_voice")
async def settings_test_voice(
    voice: str = Form(...), lang: str = Form("uk"), speed: str = Form("1.05")
):
    """Зразок обраного голосу без збереження налаштувань."""
    from app.services import tts_service
    try:
        audio = await tts_service.synthesize(
            "Привіт, це перевірка голосу Mira.", lang, voice=voice, speed=float(speed)
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"tts_error: {e}")
    return {"audio_b64": _b64(audio), "audio_mime": "audio/wav"}


@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: int):
    """Видалити чат (сесію та всю її історію реплік)."""
    db.init_db()
    db.delete_session(session_id)
    return {"ok": True}



def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode() if data else ""
