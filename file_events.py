"""file_events.py — Clean thread-safe event bus for JARVIS file modifications."""
from __future__ import annotations
import threading
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class FileEvent:
    event_type: str  # 'code' | 'document' | 'image'
    path: str
    content: Any

_handlers: list[Callable[[FileEvent], None]] = []
_lock = threading.Lock()

def subscribe(handler: Callable[[FileEvent], None]) -> None:
    """Subscribe a callback to all file events."""
    with _lock:
        if handler not in _handlers:
            _handlers.append(handler)

def unsubscribe(handler: Callable[[FileEvent], None]) -> None:
    """Unsubscribe a callback from file events."""
    with _lock:
        if handler in _handlers:
            _handlers.remove(handler)

def emit(event: FileEvent) -> None:
    """Broadcast an event to all registered subscribers."""
    with _lock:
        current_handlers = list(_handlers)
    for handler in current_handlers:
        try:
            handler(event)
        except Exception as e:
            print(f"[EventBus] Error dispatching event to {handler.__name__}: {e}")

def emit_code(path: str, code: str) -> None:
    """Convenience method to broadcast code edits."""
    emit(FileEvent(event_type="code", path=path, content=code))

def emit_document(path: str, text: str) -> None:
    """Convenience method to broadcast document changes."""
    emit(FileEvent(event_type="document", path=path, content=text))

def emit_image(path: str, img_data: Any) -> None:
    """Convenience method to broadcast new visual assets or captures."""
    emit(FileEvent(event_type="image", path=path, content=img_data))
