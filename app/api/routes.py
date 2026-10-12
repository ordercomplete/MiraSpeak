from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.core import db
from app.core.config import settings
from app.services.pipeline import pipeline_service
from app.services.prompt import available_levels, available_scenarios

router = APIRouter(prefix="/api")


class TextTurnRequest(BaseModel):
    message: str
    language: str = "en"
    level: str = "B1"
    scenario: str = "free talk"
    history: list[dict] = []
    session_id: int = 0


@router.post("/voice")
async def voice_turn(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    level: str = Form("B1"),
    scenario: str = Form("free talk"),
    session_id: int = Form(0),
):
    """Голосовий цикл: multipart аудіофайл (webm/wav/mp3) → JSON з відповіддю + base64 mp3."""
    raw = await audio.read()
    if not raw:
        raise HTTPException(status_code=400, detail="порожній аудіофайл")
    result = await pipeline_service.voice_turn(
        raw, language=language, level=level, scenario=scenario
    )
    if not result.get("ok"):
        raise HTTPException(status_code=422, detail=result.get("error"))
    audio_bytes = result.pop("audio")
    # Збереження ходу в історію сесії (прогрес/аналітика)
    if session_id:
        db.add_message(session_id, "user", result.get("transcript", ""))
        db.add_message(session_id, "assistant", result.get("reply_text", ""), result.get("correction", ""))
    return {
        **result,
        "audio_b64": _b64(audio_bytes),
    }


@router.post("/text")
async def text_turn(req: TextTurnRequest):
    """Текстовий цикл (без мікрофона) — для тестів і швидкого чату."""
    import asyncio
    from app.services import llm_service, tts_service
    from app.services.prompt import build_system_prompt

    messages = [{"role": "system", "content": build_system_prompt(req.level, req.scenario)}]
    messages.extend(req.history)
    messages.append({"role": "user", "content": req.message})
    try:
        reply = await llm_service.chat(messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"llm_error: {e}")
    spoken, correction = pipeline_service._split_reply(reply)
    audio = b""
    if spoken:
        try:
            audio = await tts_service.synthesize(spoken, "en")
        except Exception:
            pass
    if req.session_id:
        db.add_message(req.session_id, "user", req.message)
        db.add_message(req.session_id, "assistant", reply, correction)
    return {"reply_text": reply, "reply_spoken": spoken, "correction": correction, "audio_b64": _b64(audio)}


@router.get("/voice/sample")
async def voice_sample():
    """Демо-голос тьютора (для екрана привітання)."""
    from app.services import tts_service
    audio = await tts_service.synthesize("Hi! I'm Mira, your English tutor. Let's talk!", "en")
    return Response(content=audio, media_type="audio/mpeg")


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
