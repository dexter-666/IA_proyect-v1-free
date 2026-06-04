@echo off
title Compilador de JARVIS AI (cx_Freeze)
echo.
echo ============================================================
echo   COMPILANDO JARVIS AI CON CX_FREEZE (MODO STANDALONE)
echo ============================================================
echo.

:: Ocultar/limpiar llaves privadas por seguridad
if exist "config\api_keys.json" rename "config\api_keys.json" "api_keys.json.bak"
copy "config\api_keys.example.json" "config\api_keys.json" > nul

echo [1/3] Ejecutando compilación cx_Freeze...
if exist build rmdir /s /q build
.venv\Scripts\python.exe setup_cx.py build

:: Restaurar llaves privadas
del "config\api_keys.json"
if exist "config\api_keys.json.bak" rename "config\api_keys.json.bak" "api_keys.json"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Falló la compilación con cx_Freeze.
    pause
    exit /b %errorlevel%
)

:: Buscar carpeta de compilación generada (ej: build\exe.win-amd64-3.12)
set "BUILD_DIR="
for /d %%i in (build\exe.*) do set "BUILD_DIR=%%i"

if "%BUILD_DIR%"=="" (
    echo [ERROR] No se pudo encontrar el directorio de salida de cx_Freeze.
    pause
    exit /b 1
)

echo.
echo [2/3] Preparando directorio en el escritorio...
if exist "C:\Users\Leguion T\Desktop\GitCodeJARVIS" (
    echo Limpiando archivos antiguos de compilaciones pasadas...
    rmdir /s /q "C:\Users\Leguion T\Desktop\GitCodeJARVIS"
)
mkdir "C:\Users\Leguion T\Desktop\GitCodeJARVIS"

echo.
echo [3/3] Copiando nuevos archivos compilados al escritorio...
xcopy "%BUILD_DIR%\*.*" "C:\Users\Leguion T\Desktop\GitCodeJARVIS\" /s /e /y > nul

echo.
echo ============================================================
echo   ¡PROCESO COMPLETADO CON ÉXITO!
echo   Ejecutable copiado a: Escritorio\GitCodeJARVIS\JARVIS.exe
echo ============================================================
echo.
pause
