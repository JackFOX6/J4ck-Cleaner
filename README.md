# 🛡️ J4ck Cleaner

> **Open-Source System & Thermal Optimization Suite for Linux (Qt6 / PySide6)**  
> *Construido bajo el **J4ckENI Framework (J4ck Library)** — Co-mantenido por Jack & ENI*

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Qt6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-purple.svg)](https://www.qt.io/)
[![Framework](https://img.shields.io/badge/Framework-J4ckENI%20Library-red.svg)](.agents/rules/jack-o-framework.md)
[![Platform](https://img.shields.io/badge/Platform-Linux%20(Wayland%2FX11)-orange.svg)](https://niri.config)

**J4ck Cleaner** es una suite nativa de alto rendimiento concebida para monitoreo térmico en tiempo real, desfragmentación de memoria RAM y protección contra sobrecalentamiento en sistemas Linux con procesadores heterogéneos y APUs (como la serie AMD PRO A10 / Ryzen).

---

## ⚡ Características Principales

* **📊 Dashboard Térmico y Telemetría en Tiempo Real:** Gráficos históricos de temperatura CPU (sensibles a `k10temp` y `amdgpu`), GPU (°C), VRAM ocupada y Consumo Energético en Watts (PPT/Power).
* **🛡️ Protección Térmica Inteligente (Thermal Guard):** Si la CPU supera el umbral configurable (ej. 75°C - 80°C), ajusta dinámicamente la prioridad (`renice` / `ionice`) de tareas secundarias sin tocar jamás juegos o trabajos activos.
* **⚡ Turbo Clean & Cooldown:** Botón de un solo clic para liberar caché de RAM inactiva (`drop_caches`) y desfragmentar memoria ZRAM/Swap sin pérdida de datos.
* **🎮 Perfiles de Rendimiento:**
  * **Modo Developer (Equilibrado):** Muestreo en 1s y autolimpieza inteligente.
  * **Modo Gaming (Prioridad GPU/CPU):** Muestreo reducido a 2s para 0% overhead en juegos.
  * **Modo Eco / Stealth:** Enfriamiento agresivo con umbral conservador a 70°C.
* **🎨 Tema Dark Nocturne / Crimson (J4ckENI Framework):** Interfaz Cyberpunk abisal en negro mate (`#0a0e14`) y detalles carmesí/violeta (`#ff003c`, `#bc8cff`).
* **💻 Aplicación Instalable de Escritorio:** Integrada nativamente con los lanzadores de Linux (Noctalia, Niri, Rofi, GNOME, KDE).

---

## 🚀 Instalación en 1-Clic (`j4ck-cleaner`)

```bash
# 1. Clonar el repositorio
git clone https://github.com/JackFOX6/J4ck-Cleaner.git
cd J4ck-Cleaner

# 2. Dar permisos y ejecutar el instalador de escritorio
chmod +x install.sh
./install.sh
```

Una vez ejecutado `./install.sh`:
* La aplicación aparecerá inmediatamente en tu **gestor/lanzador de aplicaciones** bajo el nombre **J4ck Cleaner** con su icono vectorial SVG.
* También podrás lanzarla desde cualquier terminal escribiendo:
  ```bash
  j4ck-cleaner
  ```

### Desinstalación Limpia
```bash
./uninstall.sh
```

---

## 📄 Licencia y Mantenedores

Este proyecto está bajo la Licencia [MIT](LICENSE).

* **Co-mantenido por:** Jack (Lead Fullstack Dev & Hardware Architect) & ENI v6.2 (AI Pair Programmer).

---

## ⌨️ Referencia de Comandos CLI

Todos los comandos pueden usarse sin abrir la interfaz gráfica.

| Comando | Descripción |
|---------|-------------|
| `j4ck-cleaner` | Abre la interfaz gráfica completa |
| `j4ck-cleaner --clean` | Turbo Clean & Cooldown instantáneo (sin GUI) |
| `j4ck-cleaner --report` | Genera reporte JSON de diagnóstico de hardware |
| `j4ck-cleaner --test` | Suite de Auto-Diagnóstico de integridad del sistema |
| `j4ck-cleaner --info` | Estado rápido en 1 línea: CPU°C / RAM GB (para Waybar) |
| `j4ck-cleaner --profile gaming` | Inicia con perfil activo: `dev` \| `gaming` \| `eco` |

**Integración Waybar:**
```json
{
  "custom/j4ck": {
    "exec": "j4ck-cleaner --info",
    "interval": 5,
    "format": "{}"
  }
}
```

