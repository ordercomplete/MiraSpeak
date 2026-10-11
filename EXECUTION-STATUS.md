# MiraSpeak — статус виконання плану

> Автоматично згенеровано `python tools/progress.py report`. Оновлено: 2026-10-12 00:07:17

## Підсумок

| Метрика | Значення |
|---|---|
| **Загальний прогрес** | **13/62 (21%)** ███░░░░░░░░░░░ |
| Синтетичні тести (auto) | 13/51 |
| Фізичні тести користувача (manual) | 0/11 |
| Статуси | ✅ 13 · ❌ 0 · ⛔ 2 · ⏳ 47 |
| Опційні (не впливають на %) | 3 |

## ⛔ Заблоковані (немає передумов)

| ID | Крок | Причина |
|---|---|---|
| B4-4 | інтеграційний синтетичний тест /api/text (LLM відповідає з 📌) | venv не створено — виконай Блок 2, крок 3 |
| B8-3 | pytest — усі тести зелені (синтетичний) | venv не створено — виконай Блок 2, крок 3 |

## ⏳ Далі виконувати

1. `B3-1` [синт] Ollama встановлено (CLI)
2. `B3-2` [синт] Ollama API відповідає (11434)
3. `B3-3` [синт] OLLAMA_MODELS перенесено на D:
4. `B3-4` [синт] LLM-модель за профілем завантажена
5. `B3-5` [синт] модель генерує відповідь (generate)
6. `B3-6` [синт] app/services/stt.py (STTService)
7. `B3-7` [синт] app/services/tts.py (TTSService)
8. `B3-8` [синт] app/services/llm.py (LLMService, провайдери)
9. `B3-9` [синт] усі сервіси разом (services/__init__)
10. `B3-10` [синт] синтетичний LLM-тест (chat → відповідь)

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

### Блок 3 — Налаштування AI-стеку (Ollama + STT + TTS)  (0/14)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B3-1` | синт | Ollama встановлено (CLI) | ⏳ pending |  |  |
| `B3-2` | синт | Ollama API відповідає (11434) | ⏳ pending |  |  |
| `B3-3` | синт | OLLAMA_MODELS перенесено на D: | ⏳ pending |  |  |
| `B3-4` | синт | LLM-модель за профілем завантажена | ⏳ pending |  |  |
| `B3-5` | синт | модель генерує відповідь (generate) | ⏳ pending |  |  |
| `B3-6` | синт | app/services/stt.py (STTService) | ⏳ pending |  |  |
| `B3-7` | синт | app/services/tts.py (TTSService) | ⏳ pending |  |  |
| `B3-8` | синт | app/services/llm.py (LLMService, провайдери) | ⏳ pending |  |  |
| `B3-9` | синт | усі сервіси разом (services/__init__) | ⏳ pending |  |  |
| `B3-10` | синт | синтетичний LLM-тест (chat → відповідь) | ⏳ pending |  |  |
| `B3-11` | синт | синтетичний TTS-тест (EN+UK → data/test_*.mp3) | ⏳ pending |  |  |
| `B3-M1` | ФІЗ | ФІЗИЧНИЙ: прослухати голос Mira EN і UK (жіночий, природність, вимова) | ⏳ pending |  |  |
| `B3-13` | синт | README: розділ AI Stack | ⏳ pending |  |  |
| `B3-14` | синт | git commit «Block 3» | ⏳ pending |  |  |

### Блок 4 — Голосовий пайплайн STT → LLM → TTS  (0/6)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B4-1` | синт | app/services/pipeline.py (оркестратор) | ⏳ pending |  |  |
| `B4-2` | синт | app/api/routes.py (ендпоінти /voice /text /meta) | ⏳ pending |  |  |
| `B4-3` | синт | роутер підключено в main.py | ⏳ pending |  |  |
| `B4-4` | синт | інтеграційний синтетичний тест /api/text (LLM відповідає з 📌) | ⛔ blocked | venv не створено — виконай Блок 2, крок 3 | 2026-10-11 23:35:35 |
| `B4-M1` | ФІЗ | ФІЗИЧНИЙ: /api/voice/sample відтворює вітання Mira у браузері | ⏳ pending |  |  |
| `B4-5` | синт | git commit «Block 4» | ⏳ pending |  |  |

### Блок 5 — Системні промпти, білінгвальність і CEFR  (0/7)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B5-1` | синт | app/services/prompt.py (CEFR + SCENARIOS) | ⏳ pending |  |  |
| `B5-2` | синт | ендпоінт /api/meta віддає рівні та сценарії | ⏳ pending |  |  |
| `B5-3` | синт | синтетичний тест промпта (A2/shopping) | ⏳ pending |  |  |
| `B5-4` | синт | синтетичний тест LLM-формату (відповідь містить 📌) | ⏳ pending |  |  |
| `B5-M1` | ФІЗ | ФІЗИЧНИЙ: білінгвальність на слух — «поясни» → відповідь українською | ⏳ pending |  |  |
| `B5-M2` | ФІЗ | ФІЗИЧНИЙ: рівні CEFR — A1 vs C1 помітно різні за складністю | ⏳ pending |  |  |
| `B5-5` | синт | git commit «Block 5» | ⏳ pending |  |  |

### Блок 6 — MVP інтерфейсу користувача  (0/7)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B6-1` | синт | static/index.html створено (розмітка+стилі+JS) | ⏳ pending |  |  |
| `B6-2` | синт | сервер віддає UI на / | ⏳ pending |  |  |
| `B6-M1` | ФІЗ | ФІЗИЧНИЙ: UI — темна тема, українська, селектор рівнів/сценаріїв | ⏳ pending |  |  |
| `B6-M2` | ФІЗ | ФІЗИЧНИЙ: текстовий чат → голосова відповідь + 📌-виправлення | ⏳ pending |  |  |
| `B6-M3` | ФІЗ | ФІЗИЧНИЙ: мікрофонний цикл (🎙 → транскрипт → відповідь → голос) | ⏳ pending |  |  |
| `B6-M4` | ФІЗ | ФІЗИЧНИЙ: поведінка без мережі (текст без голосу, без помилок) | ⏳ pending |  |  |
| `B6-3` | синт | git commit «Block 6» | ⏳ pending |  |  |

### Блок 7 — Сценарії, прогрес, БД і SRS  (0/8)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B7-1` | синт | app/core/db.py (схема, сесії, SRS, прогрес) | ⏳ pending |  |  |
| `B7-2` | синт | init_db викликається при старті app.main | ⏳ pending |  |  |
| `B7-3` | синт | ендпоінти /api/session, /api/progress працюють | ⏳ pending |  |  |
| `B7-4` | синт | словник: додавання слова та /api/words/due | ⏳ pending |  |  |
| `B7-5` | синт | автономний тест БД+SRS (тимчасова БД) | ⏳ pending |  |  |
| `B7-6` | синт | історія сесії зберігається у SQLite | ⏳ pending |  |  |
| `B7-M1` | ФІЗ | ФІЗИЧНИЙ: після розмови в UI /api/progress збільшує лічильник | ⏳ pending |  |  |
| `B7-7` | синт | data/scenarios.json (опційно, повна версія) *(опц.)* | ⏳ pending |  |  |
| `B7-8` | синт | git commit «Block 7» | ⏳ pending |  |  |

### Блок 8 — Полірування, тестування та реліз  (0/7)

| ID | Тип | Крок | Статус | Результат / вердикт | Коли |
|---|---|---|---|---|---|
| `B8-1` | синт | tests/test_db.py створено | ⏳ pending |  |  |
| `B8-2` | синт | tests/test_api.py створено | ⏳ pending |  |  |
| `B8-3` | синт | pytest — усі тести зелені (синтетичний) | ⛔ blocked | venv не створено — виконай Блок 2, крок 3 | 2026-10-11 23:35:35 |
| `B8-M1` | ФІЗ | ФІЗИЧНИЙ: фінальний чек-лист релізу (п.8 Блока 8) | ⏳ pending |  |  |
| `B8-M2` | ФІЗ | ФІЗИЧНИЙ: профіль low (6 GB) — повний хід 4–8 с *(опц.)* | ⏳ pending |  |  |
| `B8-4` | синт | README оновлено (профілі, провайдери, обмеження) | ⏳ pending |  |  |
| `B8-5` | синт | Dockerfile (опційно, повна версія) *(опц.)* | ⏳ pending |  |  |
| `B8-6` | синт | тег v0.1.0 поставлено | ⏳ pending |  |  |
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
