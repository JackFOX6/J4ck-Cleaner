# 🛡️ J4ck Cleaner

> **J4ck Cleaner es un programa open source mantenido por J4ck para usuarios de Linux con Wayland. Hecho únicamente para pruebas.**

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Qt6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-purple.svg)](https://www.qt.io/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20(Wayland%2FX11)-orange.svg)](https://github.com/JackFOX6/J4ck-Cleaner)
[![Status](https://img.shields.io/badge/Status-Experimental%20Prototype-yellow.svg)](https://github.com/JackFOX6/J4ck-Cleaner)

---

> ⚠️ **Aviso de Prototipo / Disclaimer:**  
> Este software es un **prototipo experimental desarrollado únicamente con fines de prueba y evaluación técnica** en entornos Linux bajo Wayland/X11. No representa un software final, comercial o completamente estable, y **puede contener errores o comportamientos imprevistos**. Úselo bajo su propia discreción.

---

## 📌 Descripción General

**J4ck Cleaner** es una herramienta experimental concebida para pruebas de monitoreo térmico en tiempo real, análisis de memoria RAM y comprobación de perfiles de rendimiento en sistemas operativos Linux con entornos de escritorio basados en Wayland y X11.

---

## ⚡ Características Experimentales

* **📊 Telemetría y Dashboard Térmico:** Mapeo de métricas de temperatura CPU (`k10temp` / `amdgpu`), uso de VRAM y estimación de consumo energético.
* **🛡️ Lógica de Protección Térmica (Thermal Guard):** Evaluación de umbrales configurables y ajuste de prioridades (`renice` / `ionice`) de tareas secundarias.
* **⚡ Rutinas de Liberación de Memoria:** Métodos de prueba para liberación de caché inactiva (`drop_caches`) y gestión de memoria swap/ZRAM.
* **🎮 Perfiles de Prueba:**
  * **Modo Developer:** Muestreo a 1s para análisis continuo de recursos.
  * **Modo Gaming:** Muestreo a 2s para menor consumo de ciclos de CPU.
  * **Modo Eco:** Enfriamiento con umbrales conservadores.
* **🎨 Interfaz Gráfica Nocturne:** Desarrollada en Python con PySide6 (Qt6) y estilo dark mode de alto contraste.

---

## 🚀 Instalación y Prueba

```bash
# 1. Clonar el repositorio
git clone https://github.com/JackFOX6/J4ck-Cleaner.git
cd J4ck-Cleaner

# 2. Dar permisos y ejecutar el instalador de prueba
chmod +x install.sh
./install.sh
```

### Ejecución
```bash
j4ck-cleaner
```

### Desinstalación
```bash
./uninstall.sh
```

---

## ⌨️ Referencia de Comandos CLI

| Comando | Descripción |
|---------|-------------|
| `j4ck-cleaner` | Abre la interfaz gráfica completa |
| `j4ck-cleaner --clean` | Prueba de limpieza y enfriamiento (sin GUI) |
| `j4ck-cleaner --report` | Genera reporte JSON de diagnóstico de hardware |
| `j4ck-cleaner --test` | Suite de Auto-Diagnóstico de integridad del sistema |
| `j4ck-cleaner --info` | Estado en una línea para paneles de escritorio (Waybar) |
| `j4ck-cleaner --profile gaming` | Inicia con perfil específico: `dev` \| `gaming` \| `eco` |

---

## 📄 Licencia

Este proyecto está bajo la Licencia [MIT](LICENSE).
Mantenido por **Jack** como prototipo de investigación y pruebas open source.
