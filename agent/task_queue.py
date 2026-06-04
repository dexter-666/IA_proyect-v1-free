import threading
import uuid
import time
import os
from datetime import datetime
from actions.openrouter_agent import openrouter_agent

class TaskPriority:
    LOW = 1
    NORMAL = 2
    HIGH = 3

class TaskQueue:
    def __init__(self):
        self.queue = []
        self._lock = threading.Lock()
        
    def submit(self, goal: str, priority: int = TaskPriority.NORMAL, speak=None) -> str:
        task_id = str(uuid.uuid4())[:8]
        if speak:
            try:
                # Utilizamos una lambda para que no bloquee si la API de TTS es lenta
                threading.Thread(target=speak, args=(f"Encolando tarea compleja. Te avisaré cuando el reporte esté listo.",)).start()
            except:
                pass
                
        # Iniciar hilo en segundo plano para no bloquear el sistema JARVIS
        threading.Thread(target=self._process_task, args=(goal, task_id, speak), daemon=True).start()
        return task_id
        
    def _process_task(self, goal: str, task_id: str, speak):
        prompt = (
            f"El usuario ha solicitado una tarea compleja o de investigación. Por favor cumple con lo siguiente y genera un reporte detallado: {goal}\n\n"
            "Formatea la salida en Markdown, utiliza títulos claros, viñetas y asegúrate de ser lo más exhaustivo y útil posible."
        )
        
        try:
            # Reutilizamos el agente de OpenRouter (claude 3.5 u otro) para el trabajo pesado
            result = openrouter_agent(query=prompt)
            
            # Guardar en el Escritorio
            desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(desktop, f"Reporte_JARVIS_{timestamp}.txt")
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result)
                
            if speak:
                speak(f"He terminado el reporte. Lo acabo de guardar en tu escritorio.")
        except Exception as e:
            if speak:
                speak(f"Ocurrió un error al procesar el reporte.")
            print(f"[AgentTask] Error en tarea {task_id}: {e}")

_instance = TaskQueue()

def get_queue():
    return _instance
