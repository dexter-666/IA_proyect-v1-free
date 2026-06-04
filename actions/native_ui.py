import time
import pygetwindow as gw
import pyautogui

def native_ui(parameters: dict, player=None) -> str:
    """
    Automatización nativa de la interfaz de Windows (sin usar visión/API).
    Permite listar, enfocar, escribir y hacer clic en ventanas de forma precisa.
    """
    action = parameters.get("action", "")
    window_title = parameters.get("window_title", "")
    text_to_type = parameters.get("text", "")
    
    if action == "list_windows":
        # Lista todas las ventanas abiertas ignorando las ocultas o sin título
        titles = [t for t in gw.getAllTitles() if t.strip()]
        return "Ventanas abiertas:\n" + "\n".join(titles)
        
    elif action == "focus_window":
        if not window_title:
            return "Error: Se requiere el nombre de la ventana (window_title)."
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return f"No se encontró ninguna ventana con el título: '{window_title}'"
        
        win = windows[0]
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            return f"Ventana '{win.title}' enfocada exitosamente."
        except Exception as e:
            return f"Error al intentar enfocar la ventana: {str(e)}"
            
    elif action == "type_in_window":
        if not window_title or not text_to_type:
            return "Error: Se requiere window_title y text."
        
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return f"No se encontró la ventana: '{window_title}'"
            
        win = windows[0]
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5) # Breve pausa para asegurar foco
            
            pyautogui.write(text_to_type, interval=0.01)
            return f"Texto escrito en la ventana '{win.title}'."
        except Exception as e:
            return f"Error al escribir en la ventana: {str(e)}"
            
    elif action == "click_center":
        if not window_title:
            return "Error: Se requiere window_title."
            
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return f"No se encontró la ventana: '{window_title}'"
            
        win = windows[0]
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5)
            
            # Calculamos el centro de la ventana
            cx = win.left + (win.width // 2)
            cy = win.top + (win.height // 2)
            pyautogui.click(cx, cy)
            
            return f"Clic realizado en el centro de la ventana '{win.title}'."
        except Exception as e:
            return f"Error al hacer clic: {str(e)}"
            
    else:
        return f"Acción '{action}' no soportada por native_ui."
