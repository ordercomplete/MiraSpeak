import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from app.core.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    scenario TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    score INTEGER            -- 0..100, заповнюється рев'ю (Блок 8)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    role TEXT NOT NULL,      -- user | assistant
    content TEXT NOT NULL,
    correction TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,   -- форма слова (lowercase)
    translation TEXT DEFAULT '',
    example TEXT DEFAULT '',
    ease REAL DEFAULT 2.5,       -- SM-2
    interval INTEGER DEFAULT 0,  -- днів
    reps INTEGER DEFAULT 0,
    due_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS progress (
    day TEXT PRIMARY KEY,        -- YYYY-MM-DD
    turns INTEGER DEFAULT 0,     -- кількість ходів
    words_added INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS curriculum_progress (
    unit_id TEXT PRIMARY KEY,        -- id юніта з curriculum.py
    level TEXT NOT NULL,             -- A1 | A2
    status TEXT NOT NULL DEFAULT 'new',  -- new | in_progress | completed
    best_score INTEGER DEFAULT 0,    -- найкращий % останніх тестів
    attempts INTEGER DEFAULT 0,      -- скільки разів проходили тест
    last_attempt_at TEXT,
    completed_at TEXT
);
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id TEXT NOT NULL,
    score_percent INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    total INTEGER NOT NULL,
    passed INTEGER NOT NULL,         -- 0/1
    details TEXT,                    -- JSON з per_question
    created_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _db_file():
    # settings.database_path може бути відносним ("data/...") або абсолютним (у тестах).
    # pathlib: Path('/abs') / '/other/abs' => '/other/abs' — саме те, що треба.
    return settings.base_dir / settings.database_path


@contextmanager
def get_conn():
    conn = sqlite3.connect(_db_file())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# --- сесії та повідомлення ---
def create_session(level: str, scenario: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO sessions (level, scenario, started_at) VALUES (?, ?, ?)",
            (level, scenario, _now()),
        )
        return cur.lastrowid


def ensure_open_session(level: str, scenario: str) -> int:
    """Автозбереження чатів: повертає останню відкриту сесію з тим самим
    рівнем/сценарієм (останні 24 год) або створює нову. Фронту не треба думати
    про session_id — кожен хід зберігається автоматично."""
    from datetime import datetime, timedelta, timezone

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(timespec="seconds")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM sessions WHERE level = ? AND scenario = ? "
            "AND ended_at IS NULL AND started_at >= ? ORDER BY id DESC LIMIT 1",
            (level, scenario, cutoff),
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO sessions (level, scenario, started_at) VALUES (?, ?, ?)",
            (level, scenario, _now()),
        )
        return cur.lastrowid


def recent_sessions(limit: int = 20) -> list[dict]:
    """Останні чати для екрана історії: id, рівень, сценарій, час, к-сть реплік."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT s.id, s.level, s.scenario, s.started_at, s.ended_at, "
            "COUNT(m.id) AS turns FROM sessions s "
            "LEFT JOIN messages m ON m.session_id = s.id "
            "GROUP BY s.id ORDER BY s.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def add_message(session_id: int, role: str, content: str, correction: str = "") -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, correction, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, correction, _now()),
        )
        conn.execute(
            "INSERT INTO progress (day, turns) VALUES (?, 1) "
            "ON CONFLICT(day) DO UPDATE SET turns = turns + 1",
            (_now()[:10],),
        )


def get_history(session_id: int, limit: int = 40) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def close_session(session_id: int) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE sessions SET ended_at = ? WHERE id = ?", (_now(), session_id))


# --- словник + SRS (спрощений SM-2) ---
def add_word(word: str, translation: str = "", example: str = "") -> None:
    now = _now()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO words (word, translation, example, due_at, created_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(word) DO NOTHING",
            (word.lower().strip(), translation, example, now, now),
        )
        conn.execute(
            "INSERT INTO progress (day, words_added) VALUES (?, 1) "
            "ON CONFLICT(day) DO UPDATE SET words_added = words_added + 1",
            (now[:10],),
        )


def due_words(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, word, translation, example FROM words WHERE due_at <= ? ORDER BY due_at LIMIT ?",
            (_now(), limit),
        ).fetchall()
    return [dict(r) for r in rows]


def review_word(word_id: int, quality: int) -> None:
    """quality: 0..5 (5 — легко згадав). Спрощений SM-2."""
    quality = max(0, min(5, quality))
    with get_conn() as conn:
        row = conn.execute(
            "SELECT ease, interval, reps FROM words WHERE id = ?", (word_id,)
        ).fetchone()
        if not row:
            return
        ease, interval, reps = row["ease"], row["interval"], row["reps"]
        if quality < 3:
            reps, interval = 0, 1
        else:
            reps += 1
            interval = 1 if reps == 1 else max(1, round(interval * ease))
        ease = max(1.3, ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        due_ordinal = datetime.now(timezone.utc).toordinal() + interval
        conn.execute(
            "UPDATE words SET ease = ?, interval = ?, reps = ?, due_at = ? WHERE id = ?",
            (ease, interval, reps, datetime.fromordinal(due_ordinal).isoformat(), word_id),
        )


def streak() -> int:
    """Кількість поспіль днів з активністю."""
    import datetime as dt
    with get_conn() as conn:
        rows = conn.execute("SELECT day FROM progress ORDER BY day DESC").fetchall()
    days = {r["day"] for r in rows}
    n, cur = 0, dt.date.today()
    while cur.isoformat() in days:
        n += 1
        cur -= dt.timedelta(days=1)
    return n


def progress_summary() -> dict:
    with get_conn() as conn:
        turns = conn.execute("SELECT COALESCE(SUM(turns),0) AS t FROM progress").fetchone()["t"]
        words = conn.execute("SELECT COUNT(*) AS c FROM words").fetchone()["c"]
        sessions = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
    return {"total_turns": turns, "words": words, "sessions": sessions, "streak": streak()}


# --- навчальний план: прогрес по юнітах та історія тестів ---
def record_quiz_attempt(unit_id: str, level: str, result: dict) -> None:
    """Зберігає результат тесту та оновлює прогрес юніта.
    result — вивід curriculum.grade_quiz (score_percent, correct, total, passed, per_question)."""
    import json

    now = _now()
    percent = int(result.get("score_percent", 0))
    passed = 1 if result.get("passed") else 0
    with get_conn() as conn:
        # історія спроб
        conn.execute(
            "INSERT INTO quiz_attempts (unit_id, score_percent, correct, total, passed, details, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (unit_id, percent, int(result.get("correct", 0)), int(result.get("total", 0)),
             passed, json.dumps(result.get("per_question", []), ensure_ascii=False), now),
        )
        # upsert прогресу юніта
        row = conn.execute(
            "SELECT attempts, best_score FROM curriculum_progress WHERE unit_id = ?", (unit_id,)
        ).fetchone()
        if row:
            best = max(row["best_score"], percent)
            attempts = row["attempts"] + 1
            status = "completed" if passed else "in_progress"
            conn.execute(
                "UPDATE curriculum_progress SET level=?, status=?, best_score=?, attempts=?, "
                "last_attempt_at=?, completed_at=COALESCE(completed_at, ?) WHERE unit_id=?",
                (level, status, best, attempts, now, now if passed else None, unit_id),
            )
        else:
            conn.execute(
                "INSERT INTO curriculum_progress (unit_id, level, status, best_score, attempts, "
                "last_attempt_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (unit_id, level, "completed" if passed else "in_progress", percent, 1,
                 now, now if passed else None),
            )


def curriculum_progress() -> dict:
    """Прогрес по юнітах + агрегована статистика навчання."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT unit_id, level, status, best_score, attempts, last_attempt_at, completed_at "
            "FROM curriculum_progress"
        ).fetchall()
        per_unit = {r["unit_id"]: dict(r) for r in rows}
        attempts = conn.execute("SELECT COUNT(*) AS c FROM quiz_attempts").fetchone()["c"]
        completed = conn.execute(
            "SELECT COUNT(*) AS c FROM curriculum_progress WHERE status='completed'"
        ).fetchone()["c"]
        # середній бал по всіх спробах
        avg = conn.execute("SELECT ROUND(AVG(score_percent)) AS a FROM quiz_attempts").fetchone()["a"]
    return {
        "units": per_unit,
        "attempts": attempts,
        "units_completed": completed,
        "avg_score": avg or 0,
    }


def quiz_history(unit_id: str = "", limit: int = 20) -> list[dict]:
    """Останні результати тестів (за наявності unit_id — лише по юніту)."""
    with get_conn() as conn:
        if unit_id:
            rows = conn.execute(
                "SELECT id, unit_id, score_percent, correct, total, passed, created_at "
                "FROM quiz_attempts WHERE unit_id=? ORDER BY id DESC LIMIT ?",
                (unit_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, unit_id, score_percent, correct, total, passed, created_at "
                "FROM quiz_attempts ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


