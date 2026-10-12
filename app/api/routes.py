from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.core import db
from app.core.config import settings
from app.services import curriculum
from app.services.pipeline import pipeline_service
from app.services.prompt import available_levels, available_scenarios

router = APIRouter(prefix="/api")


class TextTurnRequest(BaseModel):
    message: str
    language: str = "en"
    mode: str = "tutor"
    level: str = "B1"
    scenario: str = "free talk"
    history: list[dict] = []
    session_id: int = 0


@router.post("/voice")
async def voice_turn(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    mode: str = Form("tutor"),
    level: str = Form("B1"),
    scenario: str = Form("free talk"),
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
    )
    if not result.get("ok"):
        raise HTTPException(status_code=422, detail=result.get("error"))
    audio_bytes = result.pop("audio", b"")
    drill_audio = result.pop("drill_audio", b"")
    # Збереження ходу в історію сесії (прогрес/аналітика)
    if session_id:
        db.add_message(session_id, "user", result.get("transcript", ""))
        db.add_message(session_id, "assistant", result.get("reply_text", ""), result.get("correction", ""))
    return {
        **result,
        "audio_b64": _b64(audio_bytes),
        "drill_audio_b64": _b64(drill_audio),
    }


@router.post("/text")
async def text_turn(req: TextTurnRequest):
    """Текстовий цикл (без мікрофона) — для тестів і швидкого чату."""
    result = await pipeline_service.text_turn(
        req.message, mode=req.mode, level=req.level, scenario=req.scenario, history=req.history
    )
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result.get("error"))
    audio = result.pop("audio", b"")
    drill_audio = result.pop("drill_audio", b"")
    if req.session_id:
        db.add_message(req.session_id, "user", req.message)
        db.add_message(req.session_id, "assistant", result.get("reply_text", ""), result.get("correction", ""))
    return {
        **result,
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
        "profile": settings.model_profile,
        "llm_provider": settings.llm_provider,
        "tts_provider": settings.tts_provider,
    }


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


def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode() if data else ""
