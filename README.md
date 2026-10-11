# MiraSpeak

Локальна програма для вивчення англійської мови з українською підтримкою.
AI-тьютор Mira розмовляє англійською та українською.

## Запуск (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app.main
# http://127.0.0.1:8000

## AI Stack (Block 3)
- Ollama + LLM за профілем (high: llama3.1:8b / low 6GB: llama3.2:3b)
- faster-whisper (STT, cpu/cuda auto; автовідкат на CPU, якщо CUDA-бібліотеки відсутні)
- edge-tts (TTS EN + UK), Piper — офлайн-опція

