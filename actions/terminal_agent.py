# -*- coding: utf-8 -*-
import subprocess
import os

def terminal_agent(parameters: dict, player=None) -> str:
    """
    Ejecuta cualquier comando en la terminal de Windows (PowerShell o CMD).
    JARVIS puede usar esto para cualquier tarea del sistema operativo:
    instalar/desinstalar programas, consultar información, ejecutar scripts,
    manejar archivos, redes, configuraciones, etc.
    """
    command = parameters.get("command", "")
    shell_type = parameters.get("shell", "powershell").lower()
    timeout_sec = int(parameters.get("timeout", 120))
    run_as_admin = parameters.get("admin", False)
    working_dir = parameters.get("working_directory", None)

    if not command:
        return "No se proporcionó ningún comando para ejecutar."

    # Limitar timeout a un rango razonable
    timeout_sec = max(10, min(timeout_sec, 600))

    try:
        if shell_type == "cmd":
            cmd_args = ["cmd", "/c", command]
        else:
            # PowerShell por defecto — UTF-8 forzado para salida limpia
            cmd_args = [
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command",
                f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}"
            ]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=working_dir,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
            env=env,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            if output:
                # Salida hasta 3000 chars para que JARVIS tenga contexto suficiente
                if len(output) > 3000:
                    output = output[:3000] + "\n...[Salida truncada]"
                return f"Comando ejecutado exitosamente:\n{output}"
            else:
                return "Comando ejecutado exitosamente (sin salida)."
        else:
            # Incluir tanto stdout como stderr para diagnóstico
            combined = ""
            if error:
                combined += f"STDERR:\n{error}\n"
            if output:
                combined += f"STDOUT:\n{output}"
            if not combined:
                combined = "(sin salida de error)"
            return f"El comando finalizó con código {result.returncode}:\n{combined}"

    except subprocess.TimeoutExpired:
        return f"Error: El comando excedió el timeout de {timeout_sec} segundos y fue terminado."
    except FileNotFoundError:
        return f"Error: No se encontró el ejecutable para shell '{shell_type}'."
    except Exception as e:
        return f"Excepción ejecutando terminal: {str(e)}"
