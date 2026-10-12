from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Замовчування профілів (розділ 0.4): профіль підставляє модель, якщо її не задано вручну
PROFILE_MODELS = {
    "high": "gemma4:26b",
    "medium": "qwen2.5:7b",
    "low": "llama3.2:3b",
    "cpu": "qwen2.5:3b",
}

# Профільні моделі STT (Whisper). large-v3-turbo (809M) ≈ точність large-v3
# при ~6× швидкості; small лишається для слабких машин/6GB (краще за base,
# але поміщається). Вага: turbo ~1.6 GB (float16) на GPU1/GPU2.
PROFILE_STT_MODELS = {
    "high": "large-v3-turbo",
    "medium": "large-v3-turbo",
    "low": "base",
    "cpu": "base",
}

# Підказка для Whisper про мову/контекст — покращує розпізнавання української
# (правильна лексика, цифри, імена). Порожньо = вимкнути.
STT_INITIAL_PROMPT_UK = (
    "Розмова українською та англійською. Привіт, як справи? Розкажіть про свій день, "
    "роботу, подорожі, хобі. Правильні слова: Слава Україні, Київ, подорож, учора, "
    "сьогодні, завтра. Разом із англійськими фразами: Hello, how are you, yesterday I went."
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # LLM
    llm_provider: str = "ollama"          # ollama | lmstudio | openai
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = ""                # порожньо => за профілем
    ollama_num_ctx: int = 2048
    openai_api_key: str = ""
    openai_base_url: str = ""             # напр. http://127.0.0.1:1234/v1 (LM Studio)
    openai_model: str = ""
    # STT
    whisper_model: str = ""                # порожньо => за профілем (PROFILE_STT_MODELS)
    stt_device: str = "auto"              # auto | cpu | cuda
    stt_compute_type: str = "auto"        # auto | int8 | float16
    stt_initial_prompt: str = STT_INITIAL_PROMPT_UK   # контекст для кращого розпізнавання укр/англ
    stt_min_silence_ms: int = 500         # мін. пауза (мс), що вважається кінцем фрази (server-side VAD)
    # TTS
    tts_provider: str = "edge"            # edge | piper
    tts_voice_en: str = "en-US-AriaNeural"
    tts_voice_uk: str = "uk-UA-PolinaNeural"
    piper_voice_en: str = ""
    # Додаток
    model_profile: str = "high"           # high | medium | low | cpu
    database_path: str = "data/miraspeak.db"
    host: str = "127.0.0.1"
    port: int = 8000
    base_dir: Path = BASE_DIR

    @property
    def resolved_ollama_model(self) -> str:
        if self.ollama_model:
            return self.ollama_model
        return PROFILE_MODELS.get(self.model_profile, PROFILE_MODELS["high"])

    @property
    def resolved_whisper_model(self) -> str:
        if self.whisper_model:
            return self.whisper_model
        return PROFILE_STT_MODELS.get(self.model_profile, PROFILE_STT_MODELS["high"])

settings = Settings()
