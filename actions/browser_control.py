import time
import pyautogui
import pygetwindow as gw

def browser_control(parameters: dict, player=None) -> str:
    """
    Controla el navegador activo del usuario (Chrome, Edge, Firefox, etc.) mediante simulación de teclado.
    """
    action = parameters.get("action", "")
    
    # 1. Encontrar el navegador activo
    # Buscamos ventanas que tengan nombres típicos de navegadores
    browser_keywords = ["Chrome", "Edge", "Firefox", "Brave", "Opera"]
    target_window = None
    
    for win in gw.getAllWindows():
        if win.title.strip():
            for kw in browser_keywords:
                if kw.lower() in win.title.lower():
                    target_window = win
                    break
        if target_window:
            break
            
    if not target_window:
        return "No se encontró ningún navegador (Chrome, Edge, Firefox, etc.) abierto en la pantalla."
        
    try:
        # 2. Restaurar y Enfocar la ventana del navegador
        if target_window.isMinimized:
            target_window.restore()
        target_window.activate()
        time.sleep(0.15) # Tiempo para que la ventana tome foco
        
        # 3. Ejecutar la acción mediante atajos de teclado universales
        if action == "go_to":
            url = parameters.get("url", "")
            if not url:
                return "Error: Falta la URL."
            # Foco en barra de direcciones
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.05)
            pyautogui.write(url, interval=0.005)
            pyautogui.press('enter')
            return f"Navegando a {url} en la ventana '{target_window.title}'."
            
        elif action == "search":
            query = parameters.get("query", "")
            if not query:
                return "Error: Falta la búsqueda (query)."
            # Foco en barra de direcciones
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.05)
            pyautogui.write(query, interval=0.005)
            pyautogui.press('enter')
            return f"Buscando '{query}' en la ventana '{target_window.title}'."
            
        elif action == "new_tab":
            url = parameters.get("url", "")
            pyautogui.hotkey('ctrl', 't')
            time.sleep(0.3)
            if url:
                pyautogui.write(url, interval=0.01)
                pyautogui.press('enter')
                return f"Nueva pestaña abierta y navegando a {url}."
            return "Nueva pestaña abierta."
            
        elif action == "close_tab":
            pyautogui.hotkey('ctrl', 'w')
            return "Pestaña actual cerrada."
            
        elif action == "scroll":
            direction = parameters.get("direction", "down")
            if direction == "down":
                pyautogui.press('pgdn')
            else:
                pyautogui.press('pgup')
            return f"Scroleo hacia {direction} completado."
            
        else:
            return f"Acción '{action}' no es compatible con el control de navegador activo. Usa atajos de teclado estándar."
            
    except Exception as e:
        return f"Error al intentar controlar el navegador: {str(e)}"
