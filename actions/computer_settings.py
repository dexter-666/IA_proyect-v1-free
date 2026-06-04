"""computer_settings.py — Clean Win32/system settings controls."""
import os
import sys

def computer_settings(parameters: dict, response=None, player=None) -> str:
    """Adjust system settings like volume, brightness, or active window states."""
    action = parameters.get("action", "").lower()
    value = parameters.get("value", "")
    
    if action == "volume":
        try:
            import pyautogui
            if str(value).isdigit():
                target = int(value)
                try:
                    from ctypes import cast, POINTER
                    from comtypes import CoInitialize, CoUninitialize
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    CoInitialize()
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
                    volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
                    scalar_vol = max(0.0, min(1.0, target / 100.0))
                    volume_ctrl.SetMasterVolumeLevelScalar(scalar_vol, None)
                    CoUninitialize()
                    msg = f"Master volume adjusted to {target}%."
                except Exception as e:
                    msg = f"Could not set absolute volume: {e}"
            else:
                if "up" in value.lower() or "subir" in value.lower():
                    pyautogui.press("volumeup", presses=5)
                    msg = "Volume increased."
                elif "down" in value.lower() or "bajar" in value.lower():
                    pyautogui.press("volumedown", presses=5)
                    msg = "Volume decreased."
                elif "mute" in value.lower() or "silenciar" in value.lower():
                    pyautogui.press("volumemute")
                    msg = "Volume muted."
                else:
                    msg = f"Unrecognized volume value: {value}"
            if player:
                player.write_log(f"🔊 {msg}")
            return msg
        except Exception as e:
            return f"Failed to adjust volume: {e}"
            
    elif action in ("minimize", "window_minimize"):
        try:
            import pygetwindow as gw
            window = gw.getActiveWindow()
            if window:
                window.minimize()
                return "Active window minimized."
            return "No active window found."
        except Exception as e:
            return f"Failed to minimize window: {e}"

    elif action in ("maximize", "window_maximize"):
        try:
            import pygetwindow as gw
            window = gw.getActiveWindow()
            if window:
                window.maximize()
                return "Active window maximized."
            return "No active window found."
        except Exception as e:
            return f"Failed to maximize window: {e}"

    return f"Settings action '{action}' is not supported yet, sir."
