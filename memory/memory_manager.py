"""memory_manager.py — Long-term memory manager."""
import sys
import json
import threading
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
MEMORY_PATH = BASE_DIR / "memory" / "long_term.json"

MAX_VALUE_LENGTH = 500
MEMORY_MAX_CHARS = 4000
_lock = threading.Lock()

def _empty_memory() -> dict:
    return {
        "notes": {},
        "habits": {},
        "preferences": {},
        "context": {}
    }

def load_memory() -> dict:
    """Load long term memory file safely."""
    with _lock:
        if not MEMORY_PATH.exists():
            return _empty_memory()
        try:
            return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return _empty_memory()

def save_memory(memory: dict) -> None:
    """Save the memory state to disk."""
    with _lock:
        try:
            MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
            MEMORY_PATH.write_text(json.dumps(memory, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[Memory] Error saving: {e}")

def _recursive_update(d: dict, u: dict) -> dict:
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _recursive_update(d[k], v)
        else:
            d[k] = v
    return d

def _truncate_value(val: str) -> str:
    if len(val) > MAX_VALUE_LENGTH:
        return val[:MAX_VALUE_LENGTH] + "... [truncated]"
    return val

def _all_entries(mem: dict) -> list[tuple[str, str, str]]:
    entries = []
    for cat, keys in mem.items():
        if not isinstance(keys, dict):
            continue
        for k, v in keys.items():
            if isinstance(v, dict) and "value" in v:
                entries.append((cat, k, str(v["value"])))
            else:
                entries.append((cat, k, str(v)))
    return entries

def _trim_to_limit(mem: dict) -> dict:
    # Estimate size
    entries = _all_entries(mem)
    total_len = sum(len(c) + len(k) + len(v) for c, k, v in entries)
    if total_len <= MEMORY_MAX_CHARS:
        return mem
    
    # Simple FIFO trimming
    while total_len > MEMORY_MAX_CHARS and entries:
        cat, k, _ = entries.pop(0)
        if cat in mem and k in mem[cat]:
            del mem[cat][k]
        entries = _all_entries(mem)
        total_len = sum(len(c) + len(k) + len(v) for c, k, v in entries)
    return mem

def update_memory(updates: dict) -> None:
    """Recursively update the memory with updates, truncating and trimming size limits."""
    mem = load_memory()
    # Apply truncation
    truncated_updates = {}
    for cat, items in updates.items():
        truncated_updates[cat] = {}
        if isinstance(items, dict):
            for k, val_info in items.items():
                if isinstance(val_info, dict) and "value" in val_info:
                    val_str = _truncate_value(str(val_info["value"]))
                    truncated_updates[cat][k] = {"value": val_str}
                else:
                    truncated_updates[cat][k] = _truncate_value(str(val_info))
        else:
            truncated_updates[cat] = items

    mem = _recursive_update(mem, truncated_updates)
    mem = _trim_to_limit(mem)
    save_memory(mem)

def remember(category: str, key: str, value: str) -> None:
    """Store a single memory value."""
    update_memory({category: {key: {"value": value}}})

def forget(category: str, key: str) -> None:
    """Remove a single memory value."""
    mem = load_memory()
    if category in mem and key in mem[category]:
        del mem[category][key]
        save_memory(mem)

def forget_memory() -> None:
    """Clear all memory."""
    save_memory(_empty_memory())

def format_memory_for_prompt(memory: dict) -> str:
    """Format memory dict into a system prompt segment."""
    entries = _all_entries(memory)
    if not entries:
        return ""
    
    lines = ["[LONG-TERM MEMORY & USER CONTEXT]"]
    current_cat = None
    for cat, k, v in sorted(entries, key=lambda x: x[0]):
        if cat != current_cat:
            lines.append(f"\n* {cat.upper()}:")
            current_cat = cat
        lines.append(f"  - {k}: {v}")
    return "\n".join(lines) + "\n"
