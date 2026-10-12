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

