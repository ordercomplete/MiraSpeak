# MiraSpeak — статус виконання плану

> Автоматично згенеровано `python tools/progress.py report`. Оновлено: 2026-10-12 22:31:59

## Підсумок

| Метрика | Значення |
|---|---|
| **Загальний прогрес** | **52/63 (83%)** ████████████░░ |
| Синтетичні тести (auto) | 52/52 |
| Фізичні тести користувача (manual) | 0/11 |
| Статуси | ✅ 52 · ❌ 0 · ⛔ 0 · ⏳ 11 |
| Опційні (не впливають на %) | 3 |

## ⏳ Далі виконувати

1. `B3-M1` [**ФІЗ**] ФІЗИЧНИЙ: прослухати голос Mira EN і UK (жіночий, природність, вимова)
2. `B4-M1` [**ФІЗ**] ФІЗИЧНИЙ: /api/voice/sample відтворює вітання Mira у браузері
3. `B5-M1` [**ФІЗ**] ФІЗИЧНИЙ: білінгвальність на слух — «поясни» → відповідь українською
4. `B5-M2` [**ФІЗ**] ФІЗИЧНИЙ: рівні CEFR — A1 vs C1 помітно різні за складністю
5. `B6-M1` [**ФІЗ**] ФІЗИЧНИЙ: UI — темна тема, українська, селектор рівнів/сценаріїв
6. `B6-M2` [**ФІЗ**] ФІЗИЧНИЙ: текстовий чат → голосова відповідь + 📌-виправлення
7. `B6-M3` [**ФІЗ**] ФІЗИЧНИЙ: мікрофонний цикл (🎙 → транскрипт → відповідь → голос)
8. `B6-M4` [**ФІЗ**] ФІЗИЧНИЙ: поведінка без мережі (текст без голосу, без помилок)
9. `B7-M1` [**ФІЗ**] ФІЗИЧНИЙ: після розмови в UI /api/progress збільшує лічильник
10. `B7-7` [синт] data/scenarios.json (опційно, повна версія) *(опц.)*

## Деталізація по блоках

### Блок 2 — Підготовка середовища та базової структури  (13/13)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B2-1` | синт | git init у корені проєкту | ✅ pass | OK (0.01 с) | 2026-10-12 00:07:15 |
| `B2-2` | синт | .gitignore створено | ✅ pass | OK (0.06 с) | 2026-10-12 00:07:15 |
| `B2-3` | синт | venv на Python 3.12 | ✅ pass | OK (0.02 с) | 2026-10-12 00:07:15 |
| `B2-4` | синт | requirements.txt (pydantic-settings, httpx, pytest) | ✅ pass | OK (0.05 с) | 2026-10-12 00:07:15 |
| `B2-5` | синт | залежності встановлено (pip check) | ✅ pass | OK (0.36 с) | 2026-10-12 00:07:16 |
| `B2-6` | синт | структура папок app/…, data, static, tests | ✅ pass | OK (0.05 с) | 2026-10-12 00:07:16 |
| `B2-7` | синт | порожні __init__.py на місці | ✅ pass | OK (0.05 с) | 2026-10-12 00:07:16 |
| `B2-8` | синт | .env з провайдерами та профілем | ✅ pass | OK (0.06 с) | 2026-10-12 00:07:16 |
| `B2-9` | синт | app/core/config.py імпортується | ✅ pass | OK (0.19 с) | 2026-10-12 00:07:16 |
| `B2-10` | синт | app/main.py імпортується (FastAPI app) | ✅ pass | OK (0.31 с) | 2026-10-12 00:07:16 |
| `B2-11` | синт | README.md створено | ✅ pass | OK (0.05 с) | 2026-10-12 00:07:16 |
| `B2-12` | синт | сервер запускається, /api/health → ok | ✅ pass | OK (0.27 с) | 2026-10-12 00:07:17 |
| `B2-13` | синт | git commit «Block 2» | ✅ pass | OK (0.03 с) | 2026-10-12 00:07:17 |

### Блок 3 — Налаштування AI-стеку (Ollama + STT + TTS)  (14/15)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B3-1` | синт | Ollama встановлено (CLI) | ✅ pass | OK (0.08 с) | 2026-10-12 00:25:01 |
| `B3-2` | синт | Ollama API відповідає (11434) | ✅ pass | OK (0.28 с) | 2026-10-12 00:25:01 |
| `B3-3` | синт | OLLAMA_MODELS перенесено на D: | ✅ pass | OK (0.14 с) | 2026-10-12 00:25:02 |
| `B3-4` | синт | LLM-модель за профілем завантажена | ✅ pass | OK (0.42 с) | 2026-10-12 00:33:24 |
| `B3-5` | синт | модель генерує відповідь (generate) | ✅ pass | OK (4.45 с) | 2026-10-12 00:33:28 |
| `B3-6` | синт | app/services/stt.py (STTService) | ✅ pass | OK (0.81 с) | 2026-10-12 00:34:46 |
| `B3-7` | синт | app/services/tts.py (TTSService) | ✅ pass | OK (0.81 с) | 2026-10-12 00:34:47 |
| `B3-8` | синт | app/services/llm.py (LLMService, провайдери) | ✅ pass | OK (0.77 с) | 2026-10-12 00:34:47 |
| `B3-9` | синт | усі сервіси разом (services/__init__) | ✅ pass | OK (0.75 с) | 2026-10-12 00:34:48 |
| `B3-10` | синт | синтетичний LLM-тест (chat → відповідь) | ✅ pass | OK (4.34 с) | 2026-10-12 00:34:59 |
| `B3-11` | синт | синтетичний TTS-тест (EN+UK → data/test_*.mp3) | ✅ pass | OK (5.61 с) | 2026-10-12 00:35:05 |
| `B3-12` | синт | синтетичний STT-тест (розпізнавання аудіо → текст) | ✅ pass | OK (1.7 с) | 2026-10-12 21:52:02 |
| `B3-M1` | ФІЗ | ФІЗИЧНИЙ: прослухати голос Mira EN і UK (жіночий, природність, вимова) | ⏳ pending |  |  |
| `B3-13` | синт | README: розділ AI Stack | ✅ pass | OK (0.05 с) | 2026-10-12 01:14:37 |
| `B3-14` | синт | git commit «Block 3» | ✅ pass | OK (0.03 с) | 2026-10-12 01:14:50 |

### Блок 4 — Голосовий пайплайн STT → LLM → TTS  (5/6)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B4-1` | синт | app/services/pipeline.py (оркестратор) | ✅ pass | OK (0.72 с) | 2026-10-12 22:00:38 |
| `B4-2` | синт | app/api/routes.py (ендпоінти /voice /text /meta) | ✅ pass | OK (0.89 с) | 2026-10-12 22:00:39 |
| `B4-3` | синт | роутер підключено в main.py | ✅ pass | OK (1.16 с) | 2026-10-12 22:02:53 |
| `B4-4` | синт | інтеграційний синтетичний тест /api/text (LLM відповідає з 📌) | ✅ pass | OK (24.02 с) | 2026-10-12 22:04:04 |
| `B4-M1` | ФІЗ | ФІЗИЧНИЙ: /api/voice/sample відтворює вітання Mira у браузері | ⏳ pending |  |  |
| `B4-5` | синт | git commit «Block 4» | ✅ pass | OK (0.05 с) | 2026-10-12 22:05:46 |

### Блок 5 — Системні промпти, білінгвальність і CEFR  (5/7)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B5-1` | синт | app/services/prompt.py (CEFR + SCENARIOS) | ✅ pass | OK (1.03 с) | 2026-10-12 22:26:25 |
| `B5-2` | синт | ендпоінт /api/meta віддає рівні та сценарії | ✅ pass | OK (0.39 с) | 2026-10-12 22:26:46 |
| `B5-3` | синт | синтетичний тест промпта (A2/shopping) | ✅ pass | OK (0.94 с) | 2026-10-12 22:26:26 |
| `B5-4` | синт | синтетичний тест LLM-формату (відповідь містить 📌) | ✅ pass | OK (17.8 с) | 2026-10-12 22:30:19 |
| `B5-M1` | ФІЗ | ФІЗИЧНИЙ: білінгвальність на слух — «поясни» → відповідь українською | ⏳ pending |  |  |
| `B5-M2` | ФІЗ | ФІЗИЧНИЙ: рівні CEFR — A1 vs C1 помітно різні за складністю | ⏳ pending |  |  |
| `B5-5` | синт | git commit «Block 5» | ✅ pass | OK (0.05 с) | 2026-10-12 22:31:13 |

### Блок 6 — MVP інтерфейсу користувача  (3/7)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B6-1` | синт | static/index.html створено (розмітка+стилі+JS) | ✅ pass | OK (0.06 с) | 2026-10-12 22:30:46 |
| `B6-2` | синт | сервер віддає UI на / | ✅ pass | OK (0.36 с) | 2026-10-12 22:27:19 |
| `B6-M1` | ФІЗ | ФІЗИЧНИЙ: UI — темна тема, українська, селектор рівнів/сценаріїв | ⏳ pending |  |  |
| `B6-M2` | ФІЗ | ФІЗИЧНИЙ: текстовий чат → голосова відповідь + 📌-виправлення | ⏳ pending |  |  |
| `B6-M3` | ФІЗ | ФІЗИЧНИЙ: мікрофонний цикл (🎙 → транскрипт → відповідь → голос) | ⏳ pending |  |  |
| `B6-M4` | ФІЗ | ФІЗИЧНИЙ: поведінка без мережі (текст без голосу, без помилок) | ⏳ pending |  |  |
| `B6-3` | синт | git commit «Block 6» | ✅ pass | OK (0.03 с) | 2026-10-12 22:31:17 |

### Блок 7 — Сценарії, прогрес, БД і SRS  (7/8)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B7-1` | синт | app/core/db.py (схема, сесії, SRS, прогрес) | ✅ pass | OK (0.25 с) | 2026-10-12 22:26:26 |
| `B7-2` | синт | init_db викликається при старті app.main | ✅ pass | OK (1.06 с) | 2026-10-12 22:26:27 |
| `B7-3` | синт | ендпоінти /api/session, /api/progress працюють | ✅ pass | OK (0.5 с) | 2026-10-12 22:28:09 |
| `B7-4` | синт | словник: додавання слова та /api/words/due | ✅ pass | OK (0.5 с) | 2026-10-12 22:28:10 |
| `B7-5` | синт | автономний тест БД+SRS (тимчасова БД) | ✅ pass | OK (0.3 с) | 2026-10-12 22:26:28 |
| `B7-6` | синт | історія сесії зберігається у SQLite | ✅ pass | OK (0.27 с) | 2026-10-12 22:26:28 |
| `B7-M1` | ФІЗ | ФІЗИЧНИЙ: після розмови в UI /api/progress збільшує лічильник | ⏳ pending |  |  |
| `B7-7` | синт | data/scenarios.json (опційно, повна версія) *(опц.)* | ⏳ pending |  |  |
| `B7-8` | синт | git commit «Block 7» | ✅ pass | OK (0.03 с) | 2026-10-12 22:31:21 |

### Блок 8 — Полірування, тестування та реліз  (5/7)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B8-1` | синт | tests/test_db.py створено | ✅ pass | OK (0.06 с) | 2026-10-12 22:26:28 |
| `B8-2` | синт | tests/test_api.py створено | ✅ pass | OK (0.06 с) | 2026-10-12 22:26:28 |
| `B8-3` | синт | pytest — усі тести зелені (синтетичний) | ✅ pass | OK (1.77 с) | 2026-10-12 22:26:30 |
| `B8-M1` | ФІЗ | ФІЗИЧНИЙ: фінальний чек-лист релізу (п.8 Блока 8) | ⏳ pending |  |  |
| `B8-M2` | ФІЗ | ФІЗИЧНИЙ: профіль low (6 GB) — повний хід 4–8 с *(опц.)* | ⏳ pending |  |  |
| `B8-4` | синт | README оновлено (профілі, провайдери, обмеження) | ✅ pass | OK (0.12 с) | 2026-10-12 22:31:54 |
| `B8-5` | синт | Dockerfile (опційно, повна версія) *(опц.)* | ✅ pass | OK (0.11 с) | 2026-10-12 22:31:54 |
| `B8-6` | синт | тег v0.1.0 поставлено | ✅ pass | OK (0.03 с) | 2026-10-12 22:31:59 |
| `FINAL-M1` | ФІЗ | ФІЗИЧНИЙ: приймальна сесія — 5-хвилинна вільна розмова з Mira | ⏳ pending |  |  |

## Виводи синтетичних тестів

<details><summary><code>B2-1</code> — git init у корені проєкту (✅)</summary>

```
true
```
</details>

<details><summary><code>B2-2</code> — .gitignore створено (✅)</summary>

```
True
```
</details>

<details><summary><code>B2-3</code> — venv на Python 3.12 (✅)</summary>

```
Python 3.12.9
```
</details>

<details><summary><code>B2-4</code> — requirements.txt (pydantic-settings, httpx, pytest) (✅)</summary>

```
missing: []
```
</details>

<details><summary><code>B2-5</code> — залежності встановлено (pip check) (✅)</summary>

```
No broken requirements found.
```
</details>

<details><summary><code>B2-6</code> — структура папок app/…, data, static, tests (✅)</summary>

```
missing: []
```
</details>

<details><summary><code>B2-7</code> — порожні __init__.py на місці (✅)</summary>

```
missing: []
```
</details>

<details><summary><code>B2-8</code> — .env з провайдерами та профілем (✅)</summary>

```
True
```
</details>

<details><summary><code>B2-9</code> — app/core/config.py імпортується (✅)</summary>

```
high llama3.1:8b
```
</details>

<details><summary><code>B2-10</code> — app/main.py імпортується (FastAPI app) (✅)</summary>

```
MiraSpeak
```
</details>

<details><summary><code>B2-11</code> — README.md створено (✅)</summary>

```
True
```
</details>

<details><summary><code>B2-12</code> — сервер запускається, /api/health → ok (✅)</summary>

```
{"status":"ok","version":"0.2.0","llm_provider":"ollama","model":"llama3.1:8b","profile":"high"}
```
</details>

<details><summary><code>B2-13</code> — git commit «Block 2» (✅)</summary>

```
Block 2: project scaffold
```
</details>

<details><summary><code>B3-1</code> — Ollama встановлено (CLI) (✅)</summary>

```
ollama version is 0.34.4
```
</details>

<details><summary><code>B3-2</code> — Ollama API відповідає (11434) (✅)</summary>

```
{"models":[]}
```
</details>

<details><summary><code>B3-3</code> — OLLAMA_MODELS перенесено на D: (✅)</summary>

```
D:\models\ollama
```
</details>

<details><summary><code>B3-4</code> — LLM-модель за профілем завантажена (✅)</summary>

```
want: llama3.1:8b have: ['llama3.1:8b']
```
</details>

<details><summary><code>B3-5</code> — модель генерує відповідь (generate) (✅)</summary>

```
OK
```
</details>

<details><summary><code>B3-6</code> — app/services/stt.py (STTService) (✅)</summary>

```
stt ok
```
</details>

<details><summary><code>B3-7</code> — app/services/tts.py (TTSService) (✅)</summary>

```
tts ok
```
</details>

<details><summary><code>B3-8</code> — app/services/llm.py (LLMService, провайдери) (✅)</summary>

```
llm ok: ollama
```
</details>

<details><summary><code>B3-9</code> — усі сервіси разом (services/__init__) (✅)</summary>

```
Services OK
```
</details>

<details><summary><code>B3-10</code> — синтетичний LLM-тест (chat → відповідь) (✅)</summary>

```
Hello
```
</details>

<details><summary><code>B3-11</code> — синтетичний TTS-тест (EN+UK → data/test_*.mp3) (✅)</summary>

```
TTS OK
```
</details>

<details><summary><code>B3-12</code> — синтетичний STT-тест (розпізнавання аудіо → текст) (✅)</summary>

```
TEXT: 'Hello, I am Mira'
DEVICE: cuda
STT OK
```
</details>

<details><summary><code>B3-13</code> — README: розділ AI Stack (✅)</summary>

```
True
```
</details>

<details><summary><code>B3-14</code> — git commit «Block 3» (✅)</summary>

```
Block 3: AI stack (STT/LLM/TTS)
```
</details>

<details><summary><code>B4-1</code> — app/services/pipeline.py (оркестратор) (✅)</summary>

```
pipeline ok
```
</details>

<details><summary><code>B4-2</code> — app/api/routes.py (ендпоінти /voice /text /meta) (✅)</summary>

```
['/api/meta', '/api/text', '/api/voice', '/api/voice/sample']
```
</details>

<details><summary><code>B4-3</code> — роутер підключено в main.py (✅)</summary>

```
['/', '/api/health', '/api/meta', '/api/text', '/api/voice', '/api/voice/sample']
```
</details>

<details><summary><code>B4-4</code> — інтеграційний синтетичний тест /api/text (LLM відповідає з 📌) (✅)</summary>

```
200 {"reply_text":"That's nice! What's your friend's name? Do you like to see him at school?","reply_spoken":"That's nice! What's your friend's name? Do you like to see him at school?","correction":"","audio_b64":"//NkxAAAAANIAAAAAExBTUVVVVUgNkBhRi0+5CI54DWYg2dyabEEKiIezEOYQy4ldyQg4GBsAF+7xC30RC66JXd3BC
```
</details>

<details><summary><code>B4-5</code> — git commit «Block 4» (✅)</summary>

```
Block 4: voice pipeline API (STT->LLM->TTS orchestrator + REST endpoints)
```
</details>

<details><summary><code>B5-1</code> — app/services/prompt.py (CEFR + SCENARIOS) (✅)</summary>

```
6 7
```
</details>

<details><summary><code>B5-2</code> — ендпоінт /api/meta віддає рівні та сценарії (✅)</summary>

```
['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
```
</details>

<details><summary><code>B5-3</code> — синтетичний тест промпта (A2/shopping) (✅)</summary>

```
True True
```
</details>

<details><summary><code>B5-4</code> — синтетичний тест LLM-формату (відповідь містить 📌) (✅)</summary>

```
len 89 haspin True
```
</details>

<details><summary><code>B5-5</code> — git commit «Block 5» (✅)</summary>

```
Block 5: prompts, CEFR, bilingual rules
```
</details>

<details><summary><code>B6-1</code> — static/index.html створено (розмітка+стилі+JS) (✅)</summary>

```
missing: []
```
</details>

<details><summary><code>B6-2</code> — сервер віддає UI на / (✅)</summary>

```
200 6627
```
</details>

<details><summary><code>B6-3</code> — git commit «Block 6» (✅)</summary>

```
Block 6: MVP UI (static/index.html)
```
</details>

<details><summary><code>B7-1</code> — app/core/db.py (схема, сесії, SRS, прогрес) (✅)</summary>

```
True True True
```
</details>

<details><summary><code>B7-2</code> — init_db викликається при старті app.main (✅)</summary>

```
D:\GEN\MiraSpeak\data\miraspeak.db True
```
</details>

<details><summary><code>B7-3</code> — ендпоінти /api/session, /api/progress працюють (✅)</summary>

```
200 {"total_turns":0,"words":0,"sessions":1,"streak":0}
```
</details>

<details><summary><code>B7-4</code> — словник: додавання слова та /api/words/due (✅)</summary>

```
200 {"words":[{"id":1,"word":"miraspeak-test","translation":"����","example":""}]}
```
</details>

<details><summary><code>B7-5</code> — автономний тест БД+SRS (тимчасова БД) (✅)</summary>

```
{'total_turns': 1, 'words': 1, 'sessions': 1, 'streak': 1}
```
</details>

<details><summary><code>B7-6</code> — історія сесії зберігається у SQLite (✅)</summary>

```
2 user
```
</details>

<details><summary><code>B7-8</code> — git commit «Block 7» (✅)</summary>

```
Block 7: DB, SRS, progress (sessions, words, SM-2)
```
</details>

<details><summary><code>B8-1</code> — tests/test_db.py створено (✅)</summary>

```
True
```
</details>

<details><summary><code>B8-2</code> — tests/test_api.py створено (✅)</summary>

```
True
```
</details>

<details><summary><code>B8-3</code> — pytest — усі тести зелені (синтетичний) (✅)</summary>

```
......                                                                   [100%]
6 passed in 1.26s
```
</details>

<details><summary><code>B8-4</code> — README оновлено (профілі, провайдери, обмеження) (✅)</summary>

```
True
```
</details>

<details><summary><code>B8-5</code> — Dockerfile (опційно, повна версія) (✅)</summary>

```
True
```
</details>

<details><summary><code>B8-6</code> — тег v0.1.0 поставлено (✅)</summary>

```
v0.1.0
```
</details>
