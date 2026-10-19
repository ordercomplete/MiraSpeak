"""User runtime settings stored in data/user_settings.json.

Override config defaults WITHOUT server restart (e.g. TTS voice selection).
Keys are flat strings; unknown keys are ignored on load to survive renames.
"""
import json
import threading
from typing import Any

from app.core.config import settings
from app.services.prompt import COACH_TEMPLATE

_LOCK = threading.Lock()
_PATH = settings.base_dir / "data" / "user_settings.json"

# Defaults mirror app/core/config.py (single source for TTS knobs).
# Unknown keys are ignored on load to survive renames.
_DEFAULTS: dict[str, Any] = {
    "tts_provider": "supertonic",
    "supertonic_voice": "F1",
    "supertonic_speed": 1.05,
    # Шаблон коуча (режим "Коуч") — може бути змінений користувачем у налаштуваннях.
    "coach_template": COACH_TEMPLATE,
    # Значення за замовчуванням для нового чату (бронюються у localStorage фронтом).
    "default_level": "B1",
    "default_scenario": "free talk",
    "default_mode": "tutor",
    "default_target_lang": "en",
}


def load() -> dict[str, Any]:
    data = dict(_DEFAULTS)
    if _PATH.exists():
        try:
            raw = json.loads(_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for k in _DEFAULTS:
                    if k in raw:
                        data[k] = raw[k]
        except (json.JSONDecodeError, OSError):
            pass  # corrupt file -> defaults
    return data


def save(updates: dict[str, Any]) -> dict[str, Any]:
    with _LOCK:
        data = load()
        for k in _DEFAULTS:
            if k in updates and updates[k] is not None:
                data[k] = updates[k]
        _PATH.parent.mkdir(parents=True, exist_ok=True)
        _PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def get(key: str) -> Any:
    return load().get(key, _DEFAULTS.get(key))
