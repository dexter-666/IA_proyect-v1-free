# -*- coding: utf-8 -*-
import subprocess
import pygetwindow as gw
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def set_master_volume(volume_percent: int) -> bool:
    """Ajusta el volumen maestro del sistema usando pycaw (0-100)."""
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMasterVolumeLevelScalar(volume_percent / 100.0, None)
        return True
    except Exception as e:
        print(f"[Contextual Control] Error setting volume: {e}")
        return False

def get_master_volume() -> int:
    """Obtiene el volumen maestro actual."""
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        return int(round(volume.GetMasterVolumeLevelScalar() * 100))
    except Exception:
        return 50

def set_brightness(percent: int) -> bool:
    """Ajusta el brillo de pantalla usando WMI via PowerShell (0-100)."""
    try:
        cmd = f"powershell -Command \"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{percent})\""
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        try:
            cmd2 = f"powershell -Command \"Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods | Invoke-CimMethod -MethodName WmiSetBrightness -Arguments @{{Timeout=0; Brightness={percent}}}\""
            subprocess.run(cmd2, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception:
            return False

def set_power_plan(plan_name: str) -> bool:
    """Cambia el plan de energía activo de Windows."""
    plans = {
        "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a"
    }
    guid = plans.get(plan_name.lower())
    if not guid:
        return False
    try:
        subprocess.run(f"powercfg /setactive {guid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"[Contextual Control] Error setting power plan: {e}")
        return False

def set_focus_assist(level: int) -> bool:
    """Ajusta el nivel de No Molestar (Focus Assist) en Windows usando el registro."""
    # 0 = Off, 1 = Priority Only, 2 = Alarms Only
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Noc", 0, winreg.REG_DWORD, level)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Contextual Control] Error setting Focus Assist: {e}")
        return False

def contextual_control(parameters: dict, player=None) -> str:
    """
    Control Contextual de Entorno. Ajusta dinámicamente volumen, brillo, energía y notificaciones
    según la ventana activa, hábitos de uso o comandos manuales.
    """
    action = parameters.get("action", "adjust_context").lower()
    
    if action == "set_volume":
        vol = parameters.get("volume")
        if vol is None:
            return "Error: Falta el parámetro 'volume' (0-100) para la acción 'set_volume'."
        vol = int(vol)
        if set_master_volume(vol):
            return f"Volumen maestro ajustado correctamente al {vol}%."
        return "No se pudo cambiar el volumen maestro."

    elif action == "set_brightness":
        bri = parameters.get("brightness")
        if bri is None:
            return "Error: Falta el parámetro 'brightness' (0-100) para la acción 'set_brightness'."
        bri = int(bri)
        if set_brightness(bri):
            return f"Brillo de pantalla ajustado correctamente al {bri}%."
        return "El ajuste de brillo de pantalla no está soportado en este hardware (común en PC de escritorio sin soporte WMI)."

    elif action == "set_power_plan":
        plan = parameters.get("power_plan")
        if not plan:
            return "Error: Falta el parámetro 'power_plan' (balanced, high_performance, power_saver) para la acción 'set_power_plan'."
        if set_power_plan(plan):
            return f"Plan de energía cambiado correctamente a '{plan}'."
        return f"No se pudo cambiar al plan de energía '{plan}'."

    elif action == "set_dnd":
        # Do Not Disturb / Focus Assist
        state = parameters.get("state", "off").lower()
        level = 0
        if state == "on" or state == "priority":
            level = 1
        elif state == "alarms":
            level = 2
            
        if set_focus_assist(level):
            return f"Focus Assist (No Molestar) configurado al nivel {level} ({state})."
        return "No se pudo ajustar el estado de Focus Assist."

    elif action == "adjust_context":
        # Detección inteligente por ventana en foco
        try:
            win = gw.getActiveWindow()
            title = win.title.lower() if win and win.title else ""
        except Exception:
            title = ""
            
        if not title:
            # Fallback a buscar procesos activos de interés
            active_procs = []
            for proc in psutil.process_iter(['name']):
                try:
                    active_procs.append(proc.info['name'].lower())
                except Exception:
                    pass
            title = " ".join(active_procs)

        result_msgs = []
        
        # Categorías contextuales
        # 1. Comunicación / Reunión
        if any(w in title for w in ["zoom", "teams", "meet", "discord", "skype", "whatsapp"]):
            set_master_volume(40)
            set_brightness(60)
            set_power_plan("balanced")
            set_focus_assist(1)  # Solo Prioridad
            result_msgs.append("Modo Reunión/Comunicación: Volumen 40%, Brillo 60%, Energía Equilibrado, No Molestar Activo.")
            
        # 2. Gaming / Alto Rendimiento
        elif any(w in title for w in ["steam", "epicgames", "cyberpunk", "csgo", "minecraft", "valorant", "gta"]):
            set_master_volume(75)
            set_brightness(90)
            set_power_plan("high_performance")
            set_focus_assist(2)  # Solo Alarmas
            result_msgs.append("Modo Gaming: Volumen 75%, Brillo 90%, Alto Rendimiento activado, No Molestar total.")

        # 3. Multimedia / Entretenimiento
        elif any(w in title for w in ["vlc", "netflix", "prime video", "youtube", "spotify"]):
            set_master_volume(80)
            set_brightness(80)
            set_power_plan("balanced")
            set_focus_assist(0)  # Apagado (para ver notificaciones o según preferencia)
            result_msgs.append("Modo Multimedia: Volumen 80%, Brillo 80%, Energía Equilibrado, No Molestar Desactivado.")

        # 4. Trabajo de Foco / Programación / Oficina
        elif any(w in title for w in ["word", "excel", "powerpoint", "vscode", "notepad", "sublime", "pdf", "python", "jarvis"]):
            set_master_volume(20)
            set_brightness(50)
            set_power_plan("power_saver")
            set_focus_assist(1)
            result_msgs.append("Modo Productividad/Foco: Volumen 20% (silencioso), Brillo 50% (cuidado de vista), Ahorro de Energía, No Molestar Activo.")
            
        else:
            # Valores por defecto para otros contextos
            set_master_volume(50)
            set_brightness(70)
            set_power_plan("balanced")
            set_focus_assist(0)
            result_msgs.append(f"Contexto general ('{title[:40]}...'): Ajustes estándar aplicados (Volumen 50%, Brillo 70%, Plan Equilibrado, Notificaciones activas).")
            
        return result_msgs[0]

    else:
        return f"Acción '{action}' no soportada por el módulo de Control Contextual."
