# JARVIS AI -

Un poderoso asistente virtual avanzado para escritorio inspirado en la IA de Marvel. Este proyecto cuenta con integración profunda en Windows, automatización cognitiva, control de entorno y una interfaz *Glassmorphism* holográfica interactiva.

## 🌟 Características Principales

* **Interfaz Holográfica:** Orbe reactivo y esquema de color inspirado en JARVIS (Era de Ultrón) con tema dorado y animaciones de procesamiento dinámicas.
* **Comandos de Voz y Atajos Inteligentes:** Puedes llamarlo en cualquier momento, incluso si la ventana está minimizada, usando la tecla global `Insert` para activar el micrófono inmediatamente de manera nativa.
* **Control Contextual del Entorno:** Control autónomo del volumen, brillo, energía y *Focus Assist* basado en tus hábitos y la ventana activa en pantalla.
* **Programación Autónoma en Sandbox:** JARVIS puede escribirse sus propios scripts de habilidades (`auto_programmer`), compilarlos en frío y ejecutarlos con un timeout seguro en un entorno de pruebas, para inyectar su propio código en tiempo real si tiene éxito.
* **Navegación Web (YouTube):** Capacidad nativa de buscar música y videos invisibles y reproducirlos automáticamente a través del navegador web.
* **Organizador y Gestor de Archivos:** Abre, visualiza y edita documentos, sumado al análisis de archivos con clasificación inteligente y eliminación de duplicados exactos usando sumas `MD5`.
* **Comunicaciones Unificadas:** Envía información centralizada usando correos, Telegram, Discord, y WhatsApp desde una sola interfaz base.

## 🛠️ Tecnologías

* **Python 3.12**
* **PyQt6** (Para la interfaz holográfica dinámica y el QWebEngineView)
* **LLMs** (Soporte integrado para Gemini y OpenRouter)
* Integraciones de SO: `pycaw`, `pygetwindow`, `psutil`, `WMI`, `winreg` y llamadas directas al Win32 Kernel (`ctypes`) para el atajo global inteligente.

## 🚀 Instalación y Uso

1. Instala [Python 3.12](https://www.python.org/downloads/) asegurándote de marcar "Add Python to PATH".
2. Clona este repositorio en tu escritorio:
   ```bash
   git clone https://github.com/tu-usuario/JARVIS-AI.git
   ```
3. Ejecuta el archivo `Instalar_JARVIS.bat` para construir el entorno virtual (`.venv`) e instalar automáticamente todas las dependencias (`requirements.txt`).
4. Para iniciarlo rápidamente (y en segundo plano), puedes utilizar **`Iniciar JARVIS Beta.vbs`**.

## 🛡️ Notas de Seguridad
Este proyecto usa tu configuración local en `config/api_keys.json` para gestionar llaves maestras de API. Este archivo **no debe subirse** a GitHub bajo ningún concepto, por lo cual ya viene protegido automáticamente por el `.gitignore` nativo de esta rama.

---
*Desarrollado y mantenido con IA & 2PAC.*


