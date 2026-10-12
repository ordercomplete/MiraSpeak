import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.db import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

app = FastAPI(title="MiraSpeak", version="0.3.0")

app.mount("/static", StaticFiles(directory=settings.base_dir / "static"), name="static")

from app.api.routes import router as api_router
app.include_router(api_router)

init_db()

@app.get("/")
async def root():
    return FileResponse(settings.base_dir / "static" / "index.html")

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "0.3.0",
        "llm_provider": settings.llm_provider,
        "model": settings.resolved_ollama_model,
        "profile": settings.model_profile,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
