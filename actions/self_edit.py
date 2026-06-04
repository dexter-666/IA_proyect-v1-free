# -*- coding: utf-8 -*-
"""
self_edit.py — Permite a JARVIS editar sus propios archivos de código fuente.
Crea backups automáticos antes de cada modificación para seguridad.
"""
import os
import shutil
import difflib
from pathlib import Path
from datetime import datetime

# Raíz del proyecto JARVIS
JARVIS_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = JARVIS_ROOT / "backups"


def _ensure_backup_dir():
    BACKUP_DIR.mkdir(exist_ok=True)


def _make_backup(file_path: Path) -> str:
    """Crea una copia de seguridad del archivo antes de editarlo."""
    _ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relative = file_path.relative_to(JARVIS_ROOT)
    safe_name = str(relative).replace(os.sep, "__").replace("/", "__")
    backup_name = f"{safe_name}.{timestamp}.bak"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    return str(backup_path)


def _resolve_path(file_ref: str) -> Path:
    """
    Resuelve una referencia de archivo relativa al proyecto JARVIS.
    Acepta: 'main.py', 'actions/terminal_agent.py', 'core/prompt.txt', etc.
    También acepta rutas absolutas dentro del proyecto.
    """
    p = Path(file_ref)
    if p.is_absolute():
        # Verificar que esté dentro del proyecto
        try:
            p.relative_to(JARVIS_ROOT)
            return p
        except ValueError:
            raise ValueError(
                f"Ruta fuera del proyecto JARVIS. Solo se pueden editar archivos dentro de: {JARVIS_ROOT}"
            )
    # Relativa al root del proyecto
    resolved = (JARVIS_ROOT / p).resolve()
    try:
        resolved.relative_to(JARVIS_ROOT)
    except ValueError:
        raise ValueError(f"Ruta resuelta fuera del proyecto: {resolved}")
    return resolved


def self_edit(parameters: dict, player=None) -> str:
    """
    Auto-edición de código de JARVIS.
    Acciones: read_file, edit_file, append_file, create_file, list_backups, restore_backup
    """
    action = parameters.get("action", "").lower()
    file_ref = parameters.get("file", "")
    
    # ── READ ──────────────────────────────────────────────────────────────
    if action == "read_file":
        if not file_ref:
            return "Error: Se requiere 'file' para leer (ej: 'main.py', 'core/prompt.txt')."
        try:
            fp = _resolve_path(file_ref)
            if not fp.exists():
                return f"Error: El archivo '{file_ref}' no existe."
            content = fp.read_text(encoding="utf-8")
            # Numerar líneas para referencia
            lines = content.split("\n")
            if len(lines) > 200:
                # Mostrar solo las primeras 200 líneas con aviso
                numbered = "\n".join(f"{i+1}: {l}" for i, l in enumerate(lines[:200]))
                return (
                    f"Archivo '{file_ref}' ({len(lines)} líneas). Mostrando primeras 200:\n\n"
                    f"{numbered}\n\n... [{len(lines) - 200} líneas más]"
                )
            numbered = "\n".join(f"{i+1}: {l}" for i, l in enumerate(lines))
            return f"Archivo '{file_ref}' ({len(lines)} líneas):\n\n{numbered}"
        except Exception as e:
            return f"Error leyendo archivo: {e}"

    # ── EDIT (buscar y reemplazar) ────────────────────────────────────────
    elif action == "edit_file":
        if not file_ref:
            return "Error: Se requiere 'file'."
        target = parameters.get("target", "")
        replacement = parameters.get("replacement", "")
        if not target:
            return "Error: Se requiere 'target' (el texto exacto a buscar y reemplazar)."

        try:
            fp = _resolve_path(file_ref)
            if not fp.exists():
                return f"Error: El archivo '{file_ref}' no existe."

            content = fp.read_text(encoding="utf-8")
            
            if target not in content:
                return (
                    f"Error: No se encontró el texto 'target' en '{file_ref}'. "
                    f"Asegurate de que sea exacto (incluyendo espacios e indentación)."
                )

            count = content.count(target)
            
            # Crear backup antes de editar
            backup_path = _make_backup(fp)

            new_content = content.replace(target, replacement, 1)
            fp.write_text(new_content, encoding="utf-8")

            # Generar diff resumido
            old_lines = content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            diff = list(difflib.unified_diff(old_lines, new_lines, n=2))
            diff_str = "".join(diff[:30])  # Máximo 30 líneas de diff
            if len(diff) > 30:
                diff_str += "\n... [diff truncado]"

            result = (
                f"✅ Archivo '{file_ref}' editado exitosamente.\n"
                f"Backup guardado en: {backup_path}\n"
                f"Ocurrencias encontradas: {count} (se reemplazó la primera)\n"
            )
            if diff_str:
                result += f"\nDiff:\n{diff_str}"
            return result

        except Exception as e:
            return f"Error editando archivo: {e}"

    # ── APPEND ────────────────────────────────────────────────────────────
    elif action == "append_file":
        if not file_ref:
            return "Error: Se requiere 'file'."
        content_to_add = parameters.get("content", "")
        if not content_to_add:
            return "Error: Se requiere 'content' (el texto a agregar al final del archivo)."

        try:
            fp = _resolve_path(file_ref)
            if not fp.exists():
                return f"Error: El archivo '{file_ref}' no existe."

            backup_path = _make_backup(fp)

            with open(fp, "a", encoding="utf-8") as f:
                f.write(content_to_add)

            return (
                f"✅ Contenido agregado al final de '{file_ref}'.\n"
                f"Backup: {backup_path}"
            )
        except Exception as e:
            return f"Error agregando contenido: {e}"

    # ── CREATE ────────────────────────────────────────────────────────────
    elif action == "create_file":
        if not file_ref:
            return "Error: Se requiere 'file' (ruta relativa al proyecto)."
        content_new = parameters.get("content", "")

        try:
            fp = _resolve_path(file_ref)
            if fp.exists():
                backup_path = _make_backup(fp)
                fp.write_text(content_new, encoding="utf-8")
                return (
                    f"✅ Archivo '{file_ref}' sobrescrito (backup: {backup_path})."
                )
            else:
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(content_new, encoding="utf-8")
                return f"✅ Archivo '{file_ref}' creado exitosamente."
        except Exception as e:
            return f"Error creando archivo: {e}"

    # ── LIST BACKUPS ──────────────────────────────────────────────────────
    elif action == "list_backups":
        _ensure_backup_dir()
        backups = sorted(BACKUP_DIR.glob("*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            return "No hay backups guardados."
        lines = [f"Backups disponibles ({len(backups)}):"]
        for b in backups[:20]:  # Mostrar máximo 20
            size_kb = b.stat().st_size / 1024
            lines.append(f"  - {b.name} ({size_kb:.1f} KB)")
        if len(backups) > 20:
            lines.append(f"  ... y {len(backups) - 20} más")
        return "\n".join(lines)

    # ── RESTORE BACKUP ────────────────────────────────────────────────────
    elif action == "restore_backup":
        backup_name = parameters.get("backup_name", "")
        if not backup_name:
            return "Error: Se requiere 'backup_name' (nombre del archivo .bak a restaurar)."

        _ensure_backup_dir()
        backup_file = BACKUP_DIR / backup_name
        if not backup_file.exists():
            return f"Error: Backup '{backup_name}' no encontrado."

        # Deducir el archivo original del nombre del backup
        # Formato: ruta__al__archivo.py.20250521_123456.bak
        parts = backup_name.rsplit(".", 3)  # [name, timestamp, bak]
        if len(parts) < 3:
            return "Error: Formato de nombre de backup no reconocido."
        
        original_rel = parts[0].replace("__", os.sep)
        original_path = JARVIS_ROOT / original_rel

        try:
            # Backup del estado actual antes de restaurar
            if original_path.exists():
                _make_backup(original_path)
            shutil.copy2(backup_file, original_path)
            return f"✅ Backup '{backup_name}' restaurado exitosamente a '{original_rel}'."
        except Exception as e:
            return f"Error restaurando backup: {e}"

    # ── LIST FILES ────────────────────────────────────────────────────────
    elif action == "list_files":
        directory = parameters.get("directory", ".")
        try:
            dp = _resolve_path(directory)
            if not dp.is_dir():
                return f"Error: '{directory}' no es un directorio."
            
            items = sorted(dp.iterdir())
            lines = [f"Contenido de '{directory}/' ({len(items)} items):"]
            for item in items:
                if item.name.startswith(".") and item.name not in [".gitignore"]:
                    continue
                if item.is_dir():
                    lines.append(f"  📁 {item.name}/")
                else:
                    size_kb = item.stat().st_size / 1024
                    lines.append(f"  📄 {item.name} ({size_kb:.1f} KB)")
            return "\n".join(lines)
        except Exception as e:
            return f"Error listando archivos: {e}"

    else:
        return (
            f"Acción '{action}' no reconocida. Acciones disponibles:\n"
            "- read_file: Leer un archivo del proyecto\n"
            "- edit_file: Buscar y reemplazar texto en un archivo\n"
            "- append_file: Agregar contenido al final de un archivo\n"
            "- create_file: Crear o sobrescribir un archivo\n"
            "- list_files: Listar archivos de un directorio\n"
            "- list_backups: Ver backups disponibles\n"
            "- restore_backup: Restaurar un backup anterior"
        )
