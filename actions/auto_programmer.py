# -*- coding: utf-8 -*-
import json
import sys
import py_compile
import subprocess
import traceback
from pathlib import Path

def run_in_sandbox(tool_name: str, test_params: dict) -> tuple[bool, str]:
    """Ejecuta de manera segura la herramienta recién creada en un subproceso sandbox con timeout."""
    python_exe = sys.executable or ".venv/Scripts/python.exe"
    params_json = json.dumps(test_params)
    
    # Código que se ejecutará en el sandbox
    code = f"""
import sys
import json
try:
    from actions.{tool_name} import {tool_name}
    params = json.loads('''{params_json}''')
    res = {tool_name}(params, player=None)
    print("SUCCESS_OUTPUT:" + str(res))
except Exception as e:
    import traceback
    print("ERROR_TRACEBACK:", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
"""
    try:
        # Asegurarse de que el PYTHONPATH incluya el directorio de JARVIS
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent)

        res = subprocess.run(
            [python_exe, "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
            encoding="utf-8"
        )
        if res.returncode == 0:
            output = res.stdout.strip()
            if "SUCCESS_OUTPUT:" in output:
                return True, output.split("SUCCESS_OUTPUT:", 1)[1]
            return True, output
        else:
            err_output = res.stderr.strip() or res.stdout.strip()
            return False, err_output
    except subprocess.TimeoutExpired:
        return False, "Error: Timeout de ejecución en sandbox (límite de 5 segundos excedido). ¿Posible bucle infinito?"
    except Exception as e:
        return False, f"Fallo al ejecutar en el sandbox: {e}"

def auto_programmer(parameters: dict, player=None) -> str:
    """
    Desarrollo y Auto-Programación autónoma. Permite escribir herramientas nuevas,
    validar sintaxis (py_compile), correr tests sintácticos en sandbox con traceback 
    y registrar dinámicamente el plugin en memoria (main.py) y persistencia (custom_tools.json).
    """
    action = parameters.get("action", "create_tool").lower()
    tool_name = parameters.get("tool_name", "")
    description = parameters.get("description", "")
    parameters_schema_str = parameters.get("parameters_schema", "{}")
    python_code = parameters.get("python_code", "")
    test_params = parameters.get("test_parameters", {})

    if not tool_name:
        return "Error: Se requiere especificar 'tool_name' para cualquier acción de auto-programación."

    actions_dir = Path(__file__).resolve().parent
    tool_file = actions_dir / f"{tool_name}.py"

    if action == "create_tool" or action == "fix_tool":
        if not python_code:
            return "Error: Se requiere proporcionar el código Python ('python_code') para programar."

        # Asegurar formato utf-8
        try:
            tool_file.write_text(python_code, encoding="utf-8")
        except Exception as e:
            return f"Error guardando el código fuente: {e}"

        # 1. Chequeo Sintáctico (py_compile)
        try:
            py_compile.compile(str(tool_file), doraise=True)
        except py_compile.PyCompileError as compile_err:
            # Retornar error de compilación detallado para auto-corrección
            return (
                f"Sintaxis Inválida en '{tool_name}.py'. "
                f"Rastreo del error para auto-corrección:\n\n{compile_err.msg}"
            )

        # 2. Validación de Ejecución (Sandbox Run)
        success, sandbox_res = run_in_sandbox(tool_name, test_params)
        if not success:
            # Retornar traceback del sandbox para auto-corrección
            return (
                f"Fallo de Ejecución en Sandbox para la herramienta '{tool_name}'. "
                f"Rastreo del error (traceback) para que lo analices y corrijas:\n\n{sandbox_res}"
            )

        # 3. Construcción del JSON Schema para registro
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
            "description": description or f"Herramienta autónoma {tool_name}",
            "parameters": {
                "type": "OBJECT",
                "properties": properties,
                "required": list(properties.keys())
            }
        }

        # 4. Guardar definición en custom_tools.json (Persistencia)
        custom_tools_path = actions_dir / "custom_tools.json"
        custom_tools = []
        if custom_tools_path.exists():
            try:
                custom_tools = json.loads(custom_tools_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Reemplazar versión previa
        custom_tools = [t for t in custom_tools if t["name"] != tool_name]
        custom_tools.append(new_tool_def)
        custom_tools_path.write_text(json.dumps(custom_tools, indent=4, ensure_ascii=False), encoding="utf-8")

        # 5. Inyección dinámica en memoria de main.py
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'TOOL_DECLARATIONS'):
            main_module.TOOL_DECLARATIONS = [t for t in main_module.TOOL_DECLARATIONS if t.get("name") != tool_name]
            main_module.TOOL_DECLARATIONS.append(new_tool_def)

        # 6. Forzar la reconexión de sesión cognitiva de JARVIS
        reload_msg = ""
        if player and hasattr(player, "on_config_saved"):
            from threading import Timer
            def delayed_reload():
                try:
                    player.on_config_saved({})
                except Exception:
                    pass
            Timer(1.5, delayed_reload).start()
            reload_msg = " Reiniciando mis módulos cognitivos dinámicamente para incorporarla de inmediato..."

        return (
            f"¡Herramienta '{tool_name}' desarrollada e integrada con éxito!\n"
            f"- Compilación: Exitosa\n"
            f"- Prueba en Sandbox: Exitosa. Retornó: {sandbox_res}\n"
            f"- Persistencia e Inyección: Completadas.{reload_msg}"
        )

    elif action == "test_tool":
        if not tool_file.exists():
            return f"Error: La herramienta '{tool_name}' no existe físicamente en '{tool_file.name}'."
        
        success, sandbox_res = run_in_sandbox(tool_name, test_params)
        if success:
            return f"Prueba manual de sandbox exitosa. Retornó: {sandbox_res}"
        else:
            return f"Fallo en sandbox manual:\n\n{sandbox_res}"

    elif action == "list_tools":
        custom_tools_path = actions_dir / "custom_tools.json"
        if not custom_tools_path.exists():
            return "No se ha desarrollado ninguna herramienta personalizada autónoma todavía."
        try:
            custom_tools = json.loads(custom_tools_path.read_text(encoding="utf-8"))
            if not custom_tools:
                return "La lista de herramientas personalizadas está vacía."
            res = "Herramientas Desarrolladas de Forma Autónoma:\n"
            for idx, t in enumerate(custom_tools, 1):
                res += f"{idx}. {t.get('name')} - {t.get('description')}\n"
            return res
        except Exception as e:
            return f"Error leyendo lista de herramientas: {e}"

    else:
        return f"Acción de auto-programación '{action}' no soportada."
