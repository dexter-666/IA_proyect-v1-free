"""rules_engine.py — Clean phrase-based automation and rules subsystem."""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RULES_PATH = BASE_DIR / "config" / "rules.json"

def rules_engine(parameters: dict, player=None) -> str:
    """Process dynamic rules settings."""
    action = parameters.get("action", "").lower()
    if action == "list":
        rules = _load_rules()
        return f"Currently registered rules: {json.dumps(rules)}"
    return "Rules engine action processed."

def start_rules_runner(player=None, speak=None) -> None:
    """Start background rules listener thread (optional stub)."""
    pass

def _load_rules() -> list[dict]:
    if not RULES_PATH.exists():
        return []
    try:
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def check_phrase_triggers(text: str) -> list[dict]:
    """Check text input against phrase triggers and return matching rule definitions."""
    rules = _load_rules()
    triggered = []
    text_lower = text.lower().strip()
    
    for rule in rules:
        trigger = rule.get("phrase", "").lower().strip()
        if trigger and trigger in text_lower:
            triggered.append(rule)
            
    return triggered

def _run_action(action: dict) -> None:
    """Execute action block of a matching rule in background."""
    print(f"[RulesEngine] Executing rule action: {action}")
