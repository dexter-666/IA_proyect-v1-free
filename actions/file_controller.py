# -*- coding: utf-8 -*-
"""
file_controller.py — Basic file and directory operations manager for JARVIS.
"""
import os
import shutil
import traceback
from pathlib import Path

def resolve_path(p: str) -> str:
    try:
        from actions.path_helper import get_desktop_path, get_documents_path, get_downloads_path
        desktop_dir = str(get_desktop_path())
        documents_dir = str(get_documents_path())
        downloads_dir = str(get_downloads_path())
    except Exception:
        home = os.path.expanduser("~")
        desktop_dir = os.path.join(home, "Desktop")
        documents_dir = os.path.join(home, "Documents")
        downloads_dir = os.path.join(home, "Downloads")

    if not p:
        return desktop_dir
    
    p_lower = p.lower().strip()
    
    if p_lower == "desktop" or p_lower.startswith("desktop\\") or p_lower.startswith("desktop/"):
        rel = p[7:].lstrip("\\/")
        return os.path.join(desktop_dir, rel)
    elif p_lower == "downloads" or p_lower.startswith("downloads\\") or p_lower.startswith("downloads/"):
        rel = p[9:].lstrip("\\/")
        return os.path.join(downloads_dir, rel)
    elif p_lower == "documents" or p_lower.startswith("documents\\") or p_lower.startswith("documents/"):
        rel = p[9:].lstrip("\\/")
        return os.path.join(documents_dir, rel)
    
    return os.path.abspath(p)

def file_controller(parameters: dict, player=None) -> str:
    action = parameters.get("action", "").lower().strip()
    path_raw = parameters.get("path", "")
    destination_raw = parameters.get("destination", "")
    new_name = parameters.get("new_name", "")
    content = parameters.get("content", "")

    if not action:
        return "Error: Se requiere el parámetro 'action'."

    try:
        resolved_path = resolve_path(path_raw)

        if action == "list":
            if not os.path.exists(resolved_path):
                return f"Error: La ruta '{path_raw}' no existe."
            if not os.path.isdir(resolved_path):
                return f"Error: '{path_raw}' no es una carpeta."
            
            items = sorted(os.listdir(resolved_path))
            lines = [f"Contenido de '{os.path.basename(resolved_path)}':"]
            for item in items[:30]: # Limit output
                lines.append(f" - {item}")
            return "\n".join(lines)

        elif action == "create_folder":
            os.makedirs(resolved_path, exist_ok=True)
            if player: player.write_log(f"📁 Carpeta creada: '{resolved_path}'.")
            return f"Carpeta creada exitosamente."

        elif action == "delete":
            if not os.path.exists(resolved_path):
                return f"Error: La ruta '{path_raw}' no existe."
            try:
                import send2trash
                send2trash.send2trash(resolved_path)
            except ImportError:
                if os.path.isdir(resolved_path): shutil.rmtree(resolved_path)
                else: os.remove(resolved_path)
            if player: player.write_log(f"🗑️ Eliminado: '{path_raw}'.")
            return "Eliminado con éxito."

        elif action == "move":
            resolved_dest = resolve_path(destination_raw)
            os.makedirs(os.path.dirname(resolved_dest), exist_ok=True)
            shutil.move(resolved_path, resolved_dest)
            if player: player.write_log(f"🚚 Movido: '{path_raw}'.")
            return "Movido correctamente."

        elif action == "copy":
            resolved_dest = resolve_path(destination_raw)
            if os.path.isdir(resolved_path):
                shutil.copytree(resolved_path, resolved_dest)
            else:
                os.makedirs(os.path.dirname(resolved_dest), exist_ok=True)
                shutil.copy2(resolved_path, resolved_dest)
            if player: player.write_log(f"👥 Copiado: '{path_raw}'.")
            return "Copiado correctamente."

        elif action == "read":
            with open(resolved_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            return text[:2000]

        elif action == "write":
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            with open(resolved_path, "w", encoding="utf-8") as f:
                f.write(content or "")
            if player: player.write_log(f"📄 Archivo escrito: '{path_raw}'.")
            return "Archivo guardado."

        else:
            return f"Acción '{action}' limitada o no soportada en esta versión de JARVIS."

    except Exception as e:
        traceback.print_exc()
        return f"Error ejecutando la operación de archivo: {str(e)}"
