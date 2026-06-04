import json
import base64
import urllib.request
import urllib.error
from pathlib import Path
from mss import mss
from PIL import Image
import io

API_FILE = Path("config/api_keys.json")

def _get_api_key() -> str:
    try:
        data = json.loads(API_FILE.read_text(encoding="utf-8"))
        return data.get("openrouter_api_key", "")
    except Exception:
        return ""

def _capture_screen_base64() -> str:
    """
    Captura la pantalla principal, la redimensiona/comprime y la devuelve en base64.
    """
    with mss() as sct:
        monitor = sct.monitors[1] # Monitor principal
        screenshot = sct.grab(monitor)
        
        # Convertir a imagen de Pillow
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Redimensionar si es muy grande para ahorrar tokens/ancho de banda
        max_size = (1280, 720)
        img.thumbnail(max_size, Image.Resampling.BILINEAR)
        
        # Guardar en buffer en memoria como JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=65)
        
        # Codificar a base64
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_b64

def screen_vision(parameters: dict, player=None) -> str:
    """
    Toma una captura de pantalla y la analiza usando OpenRouter (multimodal).
    """
    api_key = _get_api_key()
    if not api_key:
        return (
            "Error: No se encontró una clave de OpenRouter en config/api_keys.json. "
            "Asegúrate de haber configurado tu clave."
        )
        
    query = parameters.get("query") or parameters.get("text") or parameters.get("question") or "¿Qué ves en mi pantalla?"
    
    # Notificamos por voz (opcional) o log que estamos procesando
    if player:
        player.write_log("👁️ Capturando pantalla para OpenRouter...")
        
    try:
        b64_image = _capture_screen_base64()
    except Exception as e:
        return f"Error al capturar la pantalla: {e}"
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/jarvis-beta",
        "X-Title": "JARVIS AI Assistant",
        "Content-Type": "application/json"
    }
    
    # Payload multimodal de OpenRouter (estándar OpenAI)
    payload = {
        "model": "google/gemini-2.5-flash",
        "max_tokens": 1500,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Esta es una captura de mi pantalla. {query}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=40) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return "Error: Respuesta inesperada de OpenRouter."
    except urllib.error.HTTPError as e:
        error_info = e.read().decode("utf-8")
        return f"Error de OpenRouter al analizar imagen (HTTP {e.code}): {error_info}"
    except Exception as e:
        return f"Error al conectar con OpenRouter para la visión: {str(e)}"
