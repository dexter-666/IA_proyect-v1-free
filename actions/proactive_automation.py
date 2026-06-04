# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "rules.json"

def proactive_automation(parameters: dict, player=None) -> str:
    """
    Gestiona reglas de automatización basadas en hábitos y comportamientos del sistema.
    """
    action = parameters.get("action", "").lower()
    
    # Asegurar que el archivo de reglas existe
    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not RULES_PATH.exists():
        RULES_PATH.write_text("[]", encoding="utf-8")
        
    try:
        rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except Exception:
        rules = []

    if action == "add_rule":
        rule_name = parameters.get("rule_name", "")
        trigger = parameters.get("trigger", "")  # Ej. "cpu_high", "time_of_day", "app_open"
        trigger_value = parameters.get("trigger_value", "")  # Ej. "85", "22:00", "chrome.exe"
        action_to_take = parameters.get("action_to_take", "")  # Ej. "optimize_ram", "mute_system", "run_script"
        
        if not all([rule_name, trigger, action_to_take]):
            return "Error: Faltan campos obligatorios para añadir la regla (rule_name, trigger, action_to_take)."
            
        new_rule = {
            "name": rule_name,
            "trigger": trigger,
            "trigger_value": trigger_value,
            "action": action_to_take,
            "active": True
        }
        
        # Eliminar regla anterior si tiene el mismo nombre
        rules = [r for r in rules if r.get("name") != rule_name]
        rules.append(new_rule)
        
        RULES_PATH.write_text(json.dumps(rules, indent=4, ensure_ascii=False), encoding="utf-8")
        return f"Regla proactiva '{rule_name}' agregada con éxito para ejecutarse al detectar '{trigger}': '{trigger_value}'."
        
    elif action == "list_rules":
        if not rules:
            return "No hay ninguna regla de automatización proactiva configurada."
            
        res = "Reglas de Automatización Proactivas:\n"
        for idx, r in enumerate(rules, 1):
            status = "Activa" if r.get("active", True) else "Inactiva"
            res += f"{idx}. [{status}] {r.get('name')} - Disparador: {r.get('trigger')} ({r.get('trigger_value')}) -> Acción: {r.get('action')}\n"
        return res
        
    elif action == "delete_rule":
        rule_name = parameters.get("rule_name", "")
        if not rule_name:
            return "Error: Debes proporcionar el nombre de la regla a eliminar."
            
        new_rules = [r for r in rules if r.get("name") != rule_name]
        if len(new_rules) == len(rules):
            return f"No se encontró la regla '{rule_name}'."
            
        RULES_PATH.write_text(json.dumps(new_rules, indent=4, ensure_ascii=False), encoding="utf-8")
        return f"Regla '{rule_name}' eliminada correctamente."
        
    elif action == "trigger_check":
        # Disparar chequeo manual de reglas proactivas
        triggered = []
        for r in rules:
            if not r.get("active", True):
                continue
                
            trigger_type = r.get("trigger", "")
            if trigger_type == "cpu_high":
                # Simular chequeo de recursos
                import psutil
                cpu = psutil.cpu_percent()
                limit = float(r.get("trigger_value", "90"))
                if cpu > limit:
                    triggered.append(f"Regla '{r.get('name')}' disparada por CPU alta ({cpu}% > {limit}%). Acción: {r.get('action')}")
            
            elif trigger_type == "ram_high":
                import psutil
                ram = psutil.virtual_memory().percent
                limit = float(r.get("trigger_value", "90"))
                if ram > limit:
                    triggered.append(f"Regla '{r.get('name')}' disparada por RAM alta ({ram}% > {limit}%). Acción: {r.get('action')}")
                    
        if not triggered:
            return "Chequeo proactivo completado: Ningún disparador activo de reglas de sistema en este instante."
        return "Disparadores de automatización ejecutados:\n" + "\n".join(triggered)
        
    else:
        return f"Acción '{action}' no soportada por el sistema de automatización proactiva."
