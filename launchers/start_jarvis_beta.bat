@echo off
setlocal
set "ROOT=%~dp0.."
pushd "%ROOT%"

set "PYW=%ROOT%\.venv\Scripts\pythonw.exe"
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "MAIN=%ROOT%\main.py"
set "MAINC=%ROOT%\main.pyc"

if exist "%PYW%" (
    if exist "%MAIN%"  ( start "" "%PYW%" "%MAIN%"  & goto :done )
    if exist "%MAINC%" ( start "" "%PYW%" "%MAINC%" & goto :done )
)
if exist "%PY%" (
    if exist "%MAIN%"  ( start "" /B "%PY%" "%MAIN%"  & goto :done )
    if exist "%MAINC%" ( start "" /B "%PY%" "%MAINC%" & goto :done )
)

echo JARVIS Beta: no se encontro Python o main.py.
echo Ejecuta primero "Instalar_JARVIS.bat" para instalar el entorno.
pause
:done
popd
endlocal
