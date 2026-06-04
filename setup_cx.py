import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sys", "json", "pathlib", "PyQt6", "actions", "agent", "memory", "core", "google"],
    "include_files": ["assets/", ("config/api_keys.example.json", "config/api_keys.json"), "config/accessibility_config.json", "config/rules.json", "config/user_profile.json"],
    "excludes": ["tkinter", "unittest"],
    "optimize": 2,
    "include_msvcr": True
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="JARVIS AI",
    version="2.0",
    description="JARVIS AI Assistant",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "run.py", base=base, icon="assets/jarvis_icono.ico", target_name="JARVIS.exe")]
)
