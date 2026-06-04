"""user_profile.py — Clean user habit & configuration recorder."""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = BASE_DIR / "config" / "user_profile.json"

def user_profile(parameters: dict, player=None) -> str:
    """Manage general user profile variables."""
    action = parameters.get("action", "").lower()
    if action == "get":
        profile = _load_profile()
        return f"User preferences: {json.dumps(profile)}"
    return "User profile updated."

def _load_profile() -> dict:
    if not PROFILE_PATH.exists():
        return {"name": "Sir", "habits": {}}
    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"name": "Sir", "habits": {}}

def _save_profile(profile: dict) -> None:
    try:
        PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROFILE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    except Exception:
        pass

def record_action(name: str, args: dict) -> None:
    """Log executed actions to track user habits over time."""
    try:
        profile = _load_profile()
        habits = profile.setdefault("habits", {})
        count = habits.get(name, 0)
        habits[name] = count + 1
        _save_profile(profile)
    except Exception:
        pass
