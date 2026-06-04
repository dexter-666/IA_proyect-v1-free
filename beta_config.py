"""beta_config.py — Clean configurations and tool checks."""
from __future__ import annotations
import json
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent
STATE_PATH = BASE_DIR / "config" / "app_state.json"

PRO_TOOLS: set[str] = set()
DAILY_LIMIT = 999999999

def is_pro_tool(tool_name: str) -> bool:
    """Check if the tool is restricted. We maintain all tools accessible by design."""
    return False

def check_daily_limit() -> tuple[bool, int]:
    """Check if the daily execution limit is active. Set to always active/unlimited."""
    return True, 0

def increment_calls() -> int:
    """Increment execution stats if needed."""
    return 0

def pro_tool_message(tool_name: str) -> str:
    """Message when a tool is blocked (never triggered)."""
    return ""

def daily_limit_message(calls: int) -> str:
    """Message when the daily limit is reached (never triggered)."""
    return ""
