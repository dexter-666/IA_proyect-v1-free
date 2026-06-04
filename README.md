<div align="center">

# JARVIS AI ASSISTANT
### ▰ Autonomous System Interface ▰

<img src="https://raw.githubusercontent.com/dexter-666/IA_proyect-v1-free/main/assets/jarvis_icono.ico" width="150" />

---

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

</div>

---

### ◈ CORE ARCHITECTURE
**JARVIS** es un ecosistema de automatización avanzada diseñado nativamente para Windows. Su núcleo combina modelos ultra avanzados de procesamiento de lenguaje natural (NLP) con visión computacional de última generación para ofrecer una experiencia de usuario (UX) inmersiva, conversacional y sumamente proactiva.

### ▰ KEY CAPABILITIES
| Module | Functionality |
| :--- | :--- |
| **Gemini Live** | Interacción bidireccional de voz fluida, con interrupción inteligente (habla en medio de su oración para cortarlo). |
| **Vision Guardian** | Análisis contextual de pantalla en tiempo real mediante capturas de pantalla integradas. |
| **System Kernel** | Gestión nativa de hardware, configuraciones de Windows, archivos locales y procesos. |
| **Terminal Agent** | Ejecución autónoma de comandos directamente en la consola (Powershell / CMD). |
| **Hybrid Logic** | Detección offline ultrarrápida de activación (Vosk) + Procesamiento Cloud masivo (Gemini / OpenRouter). |
| **Multimedia** | Integración total con Spotify Web API para manejo musical absoluto con tu voz. |

---

### ◈ HARDWARE REQUIREMENTS

**Requisitos Mínimos:**
* **OS:** Windows 10 / 11 (64-bits)
* **CPU:** Procesador de 4 núcleos (ej. Intel Core i3 de 8va Gen o AMD Ryzen 3)
* **RAM:** 8 GB de memoria principal
* **Periféricos:** Micrófono y Altavoces funcionales (estrictamente requeridos para la interacción natural por voz).
* **Conectividad:** Conexión a Internet activa para la sinapsis en la nube de la IA.

**Recomendados (Para visión constante y procesamiento ultrafluido):**
* **OS:** Windows 11
* **CPU:** Procesador de 6 o más núcleos (ej. Intel Core i5/i7 o AMD Ryzen 5/7)
* **RAM:** 16 GB a 32 GB
* **GPU:** Tarjeta gráfica dedicada (NVIDIA/AMD) para el renderizado eficiente del visualizador de partículas de interfaz (PyQt6).

---

### ◈ COMANDOS ESTABLECIDOS Y PALABRAS CLAVE

Dado que JARVIS utiliza un modelo de Lenguaje Natural, **no necesitas usar comandos robóticos**, puedes hablarle como a una persona. Sin embargo, hay directrices específicas en su arquitectura:

* **Activación por voz (Wake-words):** Al dormir, el micrófono trabaja localmente. Solo di *"Jarvis"* o *"Despierta"* para arrancar su procesamiento principal en la nube.
* **Interrupción bidireccional:** Si JARVIS te está dando un discurso muy largo, simplemente **habla de vuelta**. El asistente cortará inmediatamente su audio para escuchar tu nueva instrucción.
* **Integración del Sistema (Windows):** Pídele directamente: *"Baja el brillo de la pantalla"*, *"Abre Google Chrome"*, *"Sube el volumen"*, *"Encuentra mi archivo de facturas"*.
* **Reconocimiento visual (OCR/Visión):** Usa comandos como *"Mira mi pantalla y dime si este código está bien"*, o *"Qué aplicación estoy usando ahora mismo"*.

---

### ◈ CONSIDERACIONES IMPORTANTES (A TENER EN CUENTA)

1. **Gestión y Seguridad de APIs:** Al usar este software, **es obligatorio** que ingreses tus propias credenciales (API Keys) de Google Gemini y OpenRouter en `config/api_keys.json` a través de la interfaz. **ADVERTENCIA:** Si clonas el repositorio, nunca subas el archivo con tus llaves reales a Internet.
2. **Audio I/O Correcto:** JARVIS detectará tus canales de audio, pero asegúrate en la interfaz gráfica de haber seleccionado el Índice correcto de tu micrófono y de los parlantes o te parecerá que el programa "no escucha".
3. **Efecto de Eco:** Al usar la interrupción por voz con altavoces a un volumen muy alto, el micrófono podría capturar la misma voz de JARVIS y auto-interrumpirse. Se recomienda usar a un nivel de volumen prudente o usar auriculares para la experiencia bidireccional perfecta.
4. **Dependencia de la Arquitectura:** Los controles físicos y accesos directos han sido construidos, diseñados y optimizados exclusivamente para la API de Windows.

---

### ◈ DEPLOYMENT PROTOCOL

Para descargar e inicializar el sistema correctamente, evita usar el botón "Download ZIP" de GitHub para el código fuente (debido a las dependencias). 

**Opción A: Ejecutable Automático (Recomendado)**
1. Dirígete a la sección **Releases** en este GitHub.
2. Descarga el archivo `JARVIS_Release_v1.zip`.
3. Descomprímelo en tu computadora y haz doble clic en `JARVIS.exe`.

**Opción B: Clonar el Código Fuente**
```bash
# 1. Clonar el repositorio
git clone https://github.com/dexter-666/IA_proyect-v1-free.git

# 2. Configurar Entorno
# Añade tus API Keys en el archivo 'config/api_keys.json' usando un editor o la misma UI.

# 3. Iniciar el Sistema (Vía Código)
pip install -r requirements.txt
python main.py
```
