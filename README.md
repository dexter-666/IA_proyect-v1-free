# JARVIS AI -

Un poderoso asistente virtual avanzado para escritorio inspirado en la IA de Marvel. Este proyecto cuenta con integracion profunda en Windows, automatizacion cognitiva, control de entorno y una interfaz Glassmorphism holografica interactiva.

## Caracteristicas Principales

- **Interfaz Holografica:** Orbe reactivo y esquema de color inspirado en JARVIS (Era de Ultron) con tema dorado y animaciones de procesamiento dinamicas.
- **Comandos de Voz y Atajos Inteligentes:** Puedes llamarlo en cualquier momento, incluso si la ventana esta minimizada, usando la tecla global `Insert` para activar el microfono inmediatamente de manera nativa.
- **Control Contextual del Entorno:** Control autonomo del volumen, brillo, energia y Focus Assist basado en tus habitos y la ventana activa en pantalla.
- **Programacion Autonoma en Sandbox:** JARVIS puede escribirse sus propios scripts de habilidades (`auto_programmer`), compilarlos en frio y ejecutarlos con un timeout seguro en un entorno de pruebas, para inyectar su propio codigo en tiempo real si tiene exito.
- **Navegacion Web (YouTube):** Capacidad nativa de buscar musica y videos invisibles y reproducirlos automaticamente a traves del navegador web.
- **Organizador y Gestor de Archivos:** Abre, visualiza y edita documentos, sumado al analisis de archivos con clasificacion inteligente y eliminacion de duplicados exactos usando sumas `MD5`.
- **Comunicaciones Unificadas:** Envia informacion centralizada usando correos, Telegram, Discord y WhatsApp desde una sola interfaz base.

## Tecnologias

- **Python 3.12**
- **PyQt6** (Para la interfaz holografica dinamica y el QWebEngineView)
- **LLMs** (Soporte integrado para Gemini y OpenRouter)
- Integraciones de SO: `pycaw`, `pygetwindow`, `psutil`, `WMI`, `winreg` y llamadas directas al Win32 Kernel (`ctypes`) para el atajo global inteligente.

## Implementacion y Parches Arrelgad0s

- **Ejecutable standalone (EXE implementad0):** Ahora puedes descargar directamente el archivo `JARVIS.exe` generado con PyInstaller. No necesitas tener Python instalado ni crear un entorno virtual. El ejecutable incluye todas las dependencias y la interfaz holografica.
- **Parches criticos resueltos:**
  - Solucionado el error `ModuleNotFoundError: No module named '_socket'` durante el empaquetado, asegurando que el proceso hijo de PyInstaller encuentre correctamente los modulos nativos de Python.
  - Mejorada la deteccion de rutas de DLLs en Windows para evitar conflictos con entornos virtuales corruptos.
  - Añadido soporte para variables de entorno que fuerzan la carga de modulos nativos (`PYINSTALLER_ISOLATED_HOOKS=0` como alternativa).
  - El script de instalacion (`Instalar_JARVIS.bat`) ahora recrea el `.venv` desde cero si detecta inconsistencias, evitando errores de rutas absolutas.
- **Compilacion automatizada:** Se incluye el comando exacto de PyInstaller que genera el EXE con todos los `--collect-all` necesarios y la inclusion de recursos (`assets`, `config`, `memory`). El ejecutable resultante es portable y funciona en Windows 10 y 11.

## Instalacion y Uso

1. Instala [Python 3.12](https://www.python.org/downloads/) asegurandote de marcar "Add Python to PATH" (solo si deseas modificar el codigo fuente).
2. Clona este repositorio en tu escritorio:
   ```bash
   git clone https://github.com/tu-usuario/JARVIS-AI.git