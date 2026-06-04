import os
import json
import traceback
from pathlib import Path

def document_manager(parameters: dict, player=None) -> str:
    """
    Manages documents (PDF, Word, Excel, Text).
    Supports opening them in their native apps, reading their text, or editing them.
    """
    action = parameters.get("action", "").lower()
    file_path_str = parameters.get("path", "")
    content = parameters.get("content", "")

    if not action or not file_path_str:
        return "Error: Faltan parámetros requeridos ('action' o 'path')."

    # Resolve paths (desktop, documents, downloads, etc)
    path_lower = file_path_str.lower()
    home_dir = Path.home()
    if path_lower.startswith("desktop"):
        file_path = home_dir / "Desktop" / file_path_str[len("desktop"):].lstrip("\\/")
    elif path_lower.startswith("documents"):
        file_path = home_dir / "Documents" / file_path_str[len("documents"):].lstrip("\\/")
    elif path_lower.startswith("downloads"):
        file_path = home_dir / "Downloads" / file_path_str[len("downloads"):].lstrip("\\/")
    else:
        file_path = Path(file_path_str)

    if not file_path.exists() and action not in ["edit"]:
        # Let's try searching on Desktop as fallback if not absolute
        if not file_path.is_absolute():
            file_path = home_dir / "Desktop" / file_path_str
            if not file_path.exists():
                return f"Error: No se encontró el archivo '{file_path_str}'."

    try:
        if action == "open":
            os.startfile(str(file_path))
            return f"He abierto el documento '{file_path.name}' en pantalla."

        elif action == "read" or action == "view":
            ext = file_path.suffix.lower()
            if ext in [".txt", ".md", ".json", ".csv", ".py", ".js", ".html", ".log"]:
                text = file_path.read_text(encoding="utf-8", errors="replace")
                # Return the first 2000 chars to avoid overflowing LLM context if too large
                return f"Contenido de '{file_path.name}':\n\n{text[:2000]}"
            else:
                return f"Error: No puedo leer directamente archivos de extensión '{ext}' en texto plano. Usa la acción 'open' para verlo."

        elif action == "edit":
            # Si se provee contenido, lo sobrescribe o añade (dependiendo de la orden)
            # Como edición simple para archivos de texto.
            if content:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
                return f"El archivo '{file_path.name}' ha sido modificado y guardado con éxito."
            else:
                # Si no envían texto, simplemente se abre en bloc de notas o default
                os.startfile(str(file_path))
                return f"He abierto el archivo '{file_path.name}' para que puedas editarlo."
                
        else:
            return f"Error: Acción '{action}' no reconocida en document_manager."

    except Exception as e:
        return f"Error en document_manager: {str(e)}\n{traceback.format_exc()}"
