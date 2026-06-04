import os
import sys
import time
import subprocess
import traceback

def get_watched_files():
    watched = {}
    exclude_dirs = {'.git', '.venv', '__pycache__', '.system_generated', 'logs', 'build', 'dist'}
    exclude_exts = {'.pyc', '.zip', '.log', '.ico', '.png', '.mp3'}
    
    for root, dirs, files in os.walk('.'):
        # Exclude directories in-place to prevent os.walk from entering them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_exts:
                continue
            path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(path)
                watched[path] = mtime
            except Exception:
                pass
    return watched

def main():
    print("============================================================")
    print("\033[1;32m   [RELOADER] Monitor de Cambios Activo (Hot Reload)   \033[0m")
    print("   Cualquier cambio en el código reiniciará JARVIS automáticamente.")
    print("============================================================")
    
    # We run main.py inside the virtual environment python interpreter
    venv_py = os.path.join(".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_py):
        venv_py = sys.executable  # fallback
        
    cmd = [venv_py, "main.py"]
    
    child = None
    last_watch = get_watched_files()
    
    try:
        # Initial launch
        print(f"\033[1;36m[RELOADER] Iniciando {cmd[1]}...\033[0m")
        child = subprocess.Popen(cmd)
        
        while True:
            time.sleep(1.0)
            
            # Check if child process has died on its own
            if child.poll() is not None:
                exit_code = child.returncode
                if exit_code == 0:
                    print("\033[1;33m[RELOADER] JARVIS cerró normalmente.\033[0m")
                else:
                    print(f"\033[1;31m[RELOADER] JARVIS finalizó con código de error {exit_code}. Esperando cambios para reiniciar...\033[0m")
                
                # Keep looping to watch for edits to restart it
                while child.poll() is not None:
                    time.sleep(1.0)
                    current_watch = get_watched_files()
                    changed = False
                    for path, mtime in current_watch.items():
                        if path not in last_watch or last_watch[path] != mtime:
                            print(f"\033[1;32m[RELOADER] Cambio detectado en: {path}. Reiniciando...\033[0m")
                            changed = True
                            break
                    if changed:
                        last_watch = current_watch
                        child = subprocess.Popen(cmd)
                        break
                    
                    # Also detect deleted files
                    for path in list(last_watch.keys()):
                        if path not in current_watch:
                            print(f"\033[1;32m[RELOADER] Archivo eliminado: {path}. Reiniciando...\033[0m")
                            last_watch = current_watch
                            child = subprocess.Popen(cmd)
                            break
                            
            # Check for modifications
            current_watch = get_watched_files()
            changed = False
            for path, mtime in current_watch.items():
                if path not in last_watch or last_watch[path] != mtime:
                    print(f"\033[1;32m[RELOADER] Cambio detectado en: {path}. Reiniciando...\033[0m")
                    changed = True
                    break
            
            # Check for deletions
            if not changed:
                for path in list(last_watch.keys()):
                    if path not in current_watch:
                        print(f"\033[1;32m[RELOADER] Archivo eliminado: {path}. Reiniciando...\033[0m")
                        changed = True
                        break
            
            if changed:
                # Terminate child
                if child and child.poll() is None:
                    print("\033[1;33m[RELOADER] Deteniendo instancia actual...\033[0m")
                    try:
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(child.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception:
                        child.terminate()
                        child.wait()
                
                last_watch = current_watch
                child = subprocess.Popen(cmd)
                
    except KeyboardInterrupt:
        print("\n\033[1;31m[RELOADER] Cerrando Monitor de Cambios...\033[0m")
        if child and child.poll() is None:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(child.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                child.terminate()
    except Exception as e:
        print(f"\033[1;31m[RELOADER] Error crítico: {e}\033[0m")
        traceback.print_exc()
        if child and child.poll() is None:
            child.terminate()
            
if __name__ == "__main__":
    # Activate ANSI color support in Windows console
    os.system("")
    main()
