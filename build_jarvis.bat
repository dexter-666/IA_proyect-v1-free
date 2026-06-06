@echo off
title Compilador JARVIS AI

echo Limpiando build anterior...
if exist build rmdir /s /q build

echo Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo Iniciando compilacion con cx_Freeze...
python setup_cx.py build

if errorlevel 1 (
    echo.
    echo ERROR AL COMPILAR
    pause
    exit /b 1
)

echo.
echo ====================================
echo COMPILACION EXITOSA
echo ====================================
echo.

REM Opcional: probar si el ejecutable arranca sin errores de DLL
echo Probando el ejecutable (2 segundos)...
start /b build\exe.win-amd64-3.12\JARVIS.exe
timeout /t 2 /nobreak > nul
taskkill /f /im JARVIS.exe > nul 2>&1

echo Abriendo carpeta build...
explorer build

pause