import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QStackedWidget, QLineEdit, QListWidget, QListWidgetItem, QCheckBox, QComboBox,
    QGraphicsOpacityEffect, QSystemTrayIcon, QMenu, QProgressBar
)
from PySide6.QtCore import Qt, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QAction

from j4ck_cleaner.core.sensors import SystemSensorThread
from j4ck_cleaner.core.optimizer import SystemOptimizerEngine, TEMP_MIN_SLIDER, TEMP_MAX_SLIDER
from j4ck_cleaner.core.profiles import PROFILES, PerformanceProfile
from j4ck_cleaner.core.config import settings_mgr
from j4ck_cleaner.core.logger import logger
from j4ck_cleaner.ui.theme import DARK_NOCTURNE_QSS
from j4ck_cleaner.ui.widgets import MetricCard, RealtimePlotWidget, CpuCoreMatrixWidget


class J4ckCleanerWindow(QMainWindow):
    """
    Main Window Dashboard & Sidebar Navigation for J4ck Cleaner v1.2.5.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("J4ck Cleaner v1.2.5")
        self.resize(1080, 720)

        # Apply design system
        self.setStyleSheet(DARK_NOCTURNE_QSS)

        # Core Engines
        import time
        self.session_start_time = time.time()
        self.total_ram_freed_mb = 0.0
        self.last_auto_clean_time = 0.0

        self.active_profile = PROFILES["dev"]
        self.optimizer = SystemOptimizerEngine(
            thermal_threshold_c=self.active_profile.thermal_threshold_c
        )
        self.sensor_thread = SystemSensorThread(
            sample_interval_ms=self.active_profile.sample_interval_ms
        )

        # Setup UI & System Tray
        self._init_ui()
        self._setup_tray_icon()

        # Connect Signals
        self.sensor_thread.metrics_updated.connect(self.on_metrics_updated)
        self.sensor_thread.start()

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar Navigation (fixed 220px, always expanded)
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("cardFrame")
        self.sidebar_frame.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(12)

        header_side_layout = QHBoxLayout()
        self.app_title = QLabel("🛡️ J4CK CLEANER")
        self.app_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #ff003c; letter-spacing: 1px;")

        header_side_layout.addWidget(self.app_title)

        self.app_sub = QLabel("J4ckENI Framework")
        self.app_sub.setStyleSheet("font-size: 11px; color: #8b949e;")

        sidebar_layout.addLayout(header_side_layout)
        sidebar_layout.addWidget(self.app_sub)
        sidebar_layout.addSpacing(12)

        # Navigation Buttons
        self.nav_btn_dash = QPushButton("📊 Dashboard")
        self.nav_btn_dash.setObjectName("profileButton")
        self.nav_btn_dash.setCheckable(True)
        self.nav_btn_dash.setChecked(True)

        self.nav_btn_cores = QPushButton("🔲 Núcleos CPU")
        self.nav_btn_cores.setObjectName("profileButton")
        self.nav_btn_cores.setCheckable(True)

        self.nav_btn_whitelist = QPushButton("🛡️ Lista Blanca")
        self.nav_btn_whitelist.setObjectName("profileButton")
        self.nav_btn_whitelist.setCheckable(True)

        self.nav_btn_settings = QPushButton("⚙️ Ajustes")
        self.nav_btn_settings.setObjectName("profileButton")
        self.nav_btn_settings.setCheckable(True)

        sidebar_layout.addWidget(self.nav_btn_dash)
        sidebar_layout.addWidget(self.nav_btn_cores)
        sidebar_layout.addWidget(self.nav_btn_whitelist)
        sidebar_layout.addWidget(self.nav_btn_settings)
        sidebar_layout.addStretch()

        self.status_badge_side = QLabel("ACTIVO")
        self.status_badge_side.setAlignment(Qt.AlignCenter)
        self.status_badge_side.setStyleSheet(
            "background-color: #00d4ff15; color: #00d4ff; font-weight: 700; "
            "border: 1px solid #00d4ff44; border-radius: 8px; padding: 6px 12px; font-size: 11px;"
        )

        self.side_health_pbar = QProgressBar()
        self.side_health_pbar.setRange(0, 100)
        self.side_health_pbar.setValue(100)
        self.side_health_pbar.setTextVisible(False)
        self.side_health_pbar.setFixedHeight(6)

        lbl_ver_side = QLabel("J4ck Cleaner v1.2.5")
        lbl_ver_side.setAlignment(Qt.AlignCenter)
        lbl_ver_side.setStyleSheet("font-size: 10px; color: #8b949e; margin-top: 4px;")

        sidebar_layout.addWidget(self.status_badge_side)
        sidebar_layout.addWidget(self.side_health_pbar)
        sidebar_layout.addWidget(lbl_ver_side)

        main_layout.addWidget(self.sidebar_frame)

        # 2. Right Content Pages StackedWidget
        self.stacked_pages = QStackedWidget()
        
        # Build Pages
        self._init_dashboard_page()
        self._init_cores_page()
        self._init_whitelist_page()
        self._init_settings_page()

        main_layout.addWidget(self.stacked_pages)

        # Connect Sidebar Navigation Signals
        self.nav_btn_dash.clicked.connect(lambda: self.switch_page(0))
        self.nav_btn_cores.clicked.connect(lambda: self.switch_page(1))
        self.nav_btn_whitelist.clicked.connect(lambda: self.switch_page(2))
        self.nav_btn_settings.clicked.connect(lambda: self.switch_page(3))




    def switch_page(self, index: int):
        """Switch active view page with smooth fade transition."""
        if self.stacked_pages.currentIndex() == index:
            return

        target_widget = self.stacked_pages.widget(index)
        if target_widget:
            opacity_effect = QGraphicsOpacityEffect(target_widget)
            target_widget.setGraphicsEffect(opacity_effect)
            
            anim = QPropertyAnimation(opacity_effect, b"opacity", self)
            anim.setDuration(150)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutQuad)
            
            self.stacked_pages.setCurrentIndex(index)
            anim.start(QPropertyAnimation.DeleteWhenStopped)

        self.nav_btn_dash.setChecked(index == 0)
        self.nav_btn_cores.setChecked(index == 1)
        self.nav_btn_whitelist.setChecked(index == 2)
        self.nav_btn_settings.setChecked(index == 3)

    @staticmethod
    def _make_separator() -> QFrame:
        """Returns a thin horizontal line separator matching the card border color."""
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #2a2f3a; border: none; margin: 4px 0px;")
        return sep

    def _init_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Cards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_temp = MetricCard("Temperatura CPU", "°C")
        self.card_gpu = MetricCard("GPU / VRAM", "°C")
        self.card_cpu = MetricCard("Carga de CPU", "%")
        self.card_ram = MetricCard("Uso de RAM", "GB")
        self.card_swap = MetricCard("Swap", "GB")

        cards_layout.addWidget(self.card_temp)
        cards_layout.addWidget(self.card_gpu)
        cards_layout.addWidget(self.card_cpu)
        cards_layout.addWidget(self.card_ram)
        cards_layout.addWidget(self.card_swap)
        layout.addLayout(cards_layout)
        layout.addWidget(self._make_separator())

        # Middle Section (Plot + Profiles)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(12)

        self.plot_widget = RealtimePlotWidget(title="Temperatura en Tiempo Real (°C)")
        middle_layout.addWidget(self.plot_widget, stretch=3)

        controls_frame = QFrame()
        controls_frame.setObjectName("cardFrame")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(16, 16, 16, 16)
        controls_layout.setSpacing(12)

        profile_title = QLabel("PERFILES DE RENDIMIENTO")
        profile_title.setObjectName("cardTitle")
        controls_layout.addWidget(profile_title)

        btn_layout = QHBoxLayout()
        self.btn_dev = QPushButton("DEV")
        self.btn_dev.setObjectName("profileButton")
        self.btn_dev.setCheckable(True)
        self.btn_dev.setChecked(True)

        self.btn_gaming = QPushButton("GAMING")
        self.btn_gaming.setObjectName("profileButton")
        self.btn_gaming.setCheckable(True)

        self.btn_eco = QPushButton("ECO")
        self.btn_eco.setObjectName("profileButton")
        self.btn_eco.setCheckable(True)

        btn_layout.addWidget(self.btn_dev)
        btn_layout.addWidget(self.btn_gaming)
        btn_layout.addWidget(self.btn_eco)
        controls_layout.addLayout(btn_layout)

        self.btn_dev.clicked.connect(lambda: self.switch_profile("dev"))
        self.btn_gaming.clicked.connect(lambda: self.switch_profile("gaming"))
        self.btn_eco.clicked.connect(lambda: self.switch_profile("eco"))

        self.slider_label = QLabel(f"Umbral Térmico Preventivo: {self.active_profile.thermal_threshold_c:.0f}°C")
        self.slider_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #c9d1d9;")
        
        self.thermal_slider = QSlider(Qt.Horizontal)
        self.thermal_slider.setRange(TEMP_MIN_SLIDER, TEMP_MAX_SLIDER)
        self.thermal_slider.setValue(int(self.active_profile.thermal_threshold_c))
        self.thermal_slider.valueChanged.connect(self.on_slider_changed)

        controls_layout.addWidget(self.slider_label)
        controls_layout.addWidget(self.thermal_slider)

        self.desc_label = QLabel(self.active_profile.description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        controls_layout.addWidget(self.desc_label)

        middle_layout.addWidget(controls_frame, stretch=2)
        layout.addLayout(middle_layout)
        layout.addWidget(self._make_separator())

        # Bottom Action Section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        self.btn_clean = QPushButton("🧹 LIMPIAR SISTEMA")
        self.btn_clean.setObjectName("actionButton")
        self.btn_clean.clicked.connect(self.on_clean_clicked)

        self.table_procs = QTableWidget()
        self.table_procs.setColumnCount(4)
        self.table_procs.setHorizontalHeaderLabels(["PID", "Proceso", "CPU %", "RAM MB"])
        self.table_procs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_procs.verticalHeader().setVisible(False)
        self.table_procs.setFixedHeight(130)

        left_bottom_layout = QVBoxLayout()
        left_bottom_layout.addWidget(self.btn_clean)
        
        self.log_label = QLabel("Estado: Monitoreando sistema.")
        self.log_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        
        self.footer_stats_label = QLabel("⏱️ Uptime: 00h 00m | ⚡ RAM Liberada: 0 MB")
        self.footer_stats_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #bc8cff;")

        left_bottom_layout.addWidget(self.log_label)
        left_bottom_layout.addWidget(self.footer_stats_label)

        bottom_layout.addLayout(left_bottom_layout, stretch=2)
        bottom_layout.addWidget(self.table_procs, stretch=3)
        layout.addLayout(bottom_layout)

        self.stacked_pages.addWidget(page)

    def _init_cores_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🔲 TELEMETRÍA POR NÚCLEO DE CPU")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ff003c;")
        layout.addWidget(title)

        self.cpu_matrix = CpuCoreMatrixWidget(num_cores=4)
        layout.addWidget(self.cpu_matrix)
        layout.addStretch()

        self.stacked_pages.addWidget(page)

    def _init_whitelist_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("🛡️ LISTA BLANCA DE PROTECCIÓN")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ff003c;")
        sub = QLabel("Las aplicaciones registradas aquí NUNCA serán pausadas ni sufrirán reajuste de prioridad.")
        sub.setStyleSheet("font-size: 12px; color: #8b949e;")

        layout.addWidget(title)
        layout.addWidget(sub)

        # Input row
        input_layout = QHBoxLayout()
        self.whitelist_input = QLineEdit()
        self.whitelist_input.setPlaceholderText("Nombre de proceso (ej. obs, minecraft, vlc)...")
        self.whitelist_input.setStyleSheet(
            "background-color: #0d1117; border: 1px solid #21262d; border-radius: 8px; padding: 8px; color: #ffffff;"
        )
        
        btn_add = QPushButton("Añadir Aplicación")
        btn_add.setObjectName("profileButton")
        btn_add.clicked.connect(self.add_whitelist_item)

        input_layout.addWidget(self.whitelist_input)
        input_layout.addWidget(btn_add)
        layout.addLayout(input_layout)

        # Search input row
        self.whitelist_search = QLineEdit()
        self.whitelist_search.setPlaceholderText("🔍 Filtrar aplicaciones protegidas...")
        self.whitelist_search.setStyleSheet(
            "background-color: #0d1117; border: 1px solid #21262d; border-radius: 8px; padding: 6px; color: #bc8cff;"
        )
        self.whitelist_search.textChanged.connect(self.refresh_whitelist_ui)
        layout.addWidget(self.whitelist_search)

        # Whitelist ListWidget
        self.whitelist_list = QListWidget()
        self.whitelist_list.setStyleSheet(
            "background-color: #0d1117; border: 1px solid #21262d; border-radius: 12px; color: #c9d1d9; padding: 8px;"
        )
        self.refresh_whitelist_ui()
        layout.addWidget(self.whitelist_list)

        btn_remove = QPushButton("Eliminar Seleccionado")
        btn_remove.setObjectName("profileButton")
        btn_remove.clicked.connect(self.remove_whitelist_item)
        layout.addWidget(btn_remove)

        self.stacked_pages.addWidget(page)

    def _init_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("⚙️ CONFIGURACIÓN DEL SISTEMA")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ff003c;")
        layout.addWidget(title)

        # Autostart Checkbox
        self.chk_autostart = QCheckBox("Iniciar J4ck Cleaner automáticamente al encender el sistema")
        self.chk_autostart.setChecked(settings_mgr.settings.get("autostart_enabled", True))
        self.chk_autostart.setStyleSheet("font-size: 13px; color: #c9d1d9;")
        self.chk_autostart.toggled.connect(self.on_autostart_toggled)
        layout.addWidget(self.chk_autostart)

        # CPU Governor Selector
        gov_layout = QHBoxLayout()
        gov_label = QLabel("Gobernador de CPU (Frecuencia Kernel):")
        gov_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #c9d1d9;")
        
        self.combo_gov = QComboBox()
        self.combo_gov.addItems(["schedutil", "performance", "powersave", "ondemand"])
        self.combo_gov.setStyleSheet(
            "background-color: #0d1117; border: 1px solid #21262d; border-radius: 8px; padding: 6px; color: #ffffff;"
        )
        curr_gov = self.optimizer.get_current_governor()
        idx = self.combo_gov.findText(curr_gov)
        if idx >= 0:
            self.combo_gov.setCurrentIndex(idx)
        self.combo_gov.currentTextChanged.connect(self.on_governor_changed)

        gov_layout.addWidget(gov_label)
        gov_layout.addWidget(self.combo_gov)
        gov_layout.addStretch()
        layout.addLayout(gov_layout)
        layout.addWidget(self._make_separator())

        # Sampling Frequency Slider
        sample_layout = QVBoxLayout()
        curr_ms = settings_mgr.settings.get("sample_interval_ms", 1000)
        self.lbl_sample_freq = QLabel(f"Frecuencia de Muestreo de Sensores: {curr_ms} ms")
        self.lbl_sample_freq.setStyleSheet("font-size: 12px; font-weight: 600; color: #c9d1d9;")
        
        self.slider_sample_freq = QSlider(Qt.Horizontal)
        self.slider_sample_freq.setRange(500, 3000)
        self.slider_sample_freq.setSingleStep(250)
        self.slider_sample_freq.setValue(curr_ms)
        self.slider_sample_freq.valueChanged.connect(self.on_sample_slider_changed)

        sample_layout.addWidget(self.lbl_sample_freq)
        sample_layout.addWidget(self.slider_sample_freq)
        layout.addLayout(sample_layout)
        layout.addWidget(self._make_separator())

        # Hardware Specs Summary Card
        import platform
        import psutil
        specs_frame = QFrame()
        specs_frame.setObjectName("cardFrame")
        specs_layout = QVBoxLayout(specs_frame)
        specs_layout.setContentsMargins(16, 16, 16, 16)
        specs_layout.setSpacing(6)

        specs_title = QLabel("💻 ESPECIFICACIONES DEL SISTEMA")
        specs_title.setObjectName("cardTitle")
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        lbl_cpu_info = QLabel(f"<b>CPU:</b> {psutil.cpu_count(logical=False)} Cores físicos / {psutil.cpu_count(logical=True)} Lógicos ({platform.machine()})")
        lbl_ram_info = QLabel(f"<b>Memoria:</b> {mem.total / (1024**3):.1f} GB RAM | {swap.total / (1024**3):.1f} GB Swap")
        lbl_os_info = QLabel(f"<b>Kernel / OS:</b> Linux {platform.release()} | Python {platform.python_version()}")

        for lbl in [lbl_cpu_info, lbl_ram_info, lbl_os_info]:
            lbl.setStyleSheet("font-size: 12px; color: #c9d1d9;")

        specs_layout.addWidget(specs_title)
        specs_layout.addWidget(lbl_cpu_info)
        specs_layout.addWidget(lbl_ram_info)
        specs_layout.addWidget(lbl_os_info)
        layout.addWidget(specs_frame)
        layout.addWidget(self._make_separator())

        # Report Generator & Reset Buttons Row
        btns_row = QHBoxLayout()
        
        btn_report = QPushButton("📊 Generar Reporte (JSON)")
        btn_report.setObjectName("profileButton")
        btn_report.clicked.connect(self.on_generate_report_clicked)

        btn_reset = QPushButton("🔄 Restablecer Ajustes por Defecto")
        btn_reset.setObjectName("profileButton")
        btn_reset.clicked.connect(self.on_reset_defaults_clicked)

        btns_row.addWidget(btn_report)
        btns_row.addWidget(btn_reset)
        layout.addLayout(btns_row)

        # CLI Shortcuts Box
        cli_frame = QFrame()
        cli_frame.setObjectName("cardFrame")
        cli_layout = QVBoxLayout(cli_frame)
        cli_layout.setContentsMargins(16, 16, 16, 16)
        cli_layout.setSpacing(6)

        cli_title = QLabel("⌨️ COMANDOS Y ATAJOS CLI DISPONIBLES")
        cli_title.setObjectName("cardTitle")
        
        lbl_cli_clean = QLabel("<code>j4ck-cleaner --clean</code> : Ejecuta Turbo Clean instantáneo sin GUI")
        lbl_cli_report = QLabel("<code>j4ck-cleaner --report</code> : Genera reporte JSON de hardware")
        lbl_cli_test = QLabel("<code>j4ck-cleaner --test</code> : Ejecuta auto-diagnóstico de integridad")
        lbl_cli_prof = QLabel("<code>j4ck-cleaner --profile gaming</code> : Inicia en modo gaming")

        for lbl in [lbl_cli_clean, lbl_cli_report, lbl_cli_test, lbl_cli_prof]:
            lbl.setStyleSheet("font-size: 11px; color: #8b949e;")

        cli_layout.addWidget(cli_title)
        cli_layout.addWidget(lbl_cli_clean)
        cli_layout.addWidget(lbl_cli_report)
        cli_layout.addWidget(lbl_cli_test)
        cli_layout.addWidget(lbl_cli_prof)
        layout.addWidget(cli_frame)

        layout.addStretch()
        self.stacked_pages.addWidget(page)

    def refresh_whitelist_ui(self):
        """Refresh protection whitelist list widget items with live filtering."""
        self.whitelist_list.clear()
        query = getattr(self, "whitelist_search", None)
        filter_text = query.text().strip().lower() if query else ""
        
        for app_name in settings_mgr.get_whitelist():
            if not filter_text or filter_text in app_name.lower():
                self.whitelist_list.addItem(QListWidgetItem(f"🛡️  {app_name}"))

    def add_whitelist_item(self):
        """Add app to whitelist."""
        text = self.whitelist_input.text().strip()
        if text:
            settings_mgr.add_to_whitelist(text)
            self.whitelist_input.clear()
            self.refresh_whitelist_ui()

    def remove_whitelist_item(self):
        """Remove selected app from whitelist."""
        curr = self.whitelist_list.currentItem()
        if curr:
            clean_name = curr.text().replace("🛡️", "").strip()
            settings_mgr.remove_from_whitelist(clean_name)
            self.refresh_whitelist_ui()

    def on_autostart_toggled(self, checked: bool):
        """Toggle system autostart."""
        settings_mgr.configure_autostart(checked)
        self.log_label.setText(f"Autostart {'activado' if checked else 'desactivado'}.")

    def on_governor_changed(self, governor_name: str):
        """Change CPU scaling governor via optimizer engine."""
        success = self.optimizer.set_cpu_governor(governor_name)
        if success:
            self.log_label.setText(f"Gobernador de CPU cambiado a: {governor_name}")
        else:
            self.log_label.setText(f"No se pudo cambiar el gobernador a {governor_name} (requiere Polkit/sudo).")

    def on_sample_slider_changed(self, val: int):
        """Update sampling frequency interval in ms."""
        settings_mgr.settings["sample_interval_ms"] = val
        settings_mgr.save_settings()
        self.sensor_thread.sample_interval_ms = val
        self.lbl_sample_freq.setText(f"Frecuencia de Muestreo de Sensores: {val} ms")
        self.log_label.setText(f"Intervalo de muestreo ajustado a {val} ms.")

    def on_generate_report_clicked(self):
        """Generate 1-click system diagnostics JSON report."""
        rpt_path = self.optimizer.generate_diagnostics_report()
        if rpt_path:
            self.report_status_label.setText(f"Reporte listo en: {rpt_path}")

    def on_reset_defaults_clicked(self):
        """Reset settings and whitelist back to factory default values."""
        settings_mgr.reset_to_defaults()
        self.refresh_whitelist_ui()
        self.chk_autostart.setChecked(True)
        self.report_status_label.setText("Configuración restablecida a valores por defecto.")

    def _setup_tray_icon(self):
        """Setup System Tray Icon and Context Menu for background monitoring."""
        icon_path = "/home/j4ck/Dev/nocturne-guardian/assets/icons/nocturne-guardian.svg"
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            self.tray_icon = QSystemTrayIcon(self)

        self.tray_menu = QMenu(self)
        
        action_show = QAction("🛡️ Mostrar J4ck Cleaner", self)
        action_show.triggered.connect(self.show_window)
        
        action_clean = QAction("🧹 Limpiar Sistema", self)
        action_clean.triggered.connect(self.on_clean_clicked)

        menu_profile_dev = QAction("💻 Modo Developer", self)
        menu_profile_dev.triggered.connect(lambda: self.switch_profile("dev"))

        menu_profile_gaming = QAction("🎮 Modo Gaming", self)
        menu_profile_gaming.triggered.connect(lambda: self.switch_profile("gaming"))

        menu_profile_eco = QAction("🍃 Modo Eco", self)
        menu_profile_eco.triggered.connect(lambda: self.switch_profile("eco"))

        action_quit = QAction("❌ Salir", self)
        action_quit.triggered.connect(self.force_quit)

        self.tray_menu.addAction(action_show)
        self.tray_menu.addAction(action_clean)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(menu_profile_dev)
        self.tray_menu.addAction(menu_profile_gaming)
        self.tray_menu.addAction(menu_profile_eco)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(action_quit)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setToolTip("J4ck Cleaner v1.2.5 - Monitoreo Activo")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def show_window(self):
        """Show and restore main window."""
        self.show()
        self.raise_()
        self.activateWindow()

    def on_tray_icon_activated(self, reason):
        """Toggle window visibility on double click or click."""
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()

    @Slot(dict)
    def on_metrics_updated(self, metrics: dict):
        """Callback when background Thread sends updated hardware sample."""
        temp = metrics["cpu_temp"]
        gpu_temp = metrics.get("gpu_temp", temp)
        gpu_power = metrics.get("gpu_power_w", 0.0)
        vram_used = metrics.get("vram_used_gb", 0.0)
        
        usage = metrics["cpu_usage"]
        cpu_cores = metrics.get("cpu_cores", [])
        ram_used = metrics["ram_used_gb"]
        ram_total = metrics["ram_total_gb"]
        ram_pct = metrics["ram_percent"]
        freq_mhz = metrics["cpu_freq_mhz"]

        # Update sidebar RAM usage bar
        self.side_health_pbar.setValue(int(ram_pct))

        # Update Metric Cards
        self.card_temp.update_metric(temp, max_val=100.0, subtext=f"Frecuencia: {freq_mhz:.0f} MHz")
        self.card_gpu.update_metric(gpu_temp, max_val=100.0, subtext=f"VRAM: {vram_used:.1f}GB | Pwr: {gpu_power:.0f}W")
        self.card_cpu.update_metric(usage, max_val=100.0, subtext=f"Cálculo en 4 Núcleos APU")
        self.card_ram.update_metric(ram_used, max_val=ram_total, subtext=f"{ram_pct:.1f}% de {ram_total:.1f} GB Total")

        swap_used = metrics.get("swap_used_gb", 0.0)
        swap_total = metrics.get("swap_total_gb", 1.0) or 1.0
        swap_pct = metrics.get("swap_percent", 0.0)
        self.card_swap.update_metric(swap_used, max_val=swap_total, subtext=f"{swap_pct:.1f}% de {swap_total:.1f} GB")

        # Update Realtime Graph & Core Matrix
        self.plot_widget.add_point(temp)
        if cpu_cores:
            self.cpu_matrix.update_cores(cpu_cores, freq_mhz)

        # Update sidebar status badge
        guard_result = self.optimizer.enforce_thermal_throttling(temp)
        if guard_result["triggered"]:
            self.status_badge_side.setText("ALERTA TÉRMICA")
            self.status_badge_side.setStyleSheet(
                "background-color: #ff003c20; color: #ff003c; font-weight: 700; "
                "border: 1px solid #ff003c; border-radius: 8px; padding: 6px 12px; font-size: 11px;"
            )
        else:
            self.status_badge_side.setText("ACTIVO")
            self.status_badge_side.setStyleSheet(
                "background-color: #00d4ff15; color: #00d4ff; font-weight: 700; "
                "border: 1px solid #00d4ff44; border-radius: 8px; padding: 6px 12px; font-size: 11px;"
            )
        import time
        now = time.time()
        if ram_pct >= 90.0 and (now - self.last_auto_clean_time) > 60.0:
            self.last_auto_clean_time = now
            self.on_clean_clicked()
            self.log_label.setText(f"RAM al {ram_pct:.1f}%: limpieza de caché automática ejecutada.")

        # Update Top Processes Table
        procs = metrics.get("top_processes", [])
        self.table_procs.setRowCount(len(procs))
        for row, p in enumerate(procs):
            self.table_procs.setItem(row, 0, QTableWidgetItem(str(p['pid'])))
            self.table_procs.setItem(row, 1, QTableWidgetItem(p['name']))
            self.table_procs.setItem(row, 2, QTableWidgetItem(f"{p['cpu']:.1f}%"))
            self.table_procs.setItem(row, 3, QTableWidgetItem(f"{p['mem_mb']:.1f} MB"))

        # Update Session Uptime and Footer Stats
        import time
        elapsed_sec = int(time.time() - self.session_start_time)
        hours = elapsed_sec // 3600
        mins = (elapsed_sec % 3600) // 60
        bat_info = metrics.get("battery", {})
        bat_str = bat_info.get("status_str", "🔌 CA")
        self.footer_stats_label.setText(
            f"⏱️ Uptime: {hours:02d}h {mins:02d}m | {bat_str} | ⚡ RAM Liberada: {self.total_ram_freed_mb:.1f} MB"
        )

    def switch_profile(self, name: str):
        """Switch active profile (dev, gaming, eco)."""
        if name in PROFILES:
            self.active_profile = PROFILES[name]
        
        self.btn_dev.setChecked(name == "dev")
        self.btn_gaming.setChecked(name == "gaming")
        self.btn_eco.setChecked(name == "eco")

        self.optimizer.set_thermal_threshold(self.active_profile.thermal_threshold_c)
        self.thermal_slider.setValue(int(self.active_profile.thermal_threshold_c))
        self.slider_label.setText(f"Umbral Térmico Preventivo: {self.active_profile.thermal_threshold_c:.0f}°C")
        self.desc_label.setText(self.active_profile.description)
        
        self.log_label.setText(f"Perfil cambiado a: {self.active_profile.display_name}")

    def on_slider_changed(self, val: int):
        """Handle manual thermal slider adjustment."""
        self.active_profile.thermal_threshold_c = float(val)
        self.optimizer.set_thermal_threshold(float(val))
        self.slider_label.setText(f"Umbral Térmico Preventivo: {val}°C")
        self.log_label.setText(f"Umbral de temperatura ajustado a {val}°C.")

    def on_clean_clicked(self):
        """Trigger non-destructive cache flush via drop_caches."""
        res = self.optimizer.clean_cache()
        freed = res.get("freed_mb", 0.0)
        self.total_ram_freed_mb += freed
        self.log_label.setText(res["message"])
        logger.log(f"Limpieza de caché ejecutada: {freed:.1f} MB liberados.")

    def closeEvent(self, event):
        """Minimize to tray instead of exiting if tray icon is active."""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.force_quit()

    def force_quit(self):
        """Clean shutdown of worker threads and quit app."""
        self.sensor_thread.stop()
        self.sensor_thread.wait(1000)
        self.tray_icon.hide()
        self.destroy()
        os._exit(0)
