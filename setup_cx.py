import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": [
        "os", "sys", "json", "pathlib", "asyncio", "ctypes",
        "websockets", "numpy", "sounddevice", "vosk", "spotipy",
        "psutil", "pyautogui", "pygetwindow", "pyrect",
        "comtypes", "pycaw", "docx", "openpyxl", "qtawesome",
        "win10toast", "PyQt6", "actions", "agent", "memory",
        "core", "google",
        "_sounddevice_data",
    ],

    "include_files": [
        "assets/",
        "memory/",
        "config/",
        # 👇 CORREGIDO: site-packages con guion
        (
            r".venv\Lib\site-packages\_sounddevice_data",
            "lib/_sounddevice_data"
        ),
    ],

    "include_msvcr": True,
    "optimize": 2,

    "zip_exclude_packages": ["_sounddevice_data"],

    "excludes": [
        "tkinter",
        "unittest",
        "PySide6"
    ]
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="JARVIS AI",
    version="2.0",
    description="JARVIS AI Assistant",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "run.py",
            base=base,
            icon="assets/jarvis_icono.ico",
            target_name="JARVIS.exe"
        )
    ]
)