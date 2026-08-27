# CHANGELOG - J4ck Cleaner

Todos los cambios notables en este proyecto serán documentados procedimentalmente en este archivo.

## [1.2.5-staging] - 2026-08-12 (Fase 3 - Hito 75/100)

### Añadido y Consolidado
- **Búsqueda en Tiempo Real en la Lista Blanca:**
  - Entrada de texto con filtrado dinámico para la lista de aplicaciones protegidas en la pestaña *Lista Blanca*.
- **Restablecimiento de Ajustes a Valores de Fábrica:**
  - Método `reset_to_defaults()` y botón *Restablecer Ajustes por Defecto* en la pestaña *Ajustes*.
- **Directiva de Resguardo de Datos (Data Loss Safeguard Policy):**
  - Consolidada en `.agents/rules/code-style-eni.md`.
- **Caja Informativa de Comandos y Atajos CLI:**
  - Panel estático en *Ajustes* con los comandos `--clean`, `--report`, `--test`, `--info` y `--profile`.
- **Etiqueta de Versión del Sistema:**
  - Etiqueta estática `J4ck Cleaner v1.2.0` al pie de la barra lateral.
- **Resguardo Atómico de Ajustes (`settings.json.bak`):**
  - Guardado atómico con archivo `.tmp` y copia de respaldo `.bak` en `core/config.py`.
- **Deslizador de Frecuencia de Muestreo de Sensores:**
  - Control de intervalo (500ms - 3000ms) en la pestaña *Ajustes*.
- **Auditoría de Módulos del Kernel:**
  - Verificación de módulos `amdgpu` y `k10temp` integrada en la Suite de Auto-Diagnóstico (`--test`).
- **Comando CLI `--info` de 1 Línea:**
  - Salida instantánea para barras de estado (Waybar, Noctalia Shell) e inspección en scripts: `j4ck-cleaner --info`.
- **Garantía de OOM y Limpieza Preventiva de RAM al 90%:**
  - Ejecución de desfragmentación automática cuando la RAM física ocupada supera el 90% (con throttle de 60 segundos).
- **Indicador de Red CA / Batería en el Pie:**
  - Muestreo `psutil.sensors_battery()` mostrando estado `🔌 CA` o `🔋 Batería (XX%)` en el pie del Dashboard.
- **Registro de Alertas Térmicas en Logs (`core/logger.py`):**
  - Emisión de advertencias a los archivos de log de 7 días al activarse el Thermal Guard.
- **Corrección de Duplicación en el Lanzador de Aplicaciones:**
  - Purga de la entrada de escritorio obsoleta `nocturne-guardian.desktop` en `~/.local/share/applications/` para mantener un único lanzador `j4ck-cleaner.desktop`.
- **Integración y Compilación de Binario Nativo Standalone (`build-bin.sh` & `install.sh`):**
  - Compilación PyInstaller verificada (`dist/j4ck-cleaner-bin`). El script del lanzador `$PATH` ahora ejecuta automáticamente el binario nativo si existe.
- **Corrección de Excepciones NameError en la Interfaz Gráfica (`j4ck_cleaner/ui/dashboard.py`):**
  - Importación requerida de `QProgressBar` desde `PySide6.QtWidgets`.
  - Corrección de referencia a `self.sidebar_frame` al incorporar la barra lateral a la ventana principal.



## [1.2.0-staging] - 2026-08-12 (Fase 3 - Hito 50/100)

### Añadido y Estandarizado (J4ckENI Framework)
- **Rebranding Oficial a J4ck Cleaner (`j4ck_cleaner`):**
  - Actualización completa del paquete principal de `nocturne_guardian` a `j4ck_cleaner`.
  - Registro de alias de binario ejecutable `j4ck-cleaner` en `$PATH` y lanzador desktop.
- **Navegación por Barra Lateral Nocturne (Sidebar Tabs):**
  - Panel lateral Cyberpunk abisal en negro mate con 4 pestañas interactivas: *Dashboard*, *Núcleos CPU*, *Lista Blanca*, *Ajustes*.
  - Transición fluida con desvanecimiento `QGraphicsOpacityEffect` de 150ms al alternar pestañas.
- **Indicador Radial de Salud Global (`SystemHealthGaugeWidget`):**
  - Anillo de progreso radial dibujado en QPainter con índice de salud (0-100%) y estados de color dinámicos (Cian/Amarillo/Carmesí).
- **Matriz Visual por Núcleo de CPU (`CpuCoreMatrixWidget`):**
  - Telemetría independiente para Core 0..3 de la APU AMD PRO A10 con barras de progreso de carga % y frecuencia en MHz.
- **Gestor de Lista Blanca de Protección:**
  - Pestaña interactiva para añadir y eliminar aplicaciones protegidas almacenadas en `~/.config/nocturne-guardian/settings.json`.
- **Selector de Gobernador de CPU del Kernel:**
  - Selector dinámico de gobernador (`schedutil`, `performance`, `powersave`, `ondemand`) integrado en la pestaña Ajustes.
- **Barra de Estado Inferior con Uptime y RAM Liberada:**
  - Rastreador de tiempo activo de sesión (ej. `⏱️ Uptime: 01h 24m`) y acumulador de memoria RAM liberada en el día.
- **Suite de Auto-Diagnóstico de Integridad (`core/selftest.py` & `--test`):**
  - Motor de pruebas automáticas para verificar rutas sysfs, permisos Polkit, versión de Python y salud de sensores.
- **Generador de Reportes de Diagnóstico (`--report`):**
  - Generador de reportes de hardware en JSON almacenados en `~/.config/nocturne-guardian/system-diagnostics.json`.
- **Sistema de Logging Rotativo a 7 Días (`core/logger.py`):**
  - Rotación y purga automática diaria de logs en `~/.config/nocturne-guardian/logs/`.
- **Compilador Standalone Native (`build-bin.sh`):**
  - Script automatizado PyInstaller para empaquetar ejecutables de 1 solo archivo para GitHub Releases.

## [1.1.0] - 2026-08-12 (Fase 3)

### Añadido
- **Telemetría Completa de GPU y VRAM (`core/sensors.py`):**
  - Muestreo en tiempo real de Temperatura GPU (°C), VRAM ocupada (MB/GB), VRAM total y Consumo Energético en Watts (PPT/Power).
  - Card telemétrica `GPU / VRAM` integrada en la fila principal del Dashboard Qt6.
- **Minimizado a la Bandeja del Sistema (System Tray / AppIndicator):**
  - Integración de `QSystemTrayIcon` con menú contextual (*Mostrar*, *Turbo Clean*, *Cambio de Perfiles*, *Salir*).
- **Gestión de Perfiles JSON (`core/profiles.py`):**
  - Carga y guardado de perfiles en `~/.config/nocturne-guardian/profiles.json`.
- **Integración Polkit Freedesktop (`assets/polkit/`):**
  - Regla de autorización Polkit para ejecutar la desfragmentación de caché RAM sin contraseña.

## [1.0.0] - 2026-08-12

### Añadido (Fase 1 & Fase 2)
- **Interfaz Gráfica Nativa (Qt6 / PySide6):**
  - Dashboard telemétrico con monitoreo en tiempo real de Temperatura CPU (°C), Uso %, Frecuencia (MHz), Memoria RAM (GB) y Swap.
  - Gráfica dinámica integrada con renderizado `matplotlib` QTAgg.
  - Botón de acción `⚡ TURBO CLEAN & COOLDOWN` para desfragmentar caché de RAM (`drop_caches`) sin perder datos.
- **Estandarización de Reglas (`.agents/rules/`):**
  - Estilo de código bajo el Protocolo Ponytail y directiva de 0 Elipsis.
  - Especificación oficial del **J4ckENI Framework (J4ck Library)** co-mantenido por Jack & ENI.
