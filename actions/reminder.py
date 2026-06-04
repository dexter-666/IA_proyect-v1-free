"""reminder.py — Clean reminder & notification system."""
import threading
import time

def reminder(parameters: dict, response=None, player=None) -> str:
    """Set a simple thread-based timer reminder."""
    text = parameters.get("message", "").strip()
    delay_str = str(parameters.get("time", "1m")).lower().strip()
    
    # Calculate delay in seconds
    seconds = 60
    try:
        if delay_str.endswith("s"):
            seconds = int(delay_str[:-1])
        elif delay_str.endswith("m"):
            seconds = int(delay_str[:-1]) * 60
        elif delay_str.endswith("h"):
            seconds = int(delay_str[:-1]) * 3600
        elif delay_str.isdigit():
            seconds = int(delay_str)
    except Exception:
        seconds = 60

    if not text:
        text = "Reminder triggered, sir."
        
    def _run_reminder():
        time.sleep(seconds)
        # Notify
        try:
            import winsound
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except Exception:
            pass
        if player:
            player.write_log(f"⏰ REMINDER: {text}")
            player.speak(f"Sir, I must remind you: {text}")

    threading.Thread(target=_run_reminder, daemon=True).start()
    
    msg = f"Reminder set for '{text}' in {delay_str}."
    if player:
        player.write_log(f"⏰ {msg}")
    return msg
