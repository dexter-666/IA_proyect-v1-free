# -*- coding: utf-8 -*-
"""
open_app.py — Intelligent heuristic application finder and launcher for JARVIS.
"""
import os
import subprocess
import webbrowser
import traceback

def find_executable(app_name: str) -> str:
    """Scan standard system folders recursively to find executable or shortcut."""
    app_lower = app_name.lower().strip()
    
    start_menu_dirs = [
        os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.path.expanduser("~"), "Desktop")
    ]
    
    for base_dir in start_menu_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".lnk"):
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower == file_name_no_ext or app_lower in file_name_no_ext:
                        return os.path.join(root, file)
                        
    exe_search_dirs = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files")),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")),
        os.path.join(os.environ.get("LocalAppData", ""), "Programs")
    ]
    
    excluded_dirs = ["windowsapps", "redist", "uninst", "temp", "cache"]
    
    for base_dir in exe_search_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            depth = root.count(os.sep) - base_dir.count(os.sep)
            if depth > 3:
                dirs.clear()
                continue
            dirs[:] = [d for d in dirs if d.lower() not in excluded_dirs]
            for file in files:
                if file.lower().endswith(".exe"):
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower == file_name_no_ext or app_lower in file_name_no_ext:
                        return os.path.join(root, file)

    return None

def open_app(parameters: dict, response=None, player=None) -> str:
    """Launch local desktop applications based on user request."""
    app_name = parameters.get("app_name", "").strip()
    if not app_name:
        return "Error: Se requiere el parámetro 'app_name'."

    app_lower = app_name.lower().strip()

    try:
        # Check URLs
        if app_lower.startswith("http://") or app_lower.startswith("https://") or app_lower.endswith(".com"):
            url = app_name if app_lower.startswith("http") else f"https://{app_name}"
            webbrowser.open(url)
            if player: player.write_log(f"🌐 Abriendo web: '{url}'.")
            return f"Abriendo web: {url}"

        # Standard Mappings
        mappings = {
            "notepad": "notepad.exe",
            "bloc de notas": "notepad.exe",
            "calculator": "calc.exe",
            "calculadora": "calc.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "terminal": "powershell.exe",
            "paint": "mspaint.exe",
            "taskmgr": "taskmgr.exe"
        }

        executable = mappings.get(app_lower, None)
        
        if not executable:
            executable = find_executable(app_name)

        if not executable:
            executable = app_name

        try:
            os.startfile(executable)
        except Exception:
            cmd_exec = f'"{executable}"' if " " in executable and not executable.startswith('"') else executable
            subprocess.Popen(cmd_exec, shell=True)

        if player:
            player.write_log(f"🚀 Abriendo aplicación: '{app_name}'.")
        return f"Aplicación '{app_name}' iniciada correctamente."

    except Exception as e:
        traceback.print_exc()
        return f"Error intentando abrir '{app_name}': {str(e)}"
