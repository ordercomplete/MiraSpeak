import pytest
from app.core import db
from app.core.config import settings


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    db.init_db()


def test_session_and_messages():
    sid = db.create_session("A2", "shopping")
    db.add_message(sid, "user", "How much is it?")
    db.add_message(sid, "assistant", "It costs five dollars.", "📌 How much is it?")
    hist = db.get_history(sid)
    assert len(hist) == 2
    assert hist[0]["role"] == "user"


def test_srs_flow():
    db.add_word("gist", "зміст", "I didn't catch the gist of it.")
    due = db.due_words()
    assert due and due[0]["word"] == "gist"
    db.review_word(due[0]["id"], quality=5)   # легко згадав → інтервал > 0
    with db.get_conn() as conn:
        row = conn.execute("SELECT interval, reps FROM words WHERE word='gist'").fetchone()
    assert row["reps"] == 1 and row["interval"] >= 1


def test_progress_summary():
    sid = db.create_session("B1", "free talk")
    db.add_message(sid, "user", "hi")
    s = db.progress_summary()
    assert s["sessions"] == 1 and s["total_turns"] >= 1
    assert s["streak"] >= 1
