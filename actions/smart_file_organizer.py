# -*- coding: utf-8 -*-
import os
import hashlib
import shutil
from pathlib import Path

def get_file_md5(file_path: Path) -> str:
    """Calcula el hash MD5 de un archivo para detectar duplicados reales."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def smart_file_organizer(parameters: dict, player=None) -> str:
    """
    Automatiza la organización de carpetas, detecta archivos duplicados y analiza el espacio de disco.
    """
    action = parameters.get("action", "").lower()
    target_dir_str = parameters.get("directory", "")
    
    if not target_dir_str:
        # Por defecto, usar la carpeta de descargas del usuario en Windows o Escritorio
        target_dir_str = str(Path.home() / "Downloads")
        
    target_path = Path(target_dir_str).resolve()
    if not target_path.exists() or not target_path.is_dir():
        return f"Error: El directorio especificado '{target_dir_str}' no existe o no es válido."

    if action == "organize":
        # Organizar archivos por tipo en subcarpetas lógicas
        categories = {
            "Documentos": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".odt"],
            "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv"],
            "Musica": [".mp3", ".wav", ".flac", ".ogg"],
            "Instaladores": [".exe", ".msi"],
            "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz"]
        }
        
        moved_count = 0
        moved_details = []
        
        for file in target_path.iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                for cat, extensions in categories.items():
                    if ext in extensions:
                        cat_dir = target_path / cat
                        cat_dir.mkdir(exist_ok=True)
                        dest_file = cat_dir / file.name
                        
                        try:
                            shutil.move(str(file), str(dest_file))
                            moved_count += 1
                            moved_details.append(f"'{file.name}' -> '{cat}/'")
                            break
                        except Exception as e:
                            pass
                            
        if moved_count == 0:
            return f"No se encontraron archivos en '{target_path.name}' que necesitaran organización en categorías."
        return f"Organización completada en '{target_path.name}'. Se organizaron {moved_count} archivos:\n" + "\n".join(moved_details[:10]) + ("\n...[y más]" if len(moved_details) > 10 else "")

    elif action == "find_duplicates":
        # Buscar archivos duplicados reales usando MD5 hashes
        hashes = {}
        duplicates = []
        
        for root, dirs, files in os.walk(target_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    file_hash = get_file_md5(file_path)
                    if file_hash:
                        if file_hash in hashes:
                            duplicates.append((file_path, hashes[file_hash]))
                        else:
                            hashes[file_hash] = file_path
                            
        if not duplicates:
            return f"Análisis de duplicados completado en '{target_path.name}': No se encontraron archivos duplicados reales."
            
        res = f"Se detectaron {len(duplicates)} archivos duplicados reales en '{target_path.name}':\n"
        for dup, orig in duplicates[:10]:
            # Calcular tamaños
            size_mb = dup.stat().st_size / (1024 * 1024)
            res += f"- Duplicado: '{dup.name}' ({size_mb:.2f} MB) es idéntico a '{orig.name}'\n"
            
        if len(duplicates) > 10:
            res += "...[y más duplicados detectados]"
        return res

    elif action == "disk_space":
        # Analizar el uso y espacio libre del disco
        try:
            total, used, free = shutil.disk_usage(str(target_path))
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            percent_used = (used / total) * 100
            
            return (
                f"Análisis de espacio de disco para la unidad de '{target_path.name}':\n"
                f"- Espacio Total: {total_gb:.2f} GB\n"
                f"- Espacio Usado: {used_gb:.2f} GB ({percent_used:.1f}%)\n"
                f"- Espacio Disponible: {free_gb:.2f} GB"
            )
        except Exception as e:
            return f"Error leyendo espacio de disco: {e}"

    else:
        return f"Acción '{action}' no reconocida por el organizador inteligente de archivos."
