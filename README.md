# MiraSpeak

Локальна програма для вивчення англійської мови з українською підтримкою.
AI-тьютор Mira розмовляє англійською та українською. Головний принцип — **повна локальність** з можливістю підключення зовнішніх сервісів.

## Запуск (Windows)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.main
# http://127.0.0.1:8000
```

## AI Stack
- **Ollama + LLM** за профілем (high: gemma4:26b / low 6GB: llama3.2:3b)
- **faster-whisper** (STT, cpu/cuda auto; автовідкат на CPU, якщо CUDA-бібліотеки відсутні)
- **edge-tts** (TTS EN + UK), Piper — офлайн-опція

## Профілі продуктивності (`MODEL_PROFILE`)
| Профіль | VRAM/залізо | LLM | СТТ |
|---|---|---|---|
| `high` | ≥ 16 GB (RTX 3090+) | `gemma4:26b` | `small` (cuda) |
| `medium` | 8–12 GB | `qwen2.5:7b` | `base` (cuda) |
| `low` | **6 GB** | `llama3.2:3b` | `base` (cuda/int8) |
| `cpu` | без відеокарти | `qwen2.5:3b` | `base` (int8) |

На машинах із **6 GB VRAM** використовуйте `MODEL_PROFILE=low` та `OLLAMA_MAX_LOADED_MODELS=1`.
Моделі Ollama зберігаються на диску D: (`OLLAMA_MODELS=D:\models\ollama`), бо на C: мало місця.

## Перемикачі провайдерів (`.env`)
- **`LLM_PROVIDER`** = `ollama` (локально) | `lmstudio` | `openai` (зовнішній API; автовідкат на Ollama, якщо зовнішній недоступний).
- **`TTS_PROVIDER`** = `edge` (мережа, кращий голос) | `piper` (офлайн).
- **`STT_DEVICE`** = `auto` | `cpu` | `cuda`.

## Функціонал
- Голосовий цикл: мікрофон → розпізнавання → відповідь Mira → озвучування.
- Білінгвальність: помилки → зелена `📌`-виправлення українською; «поясни» → відповідь українською.
- 7 рівнів CEFR (A1–C2) та 7 сценаріїв розмови.
- Прогрес і словник з інтервальним повторенням (SM-2) у SQLite (`data/miraspeak.db`).

## Відомі обмеження
- Якісного **офлайн-українського TTS зараз немає** (Piper/Kokoro — лише EN); за замовчуванням edge-tts (потребує інтернет для голосу).
- CUDA-бібліотеки (`nvidia-cublas-cu12`) — опційні; без них STT автоматично працює на CPU.
- Найкращий голосовий досвід — на профілі `high`.


