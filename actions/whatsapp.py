import time
import urllib.parse
import webbrowser
import json
from pathlib import Path

# Try to import pyautogui, if not available we will gracefully fail/log
try:
    import pyautogui
except ImportError:
    pyautogui = None

BASE_DIR = Path(__file__).resolve().parent.parent
CONTACTS_FILE = BASE_DIR / "config" / "whatsapp_contacts.json"

def load_contacts() -> dict:
    if CONTACTS_FILE.exists():
        try:
            return json.loads(CONTACTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_contacts(contacts: dict):
    try:
        CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONTACTS_FILE.write_text(json.dumps(contacts, indent=4, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[WhatsApp] Error saving contacts: {e}")

def whatsapp(parameters: dict, player=None) -> str:
    """
    Control avanzado de WhatsApp Web que gestiona contactos locales y
    automatiza el envío de mensajes de texto e imágenes de manera robusta.
    """
    action = parameters.get("action", "").lower()
    receiver = parameters.get("receiver", "")
    message = parameters.get("message", "")
    image_path = parameters.get("image_path", "")
    caption = parameters.get("caption", "")
    name = parameters.get("name", "")
    phone_param = parameters.get("phone", "")

    contacts = load_contacts()

    # Map actions from main.py's TOOL_DECLARATIONS
    if action == "send_text":
        action = "send"
    elif action in ["read_unread", "read_chat"]:
        action = "read"
    elif action == "unread":
        action = "read"

    # --- 1. CONTACT MANAGEMENT ---
    if action == "add_contact":
        contact_name = name or receiver
        contact_phone = phone_param
        if not contact_name or not contact_phone:
            return "Error: Para agregar un contacto se requiere el nombre ('name') y el teléfono ('phone')."
        # Clean phone
        contact_phone = "".join(filter(str.isdigit, contact_phone))
        contacts[contact_name.lower()] = {
            "name": contact_name,
            "phone": contact_phone
        }
        save_contacts(contacts)
        return f"Contacto '{contact_name}' guardado exitosamente con el teléfono: {contact_phone}."

    elif action == "delete_contact":
        contact_name = name or receiver
        if not contact_name:
            return "Error: Para eliminar un contacto se requiere especificar el nombre ('name')."
        if contact_name.lower() in contacts:
            del contacts[contact_name.lower()]
            save_contacts(contacts)
            return f"Contacto '{contact_name}' eliminado de la base de datos de JARVIS."
        return f"No se encontró ningún contacto con el nombre '{contact_name}'."

    elif action == "list_contacts":
        if not contacts:
            return "No tienes contactos guardados en la base de datos de JARVIS todavía."
        res = "Contactos guardados en JARVIS:\n"
        for k, v in contacts.items():
            res += f"• {v['name']}: {v['phone']}\n"
        return res

    # --- 2. SEND MESSAGE / IMAGE ACTIONS ---
    elif action in ["send", "send_image"]:
        if not receiver:
            return "Error: No se especificó el destinatario ('receiver')."
        
        # Determine phone number
        phone = ""
        contact_name = ""
        
        # Check if receiver itself is a phone number (e.g., contains mostly digits and len >= 8)
        cleaned_receiver = "".join(c for c in receiver if c.isdigit() or c == '+')
        digit_count = sum(c.isdigit() for c in cleaned_receiver)
        
        if digit_count >= 8:
            phone = cleaned_receiver.replace("+", "")
        else:
            # Look up in contact database
            match = contacts.get(receiver.lower())
            if match:
                phone = match["phone"]
                contact_name = match["name"]
            else:
                # Case-insensitive substring match
                for k, v in contacts.items():
                    if receiver.lower() in k or k in receiver.lower():
                        phone = v["phone"]
                        contact_name = v["name"]
                        break
        
        target_desc = contact_name if contact_name else receiver
        
        # Prepare URL
        encoded_msg = urllib.parse.quote(message)
        if phone:
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        else:
            # If no phone number is found, we search contact manually using search URL
            url = f"https://web.whatsapp.com/send?text={encoded_msg}"
            
        if player:
            player.write_log(f"💬 Abriendo WhatsApp Web para {target_desc}...")
            
        webbrowser.open(url)
        
        if not pyautogui:
            return f"Abriendo WhatsApp Web para '{target_desc}'. Para automatizar los clics se requiere instalar 'pyautogui'."

        # Wait for WhatsApp Web to load completely
        time.sleep(12)
        
        try:
            if not phone:
                # If no phone is found, search the contact name via search hotkey
                pyautogui.hotkey('ctrl', 'alt', '/')
                time.sleep(1.2)
                pyautogui.write(receiver, interval=0.01)
                time.sleep(2.5)
                pyautogui.press('enter')
                time.sleep(1.5)
                
            # Press enter to send text message
            pyautogui.press('enter')
            time.sleep(1)
            
            # --- Handle Image Sending ---
            if action == "send_image" and image_path:
                # Check if image file exists
                img_p = Path(image_path)
                if not img_p.exists():
                    return f"Mensaje de texto enviado, pero no se encontró la imagen en: {image_path}"
                
                # Copy image to clipboard depending on OS
                import ctypes
                from PIL import Image
                import io
                
                # Convert PIL image to clipboard format (DIB)
                image = Image.open(img_p)
                output = io.BytesIO()
                image.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:] # Offset 14 is the BMP file header
                output.close()
                
                # Windows clipboard API calls
                ctypes.windll.user32.OpenClipboard(None)
                ctypes.windll.user32.EmptyClipboard()
                # CF_DIB = 8
                ctypes.windll.user32.SetClipboardData(8, ctypes.windll.kernel32.GlobalAlloc(0x0002, len(data)))
                # Copy the BMP binary data to allocated memory
                h_clip_mem = ctypes.windll.user32.GetClipboardData(8)
                p_clip_mem = ctypes.windll.kernel32.GlobalLock(h_clip_mem)
                ctypes.cdll.msvcrt.memcpy(p_clip_mem, data, len(data))
                ctypes.windll.kernel32.GlobalUnlock(h_clip_mem)
                ctypes.windll.user32.CloseClipboard()
                
                time.sleep(1.0)
                # Paste the copied image
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(2.0)
                
                if caption:
                    pyautogui.write(caption, interval=0.01)
                    time.sleep(0.5)
                    
                pyautogui.press('enter')
                time.sleep(1)
                return f"Mensaje e imagen enviados exitosamente a '{target_desc}' vía WhatsApp Web."
                
            return f"Mensaje enviado exitosamente a '{target_desc}' vía WhatsApp Web."
        except Exception as e:
            return f"Mensaje abierto en WhatsApp Web para '{target_desc}'. Ocurrió una interrupción durante la simulación de teclas: {e}"

    # --- 3. READ CHAT / DEFAULT ACTION ---
    elif action == "read":
        webbrowser.open("https://web.whatsapp.com")
        return "Abriendo la bandeja de chats de WhatsApp Web para que puedas visualizarlos en pantalla."

    else:
        webbrowser.open("https://web.whatsapp.com")
        return f"Acción '{action}' ejecutada cargando WhatsApp Web en tu navegador por defecto."
