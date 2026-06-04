"""computer_control.py — Basic native computer controls (keyboard, mouse, typing)."""
import os
import time
import pyautogui
import pyperclip

def computer_control(parameters: dict, player=None) -> str:
    """
    Direct computer control: type, click, scroll.
    """
    action = parameters.get("action", "").lower().strip()
    text = parameters.get("text", "")
    key = parameters.get("key", "")
    keys = parameters.get("keys", "")
    
    if not action:
        return "Error: No se especificó ninguna acción en computer_control."

    try:
        if action == "type" or action == "smart_type":
            if not text:
                return "Error: No se proporcionó texto."
            pyperclip.copy(text)
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "v")
            msg = f"Texto escrito físicamente en pantalla: '{text}'."

        elif action == "press":
            pyautogui.press(key)
            msg = f"Tecla '{key}' presionada."

        elif action == "hotkey":
            k_list = [k.strip().lower() for k in keys.replace(",", "+").split("+")]
            pyautogui.hotkey(*k_list)
            msg = f"Atajo de teclado ejecutado: {keys}."

        elif action == "click":
            pyautogui.click()
            msg = "Clic izquierdo realizado."

        elif action == "scroll":
            pyautogui.scroll(-300)
            msg = f"Scroll hacia abajo realizado."

        elif action == "copy":
            pyautogui.hotkey("ctrl", "c")
            msg = "Comando copiar ejecutado."

        elif action == "paste":
            pyautogui.hotkey("ctrl", "v")
            msg = "Comando pegar ejecutado."

        else:
            msg = f"Acción '{action}' no soportada o limitada en esta versión."

        if player:
            player.write_log(f"💻 Control: {msg}")
        return msg

    except Exception as e:
        err_msg = f"Error al ejecutar control del PC: {str(e)}"
        if player:
            player.write_log(f"⚠️ {err_msg}")
        return err_msg
