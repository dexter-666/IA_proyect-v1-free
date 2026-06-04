"""config_manager.py — API key configuration manager."""
import sys
import json
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "api_keys.json"

def ensure_config_dir() -> None:
    """Ensure that the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def config_exists() -> bool:
    """Return True if the api_keys.json configuration file exists."""
    return CONFIG_FILE.exists()

def is_configured() -> bool:
    """Return True if the keys are set up correctly."""
    try:
        if not config_exists():
            return False
        keys = load_api_keys()
        return bool(keys.get("gemini_api_key"))
    except Exception:
        return False

def load_api_keys() -> dict[str, str]:
    """Load configuration keys from JSON file."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_api_keys(keys: dict[str, str]) -> None:
    """Save configuration keys to JSON file."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(keys, indent=2), encoding="utf-8")

def get_gemini_key() -> str:
    """Get the active Gemini API key."""
    return load_api_keys().get("gemini_api_key", "")
