from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

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


@router.post("/voice")
async def voice_turn(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    level: str = Form("B1"),
    scenario: str = Form("free talk"),
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


def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode() if data else ""
