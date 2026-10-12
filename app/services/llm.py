import httpx

from app.core.config import settings


class LLMService:
    """Єдина точка виклику LLM. Провайдер обирається через LLM_PROVIDER:
    ollama (локально) | lmstudio (локально) | openai (зовнішній API).
    Локальний Ollama — за замовчуванням; fallback на ollama при помилці зовнішнього."""

    def __init__(self):
        self.provider = settings.llm_provider

    @property
    def model(self) -> str:
        if self.provider == "ollama":
            return settings.resolved_ollama_model
        return settings.openai_model or settings.resolved_ollama_model

    async def chat(self, messages: list[dict]) -> str:
        try:
            return await self._call(messages)
        except Exception as primary_error:
            if self.provider != "ollama":
                # Зовнішній сервіс недоступний → пробуємо локальний Ollama
                try:
                    return await self._call_ollama(messages)
                except Exception:
                    pass
            raise primary_error

    async def _call(self, messages: list[dict]) -> str:
        if self.provider == "ollama":
            return await self._call_ollama(messages)
        return await self._call_openai_compatible(messages)

    async def _call_ollama(self, messages: list[dict]) -> str:
        payload = {
            "model": settings.resolved_ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"num_ctx": settings.ollama_num_ctx},
            "think": False,
        }
        async with httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=180.0) as client:
            resp = await client.post("/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    async def _call_openai_compatible(self, messages: list[dict]) -> str:
        base_url = settings.openai_base_url
        if self.provider == "lmstudio" and not base_url:
            base_url = "http://127.0.0.1:1234/v1"
        if not base_url:
            raise ValueError("OPENAI_BASE_URL не задано для LLM_PROVIDER=openai")
        headers = {}
        if settings.openai_api_key:
            headers["Authorization"] = f"Bearer {settings.openai_api_key}"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=180.0) as client:
            resp = await client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]


llm_service = LLMService()
