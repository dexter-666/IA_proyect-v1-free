# -*- coding: utf-8 -*-
import os
from pathlib import Path
from datetime import datetime

def document_creator(parameters: dict, player=None) -> str:
    """
    Crea documentos de texto, Word o Excel locales.
    Soporta rutas personalizadas en toda la PC usando el parámetro 'save_path'.
    """
    action = parameters.get("action", "").lower()
    title = parameters.get("title", "Documento_Sin_Titulo")
    content = parameters.get("content", "")
    sheets = parameters.get("sheets", [])
    save_path_str = parameters.get("save_path", "")
    
    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
    if not safe_title:
        safe_title = "Documento"

    # Determinar la ruta de guardado final en la PC
    if save_path_str:
        file_path = Path(save_path_str)
        # Si la ruta dada es un directorio, le añadimos el nombre de archivo correspondiente
        if file_path.is_dir() or save_path_str.endswith("\\") or save_path_str.endswith("/"):
            if action in ["word", "google_doc"]:
                ext = ".docx"
            elif action in ["excel", "google_sheet"]:
                ext = ".xlsx"
            else:
                ext = ".txt"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{safe_title}_{timestamp}{ext}"
            file_path = file_path / file_name
        else:
            # Asegurar que el directorio padre existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Por defecto, se escribe en el Escritorio del usuario (OneDrive/Español compatible)
        try:
            from actions.path_helper import get_desktop_path
            desktop_path = get_desktop_path()
        except Exception:
            desktop_path = Path(os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop"))
            
        if action in ["word", "google_doc"]:
            ext = ".docx"
        elif action in ["excel", "google_sheet"]:
            ext = ".xlsx"
        else:
            ext = ".txt"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{safe_title}_{timestamp}{ext}"
        file_path = desktop_path / file_name

    try:
        if action == "word" or action == "google_doc":
            try:
                from docx import Document
                doc = Document()
                doc.add_heading(title, 0)
                
                # Procesamiento simple de markdown a Word
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('## '):
                        doc.add_heading(line[3:], level=2)
                    elif line.startswith('# '):
                        doc.add_heading(line[2:], level=1)
                    elif line.startswith('- '):
                        doc.add_paragraph(line[2:], style='List Bullet')
                    else:
                        doc.add_paragraph(line)
                        
                doc.save(file_path)
                return f"Documento Word creado exitosamente en: '{file_path}'."
            except ImportError:
                return "Error: Faltan librerías para crear Word. (python-docx)"
                
        elif action == "excel" or action == "google_sheet":
            try:
                from openpyxl import Workbook
                wb = Workbook()
                wb.remove(wb.active) # Remove default sheet
                
                if not sheets:
                    return "Error: No se proporcionaron datos (sheets) para crear el Excel."
                    
                for sheet_data in sheets:
                    sheet_name = sheet_data.get("name", "Hoja")
                    headers = sheet_data.get("headers", [])
                    rows = sheet_data.get("rows", [])
                    
                    ws = wb.create_sheet(title=sheet_name[:31])
                    if headers:
                        ws.append(headers)
                    for row in rows:
                        ws.append(row)
                        
                wb.save(file_path)
                return f"Planilla Excel creada exitosamente en: '{file_path}'."
            except ImportError:
                return "Error: Faltan librerías para crear Excel. (openpyxl)"
                
        elif action == "text":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"{title}\n\n{content}")
            return f"Archivo de texto creado exitosamente en: '{file_path}'."
            
        else:
            return f"Acción '{action}' no soportada o desconocida. Usá 'word', 'excel' o 'text'."
            
    except Exception as e:
        return f"Error al crear el documento: {str(e)}"
