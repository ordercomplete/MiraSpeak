# DECISIONS — зафіксовані рішення проєкту

> Формат: дата, варіанти, чому обрано. Правило: рішення щодо вибору/заміни TTS-провайдера приймає власник (Agent-brief.MD 3.4).

## 2026-10-19 — Drama 3 (Fish Audio) як кандидат на додатковий TTS-провайдер

- **Контекст:** власник попросив додати модель Drama 3 (Fish Audio, 35B MoE) як додаткову (змінну) функцію голосу.
- **Варіанти:**
  1. Локальний сервер SGLang-Omni / vLLM-Omni у WSL2/Docker + TTS-провайдер MiraSpeak по localhost (обрано для плану).
  2. Хмарний API `api.fish.audio` — **відкинуто**: порушує offline-first і заборону хмарних TTS (Agent-brief 3.4).
  3. Не інтегрувати — лишити Supertonic — лишається fallback-станом.
- **Чому так:** Drama 3 має `uk` у списку мов (підтверджено model card), режисуру природною мовою і мультиспікер; сумісний за форматом `/v1/tts`.
- **Обмеження/ризики:** FP8 недоступний апаратно на RTX 3090 (Ampere) — реальний VRAM-gate виміряти до інтеграції; ліцензія Community License (у YAML model card вказано `fish-audio-research-license` — розбіжність, текст LICENSE ще не прочитано).
- **Статус:** план написано (`docs/plans/tts-drama3-fishaudio.md`); **рішення щодо зміни провайдера за замовчуванням НЕ прийнято** — очікує bake-off і схвалення власника.

## 2026-10-19 — Гейт кроку 1 плану ПРОЙДЕНО: сервер Drama 3 працює локально

- **Середовище:** Docker Engine (29.1.3) **всередині WSL2 Ubuntu 26.04** (не Docker Desktop — він ігнорував `DataFolder` і тримав vhdx на C: із 6.5 ГБ вільно; C: звільнено, дані Docker тепер у vhdx Ubuntu на D: `D:\WSL\Ubuntu\ext4.vhdx`). NVIDIA Container Toolkit 1.20.1 підключено (`nvidia-ctk runtime configure`), `--gpus all` бачить 3× RTX 3090.
- **Образ:** `hongccc/sglang-omni:dev` (Docker Hub, рекомендований офіційною документацією; sglang-omni 0.1.8 + Python 3.12 всередині).
- **Несумісність, яку довелося вирішити:** в образі sglang 0.5.19, а sglang-omni 0.1.8 імпортує `_SamplingMaskCapture` → `ImportError`. Виправлено: `uv pip install --no-deps sglang==0.5.21` у контейнері (версія за installation.md).
- **Чекпойнт:** `fishaudio/drama-3-int4` (GPTQ 4-bit, 23 ГБ на диску) → `/mnt/d/models/fishaudio/drama-3-int4` (мапиться у контейнер як `/mnt/d/...`).
- **Команда запуску (відтворювана):**
  ```
  docker run -d --name drama3 --gpus all --shm-size 32g --ipc host -p 8000:8000 -v /mnt/d:/mnt/d hongccc/sglang-omni:dev sleep infinity
  docker exec drama3 uv pip install --prerelease=allow --no-deps sglang==0.5.21
  docker exec -d drama3 sgl-omni serve --model-path /mnt/d/models/fishaudio/drama-3-int4 --port 8000 --tts_engine.gpu 2 --tts_engine.gpu_memory_fraction 0.92 --vocoder.gpu 1 --vocoder.gpu_memory_fraction 0.5 --preprocessing.gpu 0
  ```
  (без `--vocoder.gpu_memory_fraction 0.5` сервер падає: частки 2.4 ГБ замало для `max_new_tokens=2048`.)
- **Розподіл GPU (виміряно):** GPU0 — preprocessing 3.2 ГБ (поруч з Ollama/Whisper), GPU1 — vocoder 2.2 ГБ, GPU2 — engine **24.0/24.5 ГБ** (0.64 ГБ під CUDA-graphs, avail mem після старту = 0.00 — щільно, але стабільно; при OOM підняти `gpu_memory_fraction` нема — зменшувати `max_new_tokens` або вимикати prefill-графи).
- **Старт:** ~6 хв (ваги + JIT Triton + захоплення CUDA-graphs 328 с). `GET /health` → 200.
- **Тест-синтез (крок 1, п.4):**
  - uk: `POST /v1/audio/speech` `{"input": "Привіт! Я Міра..."}` → **200, 2.42 с, 676 КБ**, WAV PCM 16-bit mono 44100 Hz ✔
  - en: → **200, 7.24 с** (перший запит, warm-up), WAV PCM 44100 Hz ✔
- **Попередження з лога (очікувано для sm_86):** `codebook sampling: PyTorch, untested GPU sm_86`, `tower fused layers: off` (Hopper-only), `drama3-int4 quantization is not fully optimized yet` — Triton attention backend працює, як і вимагає документація.
- **Висновок гейту: ПРОЙДЕНО.** Далі за планом — Крок 2 (провайдер `FishDramaProvider`). Ліцензія дозволяє некомерційне використання (див. вище).

## 2026-10-19 — Кроки 2–6 плану впроваджено: `fishdrama` працює наскрізно

- **Нові/змінені файли:** `app/services/tts_fishdrama.py` (новий `FishDramaProvider`: `available()`, `synthesize_sync() -> WAV`, voice/speed ігноруються — в API їх немає), гілка `provider == "fishdrama"` у `app/services/tts.py` (фолбек uk→piper, en→edge/piper), `app/core/config.py` (`FISH_TTS_BASE_URL`, `FISH_TTS_TIMEOUT_S`), `app/api/routes.py` (`fishdrama` у `providers` + валідація 422), `static/index.html` (динамічна позначка AI-голосу), `tests/test_tts_fishdrama.py` (7 тестів без мережі), `.env` (змінні сервера).
- **Наскрізна перевірка (живий сервер, provider=fishdrama):** uk 406 КБ/2.1 с, en 258 КБ/0.9 с — обидва WAV PCM 44.1 kHz ✔
- **Супутній фікс:** `streak()` у `app/core/db.py` читав локальну `date.today()`, а `progress.day` пишеться в UTC → після локальної півночі streak падав у 0; узгоджено на UTC.
- **Тести:** `pytest` — 12 passed.
- **Статус:** провайдер за замовчуванням НЕ змінено (`supertonic`); залишився **Крок 7 — bake-off** (порівняння голосів на слух) за власником.

## 2026-10-19 — Стабільні голоси режимів + фіксація наголосів

- **Проблема власника:** кожна підказка FishDrama звучала іншим голосом (без референсу тембр стохастичний). **Виправлено:** `synthesize_sync(..., mode)` тепер клонує фіксований референс режиму → тембр стабільний. Живий тест: tutor/coach/mixed — усі WAV ✔
- **Голоси по режимах (+ SHA-256 у `models/drama3-voices-MANIFEST.json`):**
  - tutor: `tutor.wav` — 👩‍🏫 Mira, тепла жіноча, чітка й підбадьорлива
  - coach: `coach.wav` — 🧑‍🏫 співрозмовник, розслаблений чоловічий, природний
  - mixed: `mixed.wav` — 🌐 двомовний оповідач
  - UI: селект голосів показує ці набори з тонами лише для fishdrama; `test_voice` має параметр `mode`; позначка AI-голосу динамічна.
- **Кеш** `tts.py` тепер включає `mode` у ключ.
- **Наголоси:** підтверджено за документацією API — фонемні теги Drama 3 підтримують лише en (Arpabet), zh (pinyin), ja (romaji) → автоматичних виправлень uk-наголосів не буде. Рішення: supertonic лишається за замовчуванням; для fishdrama bake-off потрібне саме сліпе слухання.

## 2026-10-19 — Ліцензія Drama 3 прочитана (крок 1 плану, пункт 2)

- **Джерело:**

- **Джерело:** `https://huggingface.co/fishaudio/drama-3` → `LICENSE` = **Fish Audio Community License, Version 1.0 (від 13.10.2026)**.
- **Висновок:** Research і Non-Commercial (зокрема personal/hobbyist use) — **безкоштовно, без обмежень на MAU**. Комерція дозволена, поки Annual Revenue < **USD 500 000**; понад поріг або «Hosted Service» для третіх сторін — окремий договір із Fish Audio. Governed by California law. S2-Pro ваги лишаються під окремим Research License (на Drama 3 не поширюється).
- **Для MiraSpeak** (особистий навчальний застосунок): **ліцензія сумісна**. Позначка «голос згенеровано ШІ» у UI — залишається вимогою брифу (OpenRAIL-звичай для Supertonic), для FACL не є обов'язковою, але корисною.
- **Ризик «розбіжності» model card знято:** YAML-шапка вказує `license_link: LICENSE.md`, але фактичний файл `LICENSE` — Community License v1.0; research-license застосовується лише до S2-Pro.
