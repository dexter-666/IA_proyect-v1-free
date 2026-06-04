import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "json", "sys", "asyncio", "PyQt6", "numpy", "sounddevice", "google.genai", "actions", "agent", "core", "memory"],
    "include_files": ["assets/", ("config/api_keys.example.json", "config/api_keys.json"), "config/accessibility_config.json", "config/rules.json", "config/user_profile.json"],
    "excludes": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="JARVIS",
    version="1.0",
    description="JARVIS AI Assistant",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="assets/jarvis_icono.ico", target_name="JARVIS.exe")]
)
