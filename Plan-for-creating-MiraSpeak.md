# 1. Вступ

**Назва програми:** MiraSpeak  

**Цей блок інформації називається:** Вступ до створення навчальної програми з англійської мови української локалізації.

**Загальна кількість блоків до кінцевої реалізації:** рівно **8**.

1. Вступ (поточний)  
2. Підготовка середовища та базової структури проекту  
3. Налаштування локального AI-стеку (Ollama + STT + TTS)  
4. Реалізація голосового пайплайну STT → LLM → TTS  
5. Системні промпти, білінгвальна логіка та рівні CEFR  
6. MVP інтерфейсу користувача  
7. Сценарії, прогрес, база даних і SRS  
8. Полірування, тестування та фінальний реліз  

**Детальний план локальної програми для вивчення англійської (аналог Loora AI) з підтримкою української та англійської.**

Мета: повністю локальний (або гібридний) додаток, де AI-тьютор («Loora») веде розмовну практику англійською, може пояснювати/перекладати українською, давати виправлення, сценарії та зворотний зв’язок. Головний акцент — якісний голос (STT + TTS), без обов’язкової 3D-моделі. Рівні: від A1 (початковий) і вище (до C1/C2).

### 1. Готові відкриті рішення (основа для форку/адаптації)

Найкращі локальні/гібридні проекти (2025–2026):

| Проект | Посилання | Ключові фічі | Підходить для |
|--------|-----------|--------------|---------------|
| **LocalEnglishTutor** | github.com/VictorLopes/LocalEnglishTutor | Повністю локальний: Ollama + faster-whisper + kokoro-onnx TTS, CEFR рівніні (A1–C2), теми, історія розмов, WhatsApp-подібний UI | Найкращий старт для локального |
| **freelingo** | github.com/ArtCC/freelingo | CEFR-плани, AI-тьютор, голос, флеш-карти, SRS, Docker, локальний/хмарний LLM, Kokoro + faster-whisper | Повна платформа з навчальним планом |
| **Ringle AI Tutor** | github.com/UnripePlum/ringle-ai-tutor | STT→LLM→TTS пайплайн, локальний (Ollama + whisper-cpp + edge-tts) або OpenAI, streaming | Голосова розмова з низькою затримкою |
| **Discute** | github.com/5uru/Discute | Whisper + Kokoro + LLM, Streamlit UI | Швидкий прототип |
| **OllamaTutor** | github.com/tankxiaodi/OllamaTutor | Локальний Ollama, кастомні теми/персона, кілька TTS | Кастомізація персона |
| **Mimora** | github.com/vikonix/Mimora | 100% офлайн вимова (англійська/іспанська), scoring | Модуль вимови |
| **SpeakUp (XE3-ESL)** | github.com/1024XEngineer/XE3-ESL | Сценарії (IELTS, робота, життя), зворотний зв’язок, рев’ю | Розширені сценарії |

**Рекомендована база**: почати з **LocalEnglishTutor** або **freelingo** (або комбінація їх пайплайнів). Вони вже мають локальний стек і підтримку рівнів.

**Компоненти, які варто брати окремо**:
- **STT**: faster-whisper (або whisper.cpp) — відмінно працює з англійською + українською.
- **TTS**: Kokoro-onnx / Piper / edge-tts (висока якість, підтримка EN + UK). Для «жіночого» голосу Loora — клонування через OpenVoice або XTTS (якщо є GPU).
- **LLM**: Ollama (Llama 3.1/3.2, Qwen2.5, Gemma2) або LocalAI. Для білінгвальності — моделі з хорошим українським (Qwen, Llama 3.1).
- **UI**: Streamlit / Gradio (швидкий старт) → потім React/Electron/Flutter для десктопу/мобільного.

### 2. Архітектура програми

```
Користувач (мікрофон/текст)
    ↓
VAD (Voice Activity Detection) → обрізка тиші
    ↓
STT (faster-whisper) → транскрипт (EN/UK)
    ↓
LLM (Ollama) — системний промпт тьютора
    ↓
Відповідь + виправлення + пояснення (EN + UK)
    ↓
TTS (Kokoro/edge-tts) → голос
    ↓
UI + історія + прогрес (SQLite)
```

**Режими роботи**:
- Повністю локальний (Ollama + локальний STT/TTS).
- Гібрид (локальний STT/TTS + хмарний LLM для якості).
- Офлайн-режим з кешованими уроками.

### 3. Основні функції (MVP → повна версія)

**MVP (1–2 місяці)**:
1. Голосова розмова з AI-тьютором.
2. Вибір рівня (A1–B2+) і теми/сценарію.
3. Миттєве виправлення помилок + природніші варіанти.
4. Переклад/пояснення українською за запитом.
5. Історія розмов + просте оцінювання.
6. Якісний жіночий голос (EN + UK).

**Повна версія**:
- Сценарії: знайомство, магазин, робота, подорож, співбесіда, IELTS Speaking тощо.
- Граматика + словник (SRS/spaced repetition).
- Shadowing (повторення за диктором) + оцінка вимови.
- Персональний план навчання (CEFR-aligned).
- Рев’ю сесії: оцінка fluency, accuracy, vocabulary, suggestions.
- Багатомовний інтерфейс (UK/EN).
- Експорт прогресу / нотатки.

### 4. Детальний план розробки (етапи)

**Етап 0. Підготовка (1 тиждень)**
- Вибрати базу (рекомендую LocalEnglishTutor).
- Встановити Ollama + моделі (llama3.1:8b або qwen2.5:7b/14b).
- Налаштувати faster-whisper + Kokoro/edge-tts.
- Перевірити якість STT/TTS для української та англійської.

**Етап 1. Базовий голосовий пайплайн (2–3 тижні)**
- Реалізувати STT → LLM → TTS цикл.
- Системний промпт тьютора:
  - «Ти — дружня AI-тьюторка Loora. Розмовляй природною англійською. Якщо користувач помиляється — м’яко виправляй і давай кращий варіант. За запитом пояснюй українською. Підлаштовуйся під рівень A1–C2.»
- Додати можливість перемикання мови відповіді (EN/UK).
- Базовий UI (Streamlit або Gradio): кнопка мікрофона, історія чату, вибір рівня.

**Етап 2. Навчальний контент і сценарії (2–4 тижні)**
- Бібліотека тем/сценаріїв (JSON/YAML) за рівнями.
- Адаптивні відповіді залежно від рівня (A1 — прості речення, B2+ — ідіоми).
- Модуль виправлень: граматика, лексика, природність.
- Збереження сесій у SQLite.

**Етап 3. Прогрес і персоналізація (2–3 тижні)**
- Трекінг: streak, час розмови, слабкі місця.
- SRS для нових слів/фраз.
- Автоматична генерація коротких уроків/діалогів.
- Рев’ю після сесії (оцінки + рекомендації).

**Етап 4. Поліпшення голосу та UX (2–4 тижні)**
- Кращий TTS (клонування голосу Loora, якщо потрібно).
- VAD + streaming (низька затримка).
- Темп мови, паузи, можливість повторити.
- Темна/світла тема, українська локалізація UI.

**Етап 5. Полірування і розгортання**
- Docker-compose для легкого запуску.
- Десктоп (Electron/Tauri) або мобільний (Flutter/React Native) пізніше.
- Тестування на різних рівнях і апаратурі (CPU/GPU).
- Документація + інструкція встановлення.

### 5. Технічний стек (рекомендований)

- **Backend**: Python (FastAPI) + Ollama
- **STT**: faster-whisper
- **TTS**: Kokoro-onnx / edge-tts / Piper
- **LLM**: Ollama (локально) або OpenAI-compatible API
- **БД**: SQLite (потім PostgreSQL)
- **Frontend**: Streamlit (MVP) → React + Tailwind
- **Додатково**: LangChain/LlamaIndex для управління промптами і пам’яттю

### 6. Особливості для української аудиторії

- LLM повинен добре розуміти українську (Qwen2.5 або Llama 3.1 з fine-tune, якщо потрібно).
- Пояснення помилок завжди доступні українською.
- Інтерфейс і системні повідомлення — українською за замовчуванням.
- Підтримка українського акценту в STT (faster-whisper це вміє).

### 7. Ризики та поради

- **Якість голосу** — найважливіше. Тестуйте кілька TTS і вибирайте найприродніший жіночий голос.
- **Затримка** — використовуйте streaming і невеликі моделі (7–8B).
- **Пам’ять** — зберігайте профіль учня (рівень, слабкі місця, улюблені теми).
- **Ліцензії** — перевіряйте ліцензії моделей (більшість MIT/Apache).
- Починайте з простого голосового чату, потім додавайте педагогіку.

### Наступні кроки прямо зараз

1. Клонуйте **LocalEnglishTutor** або **freelingo**.
2. Запустіть локально і протестуйте голос.
3. Адаптуйте системний промпт під білінгвальний режим (EN + UK).
4. Додайте 5–10 базових сценаріїв для A1–B1.

Якщо потрібно — можу деталізувати будь-який етап (промпти, структуру БД, конкретний код пайплайну STT-LLM-TTS, список сценаріїв тощо).



---

### Блок 2. Підготовка середовища та базової структури проекту  
(точні інструкції для агента в VSCode без варіацій)

Виконай наступні дії строго по порядку. Не пропускай жодного кроку. Не додавай зайвих файлів чи залежностей.

**Крок 1.** Відкрий термінал у VSCode і виконай:  
```bash
mkdir MiraSpeak
cd MiraSpeak
git init
```

**Крок 2.** Створи файл `.gitignore` з таким точним вмістом:  
```
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
env/
*.egg-info/
dist/
build/
.DS_Store
*.log
models/
*.onnx
*.bin
*.gguf
.cache/
node_modules/
```

**Крок 3.** Створи віртуальне середовище Python і активуй його:  
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Крок 4.** Створи файл `requirements.txt` з таким точним вмістом:  
```
fastapi==0.115.0
uvicorn==0.30.6
python-multipart==0.0.9
pydantic==2.8.2
python-dotenv==1.0.1
aiofiles==24.1.0
sqlite-utils==3.36
faster-whisper==1.0.3
edge-tts==6.1.12
ollama==0.3.1
sounddevice==0.5.0
numpy==1.26.4
soundfile==0.12.1
```

**Крок 5.** Встанови залежності:  
```bash
pip install -r requirements.txt
```

**Крок 6.** Створи структуру папок точно так:  
```bash
mkdir -p app/core
mkdir -p app/api
mkdir -p app/services
mkdir -p app/models
mkdir -p app/prompts
mkdir -p data
mkdir -p static
mkdir -p tests
```

**Крок 7.** Створи файл `app/__init__.py` (порожній).  
Створи файл `app/core/__init__.py` (порожній).  
Створи файл `app/api/__init__.py` (порожній).  
Створи файл `app/services/__init__.py` (порожній).  
Створи файл `app/models/__init__.py` (порожній).

**Крок 8.** Створи файл `.env` з таким точним вмістом:  
```
OLLAMA_MODEL=llama3.1:8b
WHISPER_MODEL=base
TTS_VOICE_EN=en-US-AriaNeural
TTS_VOICE_UK=uk-UA-PolinaNeural
DATABASE_PATH=data/miraspeak.db
HOST=127.0.0.1
PORT=8000
```

**Крок 9.** Створи файл `app/core/config.py` з таким точним вмістом:  
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    ollama_model: str = "llama3.1:8b"
    whisper_model: str = "base"
    tts_voice_en: str = "en-US-AriaNeural"
    tts_voice_uk: str = "uk-UA-PolinaNeural"
    database_path: str = "data/miraspeak.db"
    host: str = "127.0.0.1"
    port: int = 8000
    base_dir: Path = Path(__file__).resolve().parent.parent.parent

    class Config:
        env_file = ".env"

settings = Settings()
```

**Крок 10.** Створи файл `app/main.py` з таким точним вмістом:  
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

app = FastAPI(title="MiraSpeak", version="0.1.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "MiraSpeak is running", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
```

**Крок 11.** Створи файл `README.md` з таким точним вмістом:  
```
# MiraSpeak

Локальна програма для вивчення англійської мови з українською підтримкою.
AI-тьютор Mira розмовляє англійською та українською.
```

**Крок 12.** Перевір, що сервер запускається:  
```bash
python -m app.main
```

Після успішного запуску (має з’явитися повідомлення про запуск на http://127.0.0.1:8000) зупини сервер (Ctrl+C).

**Кінець Блоку 2.**  
Повідом: «Блок 2 виконано успішно. Готовий до Блоку 3.»

**Блок 3. Налаштування локального AI-стеку (Ollama + STT + TTS)**  
(точні інструкції для агента в VSCode без варіацій)

Виконай наступні дії строго по порядку. Не пропускай жодного кроку. Не додавай зайвих файлів чи залежностей.

**Крок 1.** Переконайся, що віртуальне середовище активне:  
```bash
source .venv/bin/activate
```

**Крок 2.** Встанови Ollama системно (один раз на машину):  
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Крок 3.** Перевір, що Ollama встановлено:  
```bash
ollama --version
```

**Крок 4.** Запусти сервіс Ollama (якщо він ще не запущений):  
```bash
ollama serve
```  
Залиш цей термінал відкритим. Відкрий новий термінал у VSCode для наступних команд.

**Крок 5.** У новому терміналі завантаж модель LLM:  
```bash
ollama pull llama3.1:8b
```

**Крок 6.** Перевір, що модель доступна:  
```bash
ollama list
```  
У списку має бути `llama3.1:8b`.

**Крок 7.** Створи файл `app/services/stt.py` з таким точним вмістом:  
```python
from faster_whisper import WhisperModel
from app.core.config import settings
import tempfile
import os

class STTService:
    def __init__(self):
        self.model = WhisperModel(
            settings.whisper_model,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            segments, _ = self.model.transcribe(
                tmp_path,
                language=language,
                beam_size=5,
                vad_filter=True
            )
            text = " ".join([segment.text.strip() for segment in segments])
            return text.strip()
        finally:
            os.unlink(tmp_path)

stt_service = STTService()
```

**Крок 8.** Створи файл `app/services/tts.py` з таким точним вмістом:  
```python
import edge_tts
import asyncio
import tempfile
import os
from app.core.config import settings

class TTSService:
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        voice = settings.tts_voice_en if language == "en" else settings.tts_voice_uk
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        await communicate.save(tmp_path)
        try:
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            return audio_data
        finally:
            os.unlink(tmp_path)

tts_service = TTSService()
```

**Крок 9.** Створи файл `app/services/llm.py` з таким точним вмістом:  
```python
import ollama
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.model = settings.ollama_model

    def chat(self, messages: list[dict]) -> str:
        response = ollama.chat(
            model=self.model,
            messages=messages
        )
        return response["message"]["content"]

llm_service = LLMService()
```

**Крок 10.** Створи файл `app/services/__init__.py` з таким точним вмістом:  
```python
from .stt import stt_service
from .tts import tts_service
from .llm import llm_service
```

**Крок 11.** Перевір імпорт сервісів:  
```bash
python -c "from app.services import stt_service, tts_service, llm_service; print('Services OK')"
```

**Крок 12.** Перевір роботу LLM:  
```bash
python -c "
from app.services.llm import llm_service
print(llm_service.chat([{'role': 'user', 'content': 'Say hello in one word'}]))
"
```

**Крок 13.** Перевір роботу TTS (збереже тестовий файл):  
```bash
python -c "
import asyncio
from app.services.tts import tts_service
audio = asyncio.run(tts_service.synthesize('Hello, I am Mira.', 'en'))
with open('data/test_en.mp3', 'wb') as f:
    f.write(audio)
print('TTS EN OK, saved data/test_en.mp3')
audio_uk = asyncio.run(tts_service.synthesize('Привіт, я Міра.', 'uk'))
with open('data/test_uk.mp3', 'wb') as f:
    f.write(audio_uk)
print('TTS UK OK, saved data/test_uk.mp3')
"
```

**Крок 14.** Онови файл `README.md` — додай в кінець:  
```
## AI Stack (Block 3)
- Ollama + llama3.1:8b
- faster-whisper (STT)
- edge-tts (TTS EN + UK)
```

**Кінець Блоку 3.**  
Повідом: «Блок 3 виконано успішно. Готовий до Блоку 4.»

**Блок 4. Реалізація голосового пайплайну STT → LLM → TTS**  
(точні інструкції для агента в VSCode без варіацій)

Виконай наступні дії строго по порядку. Не пропускай жодного кроку. Не додавай зайвих файлів чи залежностей.

**Крок 1.** Переконайся, що віртуальне середовище активне і Ollama запущений:  
```bash
source .venv/bin/activate
```

**Крок 2.** Створи файл `app/prompts/system.py` з таким точним вмістом:  
```python
SYSTEM_PROMPT = """You are Mira, a friendly and patient AI English tutor for Ukrainian speakers.
Always reply primarily in clear, natural English appropriate to the student's level.
If the student makes a mistake, gently correct it and offer a better version.
When the student asks for explanation in Ukrainian or writes in Ukrainian, you may briefly explain in Ukrainian and then continue in English.
Keep responses concise (1-4 sentences) unless the student asks for more detail.
Encourage the student and ask follow-up questions to keep the conversation going.
Current student level: {level}
"""
```

**Крок 3.** Створи файл `app/models/schemas.py` з таким точним вмістом:  
```python
from pydantic import BaseModel
from typing import Optional, List

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    text: Optional[str] = None
    level: str = "A2"
    history: List[Message] = []

class ChatResponse(BaseModel):
    reply: str
    corrected: Optional[str] = None
    audio_base64: Optional[str] = None
```

**Крок 4.** Створи файл `app/services/pipeline.py` з таким точним вмістом:  
```python
import base64
import asyncio
from typing import List, Optional
from app.services.stt import stt_service
from app.services.tts import tts_service
from app.services.llm import llm_service
from app.prompts.system import SYSTEM_PROMPT
from app.models.schemas import Message

class PipelineService:
    def process_text(
        self,
        text: str,
        level: str = "A2",
        history: List[Message] = None
    ) -> dict:
        if history is None:
            history = []

        system_msg = {
            "role": "system",
            "content": SYSTEM_PROMPT.format(level=level)
        }

        messages = [system_msg]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": text})

        reply = llm_service.chat(messages)
        return {
            "reply": reply,
            "corrected": None
        }

    async def process_audio(
        self,
        audio_bytes: bytes,
        level: str = "A2",
        history: List[Message] = None,
        language: str = "en"
    ) -> dict:
        text = stt_service.transcribe(audio_bytes, language=language)
        result = self.process_text(text, level=level, history=history)

        audio_data = await tts_service.synthesize(result["reply"], language="en")
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        result["user_text"] = text
        result["audio_base64"] = audio_b64
        return result

pipeline_service = PipelineService()
```

**Крок 5.** Створи файл `app/api/chat.py` з таким точним вмістом:  
```python
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import json
from app.services.pipeline import pipeline_service
from app.models.schemas import ChatRequest, ChatResponse, Message

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat/text", response_model=ChatResponse)
async def chat_text(request: ChatRequest):
    result = pipeline_service.process_text(
        text=request.text or "",
        level=request.level,
        history=request.history
    )
    return ChatResponse(
        reply=result["reply"],
        corrected=result.get("corrected")
    )

@router.post("/chat/audio")
async def chat_audio(
    file: UploadFile = File(...),
    level: str = Form("A2"),
    history: Optional[str] = Form(None),
    language: str = Form("en")
):
    audio_bytes = await file.read()
    hist = []
    if history:
        hist = [Message(**m) for m in json.loads(history)]

    result = await pipeline_service.process_audio(
        audio_bytes=audio_bytes,
        level=level,
        history=hist,
        language=language
    )
    return {
        "user_text": result.get("user_text"),
        "reply": result["reply"],
        "corrected": result.get("corrected"),
        "audio_base64": result.get("audio_base64")
    }
```

**Крок 6.** Онови файл `app/main.py` — заміни весь вміст на:  
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.chat import router as chat_router

app = FastAPI(title="MiraSpeak", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "MiraSpeak is running", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
```

**Крок 7.** Онови файл `app/services/__init__.py` — заміни весь вміст на:  
```python
from .stt import stt_service
from .tts import tts_service
from .llm import llm_service
from .pipeline import pipeline_service
```

**Крок 8.** Створи порожній файл `app/prompts/__init__.py`.

**Крок 9.** Перевір, що сервер запускається без помилок:  
```bash
python -m app.main
```  
Залиш сервер запущеним. У новому терміналі виконай тести.

**Крок 10.** Протестуй текстовий ендпоінт:  
```bash
curl -X POST http://127.0.0.1:8000/api/chat/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "level": "A2", "history": []}'
```

**Крок 11.** Онови файл `README.md` — додай в кінець:  
```
## Voice Pipeline (Block 4)
- POST /api/chat/text
- POST /api/chat/audio
- STT → LLM → TTS pipeline ready
```

**Кінець Блоку 4.**  
Повідом: «Блок 4 виконано успішно. Готовий до Блоку 5.»

# Свіжий блок оновлень 23:37 12.10.2026.

**Так, зрозумів.**  
Ти хочеш, щоб Mira вела **природний інтерактивний діалог** (як я), з вільною підтримкою двох мов (англійська + українська) і відчуттям реального часу.

Нижче — чіткий план реалізації природного діалогу, а потім одразу точні інструкції для **Блоку 5**, куди це входить.

### План реалізації природного діалогу (Bilingual Real-time Conversation)

1. **Пам’ять розмови (Conversation Memory)**  
   Зберігати історію повідомлень (user + assistant) у сесії. Передавати останні 8–12 повідомлень у кожен запит до LLM, щоб Mira «пам’ятала» контекст.

2. **Розумне визначення мови**  
   - Якщо користувач говорить/пише українською → Mira спочатку коротко відповідає українською (пояснення), потім продовжує англійською.  
   - Якщо англійською → повністю англійською + м’які виправлення.  
   - Можна додати явний параметр `preferred_reply_lang`.

3. **Системний промпт з особистістю**  
   Mira має бути теплою, терплячою, трохи жартівливою, завжди задавати follow-up питання, щоб діалог не обривався.

4. **Структура відповіді**  
   Кожна відповідь LLM повинна повертатися у структурованому вигляді (JSON):  
   - `reply_en` — основна відповідь англійською  
   - `reply_uk` — короткий переклад/пояснення українською (якщо потрібно)  
   - `correction` — виправлення помилки (якщо є)  
   - `follow_up` — питання для продовження

5. **Реальний час (відчуття live)**  
   - На MVP: швидкий request-response + потокове відтворення аудіо.  
   - Пізніше (Блок 6–7): WebSocket + streaming токенів від Ollama + потоковий TTS.

6. **Рівень CEFR**  
   Промпт автоматично підлаштовує складність словника і граматики під вибраний рівень (A1–C1).

---

### Блок 5. Системні промпти, білінгвальна логіка та рівні CEFR  
(точні інструкції для агента в VSCode без варіацій)

Виконай наступні дії строго по порядку.

**Крок 1.** Активуй середовище:  
```bash
source .venv/bin/activate
```

**Крок 2.** Заміни весь вміст файлу `app/prompts/system.py` на:  
```python
SYSTEM_PROMPT = """You are Mira — a warm, patient, slightly playful AI English tutor for Ukrainian speakers.
Your goal is to help the student practice speaking English naturally through conversation.

Rules:
1. Always reply primarily in clear, natural English appropriate to the student's CEFR level: {level}.
2. If the student writes or speaks in Ukrainian, first give a short helpful reply or explanation in Ukrainian, then continue the conversation in English.
3. When the student makes a grammar or vocabulary mistake, gently correct it in a natural way (do not just list errors). Offer a better version.
4. Always end your reply with a short follow-up question to keep the conversation going.
5. Keep replies concise: 1–4 sentences maximum unless the student asks for more.
6. Be encouraging and friendly. Never sound like a strict teacher.

Current student level: {level}
Conversation history is provided. Use it to stay consistent and remember previous context.
"""
```

**Крок 3.** Онови файл `app/models/schemas.py` — заміни весь вміст на:  
```python
from pydantic import BaseModel
from typing import Optional, List

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    text: Optional[str] = None
    level: str = "A2"
    history: List[Message] = []
    preferred_lang: str = "auto"   # auto | en | uk

class ChatResponse(BaseModel):
    reply: str
    reply_uk: Optional[str] = None
    correction: Optional[str] = None
    follow_up: Optional[str] = None
    audio_base64: Optional[str] = None
    user_text: Optional[str] = None
```

**Крок 4.** Онови файл `app/services/pipeline.py` — заміни весь вміст на:  
```python
import base64
import json
from typing import List, Optional
from app.services.stt import stt_service
from app.services.tts import tts_service
from app.services.llm import llm_service
from app.prompts.system import SYSTEM_PROMPT
from app.models.schemas import Message

class PipelineService:
    def _build_messages(self, text: str, level: str, history: List[Message]) -> list:
        system_msg = {
            "role": "system",
            "content": SYSTEM_PROMPT.format(level=level)
        }
        messages = [system_msg]
        for msg in history[-10:]:  # останні 10 повідомлень
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": text})
        return messages

    def process_text(
        self,
        text: str,
        level: str = "A2",
        history: List[Message] = None,
        preferred_lang: str = "auto"
    ) -> dict:
        if history is None:
            history = []

        messages = self._build_messages(text, level, history)
        raw_reply = llm_service.chat(messages)

        # Простий парсинг (поки без строгого JSON)
        reply = raw_reply.strip()
        reply_uk = None
        correction = None

        return {
            "reply": reply,
            "reply_uk": reply_uk,
            "correction": correction,
            "follow_up": None
        }

    async def process_audio(
        self,
        audio_bytes: bytes,
        level: str = "A2",
        history: List[Message] = None,
        language: str = "en",
        preferred_lang: str = "auto"
    ) -> dict:
        text = stt_service.transcribe(audio_bytes, language=language)
        result = self.process_text(text, level=level, history=history, preferred_lang=preferred_lang)

        audio_data = await tts_service.synthesize(result["reply"], language="en")
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        result["user_text"] = text
        result["audio_base64"] = audio_b64
        return result

pipeline_service = PipelineService()
```

**Крок 5.** Онови файл `app/api/chat.py` — заміни весь вміст на:  
```python
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import json
from app.services.pipeline import pipeline_service
from app.models.schemas import ChatRequest, ChatResponse, Message

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat/text", response_model=ChatResponse)
async def chat_text(request: ChatRequest):
    result = pipeline_service.process_text(
        text=request.text or "",
        level=request.level,
        history=request.history,
        preferred_lang=request.preferred_lang
    )
    return ChatResponse(
        reply=result["reply"],
        reply_uk=result.get("reply_uk"),
        correction=result.get("correction"),
        follow_up=result.get("follow_up")
    )

@router.post("/chat/audio")
async def chat_audio(
    file: UploadFile = File(...),
    level: str = Form("A2"),
    history: Optional[str] = Form(None),
    language: str = Form("en"),
    preferred_lang: str = Form("auto")
):
    audio_bytes = await file.read()
    hist = []
    if history:
        hist = [Message(**m) for m in json.loads(history)]

    result = await pipeline_service.process_audio(
        audio_bytes=audio_bytes,
        level=level,
        history=hist,
        language=language,
        preferred_lang=preferred_lang
    )
    return {
        "user_text": result.get("user_text"),
        "reply": result["reply"],
        "reply_uk": result.get("reply_uk"),
        "correction": result.get("correction"),
        "follow_up": result.get("follow_up"),
        "audio_base64": result.get("audio_base64")
    }
```

**Крок 6.** Перевір текстовий діалог з історією:  
```bash
curl -X POST http://127.0.0.1:8000/api/chat/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Привіт! Я хочу практикувати англійську",
    "level": "A2",
    "history": [],
    "preferred_lang": "auto"
  }'
```

**Крок 7.** Онови `README.md` — додай:  
```
## Natural Dialogue (Block 5)
- Bilingual support (EN + UK)
- Conversation memory (last 10 messages)
- CEFR level adaptation
- Follow-up questions for continuous dialogue
```

**Кінець Блоку 5.**  
Повідом: «Блок 5 виконано успішно. Готовий до Блоку 6.»