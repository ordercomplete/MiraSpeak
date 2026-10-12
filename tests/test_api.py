from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_meta():
    r = client.get("/api/meta")
    data = r.json()
    assert "A1" in data["levels"]
    assert len(data["scenarios"]) >= 5


def test_prompt_builder():
    from app.services.prompt import build_system_prompt
    p = build_system_prompt("A2", "shopping")
    assert "elementary" in p and "market" in p
    assert build_system_prompt("XX", "unknown")  # фолбек на B1/free talk не падає
