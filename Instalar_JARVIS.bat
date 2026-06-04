@echo off
title Instalador de JARVIS AI

:: ── Solicitar permisos de Administrador ──────────────────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Solicitando permisos de administrador...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
    exit /b
)

:: Ya somos admin — establecer directorio de trabajo
cd /d "%~dp0"

:: 1. Comprobar si existe el Python del entorno virtual local primero
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" install.py
    exit
)

:: 2. Intentar buscar Python en la ruta estandar de instalacion del usuario (LocalAppData)
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    "%LocalAppData%\Programs\Python\Python312\python.exe" install.py
    exit
)
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" (
    "%LocalAppData%\Programs\Python\Python313\python.exe" install.py
    exit
)
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    "%LocalAppData%\Programs\Python\Python311\python.exe" install.py
    exit
)

:: 3. Intentar con el Python global del sistema (si esta en el PATH)
where python >nul 2>&1
if %errorlevel% equ 0 (
    python install.py
    exit
)

:: 4. Intentar en Program Files por si acaso
if exist "%ProgramFiles%\Python312\python.exe" (
    "%ProgramFiles%\Python312\python.exe" install.py
    exit
)
if exist "%ProgramFiles%\Python313\python.exe" (
    "%ProgramFiles%\Python313\python.exe" install.py
    exit
)

echo.
echo =======================================================================
echo [ERROR] No se pudo encontrar una instalacion de Python valida.
echo =======================================================================
echo.
echo Por favor, instala Python 3.12 o 3.13 y asegurate de marcar la opcion
echo "Add Python to PATH" durante la instalacion.
echo.
pause
exit
