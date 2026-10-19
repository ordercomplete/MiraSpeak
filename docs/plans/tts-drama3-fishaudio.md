# План інтеграції TTS-моделі Drama 3 (Fish Audio) як додаткового голосу

> Дата: 19.10.2026. Статус: план, не реалізовано.
> Мова документа — українська. Код, ідентифікатори, коментарі, commit-повідомлення — англійською.
> Контекст правил: `Agent-brief.MD` (offline-first, замінюваність за `TTSProvider`, рішення в `docs/DECISIONS.md`).

---

## Крок 0 (ОБОВ'ЯЗКОВИЙ, ПЕРШИЙ): синхронізація з репозиторієм

**Перед будь-якою роботою з новим матеріалом — завантажити актуальні зміни проєкту:**

```bash
git pull --ff-only
```

- Виконується першим, до зміни будь-якого файлу і до завантаження ваг/залежностей Drama 3.
- Якщо `pull` дає конфлікт — зупинитися, вирішити конфлікти, повторити; далі не працювати на застарілій базі.
- Якщо в робочому дереві є незакомічені зміни — спочатку закомітити/відкласти їх, потім `pull`.
- Логічно також `git fetch` + звірка `git status -sb` (гілка не має бути попереду `origin/main`).

---

## 0. Що з'ясовано (перевірено джерелами станом на 19.10.2026)

**Drama 3 (fishaudio/drama-3, model card + GitHub fishaudio/fish-speech + docs.fish.audio):**
- 35B MoE / ~3B активних на токен; FP8 MoE-експерти + bf16 решта ваг; гібридна увага.
- Теги режисури: `[whisper]`, `[pause]`, `[laughs]`…, парні `<whisper>…</whisper>`, `<emphasis>`, `<soft>`, `<fast>`, `<slow>`, `<stress>`, `<forceful>`; фонемні теги `<|phoneme_start|>…<|phoneme_end|>`.
- Мультиспікер: `<|speaker:0|>` … `<|speaker:15|>` (до 16 персонажів у запиті).
- Мови: у списку model card **є `uk`** (і `en`) — на відміну від S2 Pro, де українська не підтверджена.
- Ліцензія: **Fish Audio Community License** (у YAML шапці model card стоїть `license_name: fish-audio-research-license` — розбіжність із розділом «License»; текст `LICENSE` треба прочитати до завантаження ваг і зафіксувати висновок у `docs/DECISIONS.md`).
- Локальний запуск (офіційно підтримувані шляхи) — **див. `docs/DECISIONS.md` (гейт 19.10.2026 ПРОЙДЕНО, обрано SGLang-Omni + Docker у WSL2):**
  - **SGLang-Omni**: `sgl-omni serve --model-path fishaudio/drama-3 --port 8000`;
  - **vLLM-Omni**: `vllm serve fishaudio/drama-3 --omni --port 8091`;
  - **Ендпоінт SGLang-Omni: `POST /v1/audio/speech`, поле `{"input": "..."}`** (OpenAI-сумісне; формат `/v1/tts` з `{"text": ...}` — це хмарний API fish.audio, не локальний сервер).
- **int4-чекпойнт `fishaudio/drama-3-int4`**: GPTQ 4-bit, ваги **20.8 ГБ замість 37.0 ГБ** (FP8), GPTQ-Marlin вимагає compute capability ≥ 8.0 (RTX 3090 = 8.6 ✔), якість WER на рівні FP8 (таблиця 3 cookbook). **Обрано для цієї машини** — FP8 шлях не підтримується апаратно на Ampere.

**Залізо цієї машини:** 3× RTX 3090, 24 ГБ кожна (72 ГБ сумарно), Windows.

## 1. Критичні ризики (гейти — без їх проходження код не пишемо)

1. **FP8 на RTX 3090 (Ampere, SM 8.6) не підтримується апаратно** (FP8 tensor cores з'явилися в Ada/Hopper). Цифра «48 ГБ у FP8» на цій системі не гарантована; у bf16 ваги ≈70 ГБ — влізають тільки на всі три GPU разом, з мінімальним запасом під KV-cache/вокодер.
2. **Windows**: SGLang-Omni / vLLM-Omni — Linux-орієнтовані стеки. Очікуваний варіант — сервер у **WSL2 або Docker Desktop** на `localhost`. MiraSpeak при цьому лишається offline-first (localhost ≠ зовнішня мережа).
3. **Ліцензія**: Community License може мати некомерційні обмеження / поріг MAU — читати `LICENSE` до завантаження ваг.
4. **Конфлікт VRAM**: Ollama (gemma4:26b) і faster-whisper large-v3-turbo вже ділять ті самі GPU — знадобиться або диспетчеризація, або окремі GPU під TTS-сервер.
5. **Ризик якості uk**: наявність `uk` у списку мов ≠ якість наголосів/апострофа/ґ — перевіряється тільки bake-off (крок 7).

## 2. Кроки інтеграції

### Крок 1 — Доказ запуску (gate) ✔ ВИКОНАНО 19.10.2026 (див. `docs/DECISIONS.md`)
1. `git pull --ff-only` (крок 0). ✔
2. Прочитати `LICENSE` моделі → висновок у `docs/DECISIONS.md`. ✔ (Community License v1.0, non-commercial OK)
3. Підняти SGLang-Omni у Docker/WSL2; виміряти VRAM і квантування. ✔ (int4, 3 GPU, деталі в DECISIONS)
4. Тест-синтез uk + en через `POST /v1/audio/speech`. ✔ (200: uk 2.42 с, en 7.24 с, WAV 44.1 kHz)
5. Невдача → план зупиняється (не спрацювало).

### Крок 2 — Провайдер
- Новий файл `app/services/tts_fishdrama.py`, клас `FishDramaProvider` у стилі `SupertonicProvider`:
  - `available()` — швидкий health-check `http://127.0.0.1:<port>/…` (таймаут ~1 с);
  - `synthesize_sync(text, language, voice=None, speed=None) -> bytes` — `httpx` POST на `http://127.0.0.1:8000/v1/audio/speech` з `{"input": text}` (перевірено працює; для клонування — необов'язкове поле `references: [{audio_path, text}]`), повертає WAV bytes;
  - ліниве завантаження, `threading.Lock` на клієнт, таймаути, будь-яка помилка → виняток (обробляється фолбеком у `tts.py`).
### Крок 3 — Конфіг
- `app/core/config.py`: `fish_tts_base_url` (default `http://127.0.0.1:8000`), `fish_tts_model` (`drama-3`), `fish_tts_reference_id` ("" = без клонування, дефолтний голос), `fish_tts_timeout_s` (default 30).
- `app/core/user_settings._DEFAULTS`: ключі `fish_voice`, `fish_speed` (перевірити сумісність із чинними `supertonic_voice/speed` — можливо уніфікувати під спільні `voice/speed`).
- `.env`: `FISH_TTS_BASE_URL`, `FISH_TTS_MODEL`, `FISH_TTS_REFERENCE_ID`.

### Крок 4 — Маршрутизація
- `app/services/tts.py::synthesize`: гілка `elif provider == "fishdrama":` → `fishdrama_provider.synthesize_sync(...)` через `asyncio.to_thread`, у `try/except` із наявним ланцюжком фолбеків (uk → piper, en → edge/piper, за потреби supertonic).
- Кеш `data/tts_cache` уже враховує `provider|voice|speed` у ключі — окремих дій не треба.

### Крок 5 — API / UI
- `app/api/routes.py`:
  - `GET /api/settings` → `providers` += `fishdrama`; `voices` — список голосів Drama 3 (за наявності `reference_id` з `.env` + «default»);
  - `SettingsSaveRequest` — нові поля `fish_voice` (якщо не уніфіковано);
  - валідація `tts_provider` у `save_settings` (зараз провайдер не валідується — додати множину дозволених);
  - `POST /settings/test_voice` працює без змін (перевіряє поточний провайдер).
- `static/index.html`: селект провайдера вже рендериться з `providers` — новий елемент з'явиться автоматично; додати позначку «голос згенеровано ШІ» для fishdrama (вимога ліцензії/брифу).

### Крок 6 — Тести (pytest)
- `tests/test_tts_fishdrama.py`:
  - мережа заблокована (socket-guard): провайдер із недоступним сервером кидає виняток → `tts_service.synthesize` повертає фолбек-аудіо (mock piper/supertonic);
  - `available()` → False без сервера;
  - коректність побудови payload (мова `uk`/`en`, текст не змінюється).
- `tests/test_api.py` — `GET /api/settings` містить `fishdrama` у `providers`; 200/422 на `save_settings`.
- Прогін: `python -m pytest -q` зелений.

### Крок 7 — Bake-off (ворота якості)
- Розширити `tools/tts_eval` (корпус із `Agent-brief.MD` 1.3): Supertonic 3 vs Drama 3 на uk+en — round-trip WER (Whisper), наголоси, складні слова/числа/імена, сліпі WAV.
- Результат → `docs/DECISIONS.md` (вибір провайдера за замовчуванням — зі схвалення власника; за брифом 3.4 самостійно провайдер не перемикаємо).

## 3. Що НЕ робимо на цьому етапі
- Не змінюємо `TTS_PROVIDER` за замовчуванням (лишається `supertonic`) без запису в `DECISIONS.md` і схвалення власника.
- Не викликаємо хмарний API fish.audio (бриф 3.4: жодних хмарних TTS).
- Не завантажуємо ваги до проходження кроку 1 (ліцензія + VRAM-gate).

## 4. Чекліст DoD
- [x] `git pull --ff-only` виконано першим кроком.
- [x] `LICENSE` прочитано, висновок у `docs/DECISIONS.md`.
- [x] Сервер Drama 3 піднято локально, тест uk+en пройшов, VRAM зафіксовано.
- [ ] `FishDramaProvider` + гілка у `tts.py` + конфіг.
- [ ] `fishdrama` з'явився у `GET /api/settings.providers`, працює тест голосу.
- [ ] Фолбек при недоступному сервері працює; `pytest` зелений; мережа заблокована тестом.
- [ ] Bake-off-прогін, звіт, рішення в `DECISIONS.md`.
