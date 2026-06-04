@echo off
echo Ocultando llaves privadas por seguridad...
if exist "config\api_keys.json" rename "config\api_keys.json" "api_keys.json.bak"
copy "config\api_keys.example.json" "config\api_keys.json"

echo Iniciando compilacion de JARVIS con Nuitka (MODO ONEFILE)...
.venv\Scripts\python.exe -m nuitka --onefile --low-memory --jobs=2 --plugin-enable=pyqt6 --include-package=actions --include-package=agent --include-package=memory --include-package=core --nofollow-import-to=google.genai.types --no-deployment-flag=excluded-module-usage --include-data-files=.venv\Lib\site-packages\google\genai\types.py=google\genai\types.py --include-data-dir=assets=assets --include-data-dir=config=config --windows-icon-from-ico=assets\jarvis_icono.ico --output-dir=build_jarvis --output-filename=JARVIS.exe main.py

echo Restaurando llaves privadas...
del "config\api_keys.json"
if exist "config\api_keys.json.bak" rename "config\api_keys.json.bak" "api_keys.json"

if %errorlevel% neq 0 (
    echo Error compilando. Exit Code: %errorlevel%
    exit /b %errorlevel%
)

echo Moviendo al escritorio como GitCodeJARVIS...
if not exist "C:\Users\Leguion T\Desktop\GitCodeJARVIS" mkdir "C:\Users\Leguion T\Desktop\GitCodeJARVIS"
move build_jarvis\JARVIS.exe "C:\Users\Leguion T\Desktop\GitCodeJARVIS\JARVIS.exe"
echo Proceso Completado con Exito!
