import json
import urllib.request
import urllib.error
import base64
import io
import re
from pathlib import Path

# Utilizamos el API key de OpenRouter como está centralizado
BASE_DIR = Path(__file__).resolve().parent.parent
API_FILE = BASE_DIR / "config" / "api_keys.json"

def _get_api_key() -> str:
    if not API_FILE.exists(): return ""
    try:
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        return data.get("openrouter_api_key", "")
    except: return ""

def visual_click(parameters: dict, player=None) -> str:
    """
    Toma una captura de pantalla, usa visión para encontrar las coordenadas del elemento descrito,
    y utiliza pyautogui para mover el mouse y hacer clic de forma nativa.
    """
    element_desc = parameters.get("element_description", "")
    if not element_desc:
        return "Error: No se especificó el elemento a cliquear."

    api_key = _get_api_key()
    if not api_key:
        return "Error: No se encontró openrouter_api_key en config/api_keys.json."

    try:
        import mss
        import pyautogui
        from PIL import Image
    except ImportError:
        return "Error: Faltan dependencias (mss, pyautogui, Pillow)."

    if player:
        player.write_log(f"👁 Buscando coordenadas para: '{element_desc}'...")

    try:
        with mss.mss() as sct:
            # Capturar el monitor principal
            mon = sct.monitors[1]
            sct_img = sct.grab(mon)
            
            # Tamaño original de la pantalla
            orig_w, orig_h = sct_img.size
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            # Redimensionar para API manteniendo proporción y ahorrando tokens
            max_size = (1280, 720)
            img.thumbnail(max_size, Image.Resampling.BILINEAR)
            new_w, new_h = img.size
            
            # Factores de escala para multiplicar la respuesta de la IA
            scale_x = orig_w / new_w
            scale_y = orig_h / new_h
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=75)
            img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        prompt = (
            f"Localiza exactamente el centro visual del elemento descrito como '{element_desc}'. "
            f"La imagen tiene un tamaño de {new_w}x{new_h} píxeles. "
            "DEBES devolver ÚNICA Y EXCLUSIVAMENTE un array JSON con las coordenadas [X, Y], sin texto adicional ni bloques markdown. "
            "Si el elemento no existe en la pantalla, devuelve un array vacío []. Ejemplo de salida: [450, 312]"
        )

        payload = {
            "model": "google/gemini-2.5-flash",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ]
        }

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/jarvis-beta",
            "X-Title": "JARVIS UI Automation",
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            if "choices" in response_data and len(response_data["choices"]) > 0:
                raw_text = response_data["choices"][0]["message"]["content"].strip()
                
                # Extraer JSON limpio ignorando bloques markdown si la IA no obedece
                match = re.search(r"\[\s*\d+\s*,\s*\d+\s*\]", raw_text)
                if not match:
                    if "[]" in raw_text:
                        return f"No se encontró el elemento '{element_desc}' en la pantalla."
                    return f"Error al parsear coordenadas de la IA. Respuesta cruda: {raw_text}"
                
                coords = json.loads(match.group(0))
                ai_x, ai_y = coords[0], coords[1]
                
                # Multiplicar por el factor de escala para llegar al pixel real
                real_x = int(ai_x * scale_x)
                real_y = int(ai_y * scale_y)
                
                # Mover el mouse suavemente y hacer clic
                pyautogui.moveTo(real_x, real_y, duration=0.4, tween=pyautogui.easeInOutQuad)
                pyautogui.click()
                
                return f"Clic visual ejecutado en '{element_desc}' (coordenadas reales: X={real_x}, Y={real_y})."
            else:
                return "Error: Respuesta inesperada de OpenRouter."

    except Exception as e:
        return f"Error en visual_click: {str(e)}"
