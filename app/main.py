from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

app = FastAPI(title="MiraSpeak", version="0.2.0")

app.mount("/static", StaticFiles(directory=settings.base_dir / "static"), name="static")

from app.api.routes import router as api_router
app.include_router(api_router)

@app.get("/")
async def root():
    return FileResponse(settings.base_dir / "static" / "index.html")

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "0.2.0",
        "llm_provider": settings.llm_provider,
        "model": settings.resolved_ollama_model,
        "profile": settings.model_profile,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
