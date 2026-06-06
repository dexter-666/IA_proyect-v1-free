# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import time

def print_banner():
    cyan = "\033[36m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"
    reset = "\033[0m"
    
    # Activar colores ANSI en Windows
    os.system("") 
    
    print(f"{cyan}======================================================================={reset}")
    print(f"{cyan}      __  ___   ____   _    __  ____   _____                           {reset}")
    print(f"{cyan}     / / /   | / __ \ / /  / / / __ \ / ___/                           {reset}")
    print(f"{cyan} __  / / / /| |/ /_/ // /  / / / /_/ / \\__ \\                            {reset}")
    print(f"{cyan}/ /_/ / / ___ // _, _// /__/ /  / _, _/ ___/ /                            {reset}")
    print(f"{cyan}\\____/ /_/  |_|/_/ |_|/____/_/  /_/ |_|/____/                             {reset}")
    print("                                                                       ")
    print(f"{green}                  SISTEMA DE INSTALACIÓN INTELIGENTE                   {reset}")
    print(f"{cyan}======================================================================={reset}")
    print()

def main():
    print_banner()
    print("Este asistente preparará a JARVIS para funcionar de forma óptima.")
    print()
    print(" [1] Comenzar instalación limpia (Recomendado)")
    print(" [2] Salir")
    print()
    
    try:
        opt = input("Selecciona una opción (1-2): ").strip()
    except (KeyboardInterrupt, EOFError):
        opt = "2"
        
    if opt != "1":
        print("\nSaliendo del instalador...")
        time.sleep(1.5)
        sys.exit(0)
        
    # FASE 1: Verificación de requisitos
    os.system("cls")
    print_banner()
    print("\033[36m [FASE 1/5] - Verificando requisitos del sistema...\033[0m")
    print()
    
    print(f"[OK] Python detectado: {sys.version.split()[0]}")
    
    # Limpieza de residuos antiguos
    print("\033[33m[INFO] Limpiando archivos temporales viejos y cachés...\033[0m")
    
    basura = ["build", "dist"]
    for folder in basura:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except Exception:
                pass
                
    archivos_basura = ["jarvis.log", "JARVIS_Beta_Installer.exe"]
    for f in os.listdir("."):
        if f.endswith(".spec") or f in archivos_basura:
            try:
                os.remove(f)
            except Exception:
                pass
                
    print("\033[32m[OK] Limpieza de residuos completada.\033[0m")
    time.sleep(1)
    
    # FASE 2: Entorno Virtual
    os.system("cls")
    print_banner()
    print("\033[36m [FASE 2/5] - Configurando Entorno Virtual (.venv)...\033[0m")
    print()
    
    if not os.path.exists(".venv"):
        print("\033[33m[INFO] Creando un entorno virtual de Python limpio...\033[0m")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print("\033[32m[OK] Entorno virtual creado exitosamente.\033[0m")
        except Exception as e:
            print(f"\033[31m[ERROR] No se pudo crear el entorno virtual: {e}\033[0m")
            input("Presiona Enter para salir...")
            sys.exit(1)
    else:
        print("\033[32m[OK] Entorno virtual existente detectado.\033[0m")
        
    time.sleep(1)
    
    # FASE 3: Instalación de dependencias
    os.system("cls")
    print_banner()
    print("\033[36m [FASE 3/5] - Instalando dependencias de JARVIS...\033[0m")
    print()
    print("Esto puede tomar unos minutos dependiendo de tu conexión a Internet.")
    print("Instalando requerimientos de forma segura...")
    print()
    
    venv_python = os.path.join(".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = "python" # Fallback
        
    try:
        # Upgrade pip
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        # Install requirements
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("\033[32m\n[OK] Todas las dependencias se instalaron correctamente.\033[0m")
    except Exception as e:
        print(f"\033[31m\n[ERROR] Ocurrió un error al instalar dependencias: {e}\033[0m")
        input("Presiona Enter para salir...")
        sys.exit(1)
        
    time.sleep(1)
    
    # FASE 4: Configuración inicial
    os.system("cls")
    print_banner()
    print("\033[36m [FASE 4/5] - Configuración Inicial...\033[0m")
    print()
    
    config_dir = os.path.join(".", "config")
    api_keys_path = os.path.join(config_dir, "api_keys.json")
    api_keys_template = os.path.join(config_dir, "api_keys.example.json")
    rules_path = os.path.join(config_dir, "rules.json")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        print("\033[32m[OK] Directorio config/ creado.\033[0m")
    
    import json
    
    # Load existing config or default
    current_config = {}
    if os.path.exists(api_keys_path):
        try:
            with open(api_keys_path, "r", encoding="utf-8") as f:
                current_config = json.load(f)
        except Exception:
            pass

    if not current_config:
        current_config = {
            "gemini_api_key": "",
            "os_system": "windows",
            "camera_index": 0,
            "mic_device": "",
            "speaker_device": "",
            "chrome_google_profile": "Default",
            "chrome_exe_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "timezone": "America/Bogota",
            "language": "es-ES",
            "thinking_sound": True,
            "jarvis_voice": "Charon",
            "spotify_client_id": "",
            "spotify_client_secret": "",
            "spotify_redirect_uri": "http://127.0.0.1:8888/callback",
            "tmdb_api_key": "",
            "openrouter_api_key": "",
            "jarvis_theme": "gold",
            "gpu_acceleration": False
        }

    # Load existing name from memory if exists
    memory_dir = os.path.join(".", "memory")
    memory_path = os.path.join(memory_dir, "long_term.json")
    current_memory = {}
    existing_name = ""
    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r", encoding="utf-8") as f:
                current_memory = json.load(f)
                existing_name = current_memory.get("identity", {}).get("name", {}).get("value", "")
        except Exception:
            pass

    # Request credentials from user
    print("\033[33m[REQUERIDO] Por favor ingresa los datos fundamentales de JARVIS:\033[0m")
    print()
    
    # 1. Name
    name_prompt = f" ¿Cómo quieres que te llame JARVIS? [{existing_name}]: " if existing_name else " ¿Cómo quieres que te llame JARVIS?: "
    user_name = input(name_prompt).strip()
    if not user_name and existing_name:
        user_name = existing_name
    while not user_name:
        print("\033[31m[ERROR] El nombre es obligatorio.\033[0m")
        user_name = input(" ¿Cómo quieres que te llame JARVIS?: ").strip()

    # 2. Gemini API Key
    existing_gemini = current_config.get("gemini_api_key", "")
    gemini_prompt = f" Gemini API Key [{existing_gemini[:6]}...{existing_gemini[-6:] if len(existing_gemini) > 12 else ''}]: " if existing_gemini else " Gemini API Key: "
    user_gemini = input(gemini_prompt).strip()
    if not user_gemini and existing_gemini:
        user_gemini = existing_gemini
    while not user_gemini:
        print("\033[31m[ERROR] La Gemini API Key es obligatoria para el funcionamiento base.\033[0m")
        user_gemini = input(" Gemini API Key: ").strip()

    # 3. OpenRouter API Key
    existing_openrouter = current_config.get("openrouter_api_key", "")
    openrouter_prompt = f" OpenRouter API Key [{existing_openrouter[:6]}...{existing_openrouter[-6:] if len(existing_openrouter) > 12 else ''}]: " if existing_openrouter else " OpenRouter API Key: "
    user_openrouter = input(openrouter_prompt).strip()
    if not user_openrouter and existing_openrouter:
        user_openrouter = existing_openrouter
    while not user_openrouter:
        print("\033[31m[ERROR] La OpenRouter API Key es obligatoria para razonamiento complejo.\033[0m")
        user_openrouter = input(" OpenRouter API Key: ").strip()

    # Save to config/api_keys.json
    current_config["gemini_api_key"] = user_gemini
    current_config["openrouter_api_key"] = user_openrouter
    with open(api_keys_path, "w", encoding="utf-8") as f:
        json.dump(current_config, f, indent=4)
    print("\033[32m[OK] Archivo config/api_keys.json configurado correctamente.\033[0m")

    # Save name to memory/long_term.json
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir, exist_ok=True)
    if "identity" not in current_memory:
        current_memory["identity"] = {}
    if "name" not in current_memory["identity"]:
        current_memory["identity"]["name"] = {}
    current_memory["identity"]["name"]["value"] = user_name
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(current_memory, f, indent=4)
    print("\033[32m[OK] Memoria de usuario guardada correctamente.\033[0m")

    if not os.path.exists(rules_path):
        with open(rules_path, "w", encoding="utf-8") as f:
            json.dump({"rules": []}, f, indent=4)
        print("\033[32m[OK] Archivo rules.json creado.\033[0m")
    else:
        print("\033[32m[OK] Archivo rules.json existente detectado.\033[0m")
    
    time.sleep(1)
    
    # FASE 5: Acceso directo
    os.system("cls")
    print_banner()
    print("\033[36m [FASE 5/5] - Creación de Accesos Directos...\033[0m")
    print()
    print("Creando acceso directo en tu Escritorio para un inicio rápido...")
    print()
    
    try:
        current_dir = os.getcwd()
        icon_path = os.path.join(current_dir, "assets", "jarvis_icono.ico")
        target_vbs = os.path.join(current_dir, "Iniciar JARVIS Beta.vbs")
        
        # Crear acceso directo con PowerShell
        ps_cmd = (
            f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut(([System.Environment]::GetFolderPath('Desktop')+'\\JARVIS AI.lnk'));"
            f"$s.TargetPath='{target_vbs}';"
            f"$s.WorkingDirectory='{current_dir}';"
            f"$s.IconLocation='{icon_path}';"
            f"$s.Description='Lanzador de JARVIS AI (Admin)';"
            f"$s.Save()"
        )
        
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
        
        # Marcar el .lnk como "Ejecutar como Administrador"
        # El flag está en el byte 21 del archivo .lnk (bit 0x20)
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            lnk_path = os.path.join(desktop, "JARVIS AI.lnk")
            if os.path.exists(lnk_path):
                with open(lnk_path, "rb") as f:
                    data = bytearray(f.read())
                data[21] = data[21] | 0x20  # Set RunAsAdmin flag
                with open(lnk_path, "wb") as f:
                    f.write(data)
        except Exception:
            pass  # El VBS ya tiene auto-elevación, esto es redundante
        
        print("\033[32m[OK] Acceso directo 'JARVIS AI' creado en el Escritorio (con permisos de Admin).\033[0m")
    except Exception as e:
        print(f"\033[33m[ADVERTENCIA] No se pudo crear el acceso directo de forma automática: {e}\033[0m")
        
    time.sleep(1)
    
    # Pantalla Final
    os.system("cls")
    print_banner()
    print("\033[32m=======================================================================")
    print("     ¡INSTALACIÓN Y CONFIGURACIÓN COMPLETADA CON ÉXITO!")
    print("=======================================================================\033[0m")
    print()
    print("JARVIS está listo para servirte.")
    print("Al iniciar el sistema por primera vez se te solicitarán tus API Keys")
    print("para Gemini y OpenRouter automáticamente de forma visual.")
    print()
    print(" [1] Iniciar JARVIS ahora mismo")
    print(" [2] Salir")
    print()
    
    try:
        launch_opt = input("Selecciona una opción (1-2): ").strip()
    except (KeyboardInterrupt, EOFError):
        launch_opt = "2"
        
    if launch_opt == "1":
        print("Iniciando JARVIS...")
        try:
            # Ejecutar el VBS silencioso
            os.startfile("Iniciar JARVIS Beta.vbs")
        except Exception:
            # Fallback si no está asociado
            subprocess.Popen(["wscript.exe", "Iniciar JARVIS Beta.vbs"])
            
    print("\nGracias por usar el instalador de JARVIS AI.")
    time.sleep(2)

if __name__ == "__main__":
    main()
