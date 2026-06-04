"""spotify_control.py — Clean Spotify/Media controller using Windows API hooks."""
import time

def spotify_control(parameters: dict, player=None) -> str:
    """Control Spotify or generic active media playback using Windows API commands."""
    action = parameters.get("action", "").lower().strip()
    if not action:
        return "Action parameter is required."
        
    try:
        import pyautogui
        
        if action in ("play", "pause", "toggle"):
            pyautogui.press("playpause")
            msg = "Media playback toggled."
        elif action in ("next", "skip"):
            pyautogui.press("nexttrack")
            msg = "Skipped to next track."
        elif action in ("prev", "previous", "back"):
            pyautogui.press("prevtrack")
            msg = "Returned to previous track."
        elif action == "volume":
            value = parameters.get("value", "")
            if "up" in str(value).lower():
                pyautogui.press("volumeup", presses=5)
                msg = "Volume increased."
            elif "down" in str(value).lower():
                pyautogui.press("volumedown", presses=5)
                msg = "Volume decreased."
            else:
                msg = f"Volume adjust requires relative direction: {value}"
        else:
            msg = f"Action '{action}' not recognized, sir."
            
        if player:
            player.write_log(f"🎵 Spotify: {msg}")
        return msg
    except Exception as e:
        return f"Error executing media control action: {e}"
