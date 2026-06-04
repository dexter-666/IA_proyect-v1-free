import json
import os
import sys
from pathlib import Path

def tool_creator(parameters: dict, player=None, speak=None) -> str:
    """
    Creates and registers a new tool dynamically.
    """
    tool_name = parameters.get("tool_name", "")
    description = parameters.get("description", "")
    parameters_schema_str = parameters.get("parameters_schema", "{}")
    python_code = parameters.get("python_code", "")
    
    if not all([tool_name, description, python_code]):
        return "Error: Faltan parámetros obligatorios (tool_name, description, python_code)."
        
    try:
        # 1. Guardar el código Python de la herramienta
        actions_dir = Path(__file__).parent
        tool_file = actions_dir / f"{tool_name}.py"
        tool_file.write_text(python_code, encoding="utf-8")
        
        # 2. Parsear las propiedades del schema
        try:
            import ast
            properties = ast.literal_eval(parameters_schema_str)
            if not isinstance(properties, dict):
                properties = {}
        except Exception:
            try:
                properties = json.loads(parameters_schema_str)
            except Exception:
                properties = {}
            
        new_tool_def = {
            "name": tool_name,
            "description": description,
            "parameters": {
                "type": "OBJECT",
                "properties": properties,
                "required": list(properties.keys())
            }
        }
        
        # 3. Guardar la definición en custom_tools.json para persistencia entre reinicios
        custom_tools_path = actions_dir / "custom_tools.json"
        custom_tools = []
        if custom_tools_path.exists():
            try:
                custom_tools = json.loads(custom_tools_path.read_text(encoding="utf-8"))
            except Exception:
                pass
                
        # Remover si ya existía una herramienta con el mismo nombre y reemplazarla
        custom_tools = [t for t in custom_tools if t["name"] != tool_name]
        custom_tools.append(new_tool_def)
        custom_tools_path.write_text(json.dumps(custom_tools, indent=4, ensure_ascii=False), encoding="utf-8")
        
        # 4. Inyectar dinámicamente en el array TOOL_DECLARATIONS en memoria (main.py)
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'TOOL_DECLARATIONS'):
            # Remover si ya estaba en memoria
            main_module.TOOL_DECLARATIONS = [t for t in main_module.TOOL_DECLARATIONS if t.get("name") != tool_name]
            # Agregar la nueva herramienta
            main_module.TOOL_DECLARATIONS.append(new_tool_def)
        
        # 5. Forzar la reconexión de JARVIS para que cargue la nueva herramienta
        if player and hasattr(player, "on_config_saved"):
            from threading import Timer
            def delayed_reload():
                try:
                    # Esto forzará que JarvisLive corte la sesión, reconstruya _build_config (con la nueva herramienta) y reconecte.
                    player.on_config_saved({}) 
                except:
                    pass
            Timer(1.5, delayed_reload).start()
            return f"Herramienta '{tool_name}' programada e instalada con éxito. Reiniciando mis módulos cognitivos para integrarla..."
        
        return f"Herramienta '{tool_name}' creada exitosamente, pero no pude reiniciar el sistema automáticamente. Requiere reinicio manual."
        
    except Exception as e:
        return f"Error crítico al intentar programar la herramienta: {str(e)}"
