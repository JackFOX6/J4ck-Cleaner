"""
Dark Nocturne / Matte Charcoal Slate design system QSS (J4ckENI Framework).
Inspired by modern dark UI kit aesthetics: Charcoal #121418, Cards #1c2027, Crimson Accent #ff003c.
"""

# ─── Design Token Constants ───────────────────────────────────────────────────
# Exportable for use in QPainter, QColor, and widget-level styling
BG_BASE        = "#121418"   # Main window background (OLED charcoal)
CARD_BG        = "#1c2027"   # Card / panel fill
CARD_BORDER    = "#2a2f3a"   # Card border (subtle separator)
ELEVATED_BG    = "#232832"   # Elevated surfaces (buttons, inputs)
HOVER_BG       = "#2b313d"   # Hover state fill
ACCENT_CRIMSON = "#ff003c"   # Primary crimson accent
ACCENT_VIOLET  = "#bc8cff"   # Secondary violet accent
ACCENT_CYAN    = "#00d4ff"   # Tertiary cyan / health-good state
TEXT_PRIMARY   = "#f0f4f8"   # Main body text
TEXT_SECONDARY = "#9097a6"   # Dimmed / subtext
TEXT_HIGHLIGHT = "#ffffff"   # Full-white highlight

DARK_NOCTURNE_QSS = """
QMainWindow, QDialog {
    background-color: #121418;
    color: #f0f4f8;
}

QWidget {
    font-family: "Inter", "Segoe UI", "Roboto", "DejaVu Sans", sans-serif;
    color: #f0f4f8;
    background-color: #121418;
}

QScrollArea, QAbstractScrollArea {
    background-color: #121418;
    border: none;
}

QScrollBar:vertical {
    background: #1c2027;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2a2f3a;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#cardFrame {
    background-color: #1c2027;
    border: 1px solid #2a2f3a;
    border-radius: 16px;
}

QFrame#cardFrame:hover {
    border: 1px solid #3a4150;
}

QLabel#cardTitle {
    font-size: 13px;
    font-weight: 600;
    color: #9097a6;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#cardValue {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#cardSubtext {
    font-size: 11px;
    color: #9097a6;
}

QPushButton#actionButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff003c, stop:1 #9e0026);
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    border: 1px solid #ff2a5e55;
    border-radius: 12px;
    padding: 12px 24px;
}

QPushButton#actionButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff2a5e, stop:1 #b8002e);
    border: 1px solid #ff003c;
}

QPushButton#actionButton:pressed {
    background: #8a0020;
}

QPushButton#profileButton {
    background-color: #232832;
    color: #cdd5e0;
    border: 1px solid #323846;
    border-radius: 12px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton#profileButton:hover {
    background-color: #2b313d;
    border: 1px solid #ff003c77;
    color: #ffffff;
}

QPushButton#profileButton:checked {
    background-color: #343b4a;
    color: #ff003c;
    border: 2px solid #ff003c;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #232832;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #bc8cff, stop:1 #ff003c);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #ff003c;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QProgressBar {
    border: 1px solid #2a2f3a;
    border-radius: 10px;
    text-align: center;
    background-color: #121418;
    color: #ffffff;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d4ff, stop:1 #ff003c);
    border-radius: 9px;
}

QTableWidget {
    background-color: #1c2027;
    border: 1px solid #2a2f3a;
    border-radius: 16px;
    gridline-color: #232832;
    color: #cdd5e0;
}

QHeaderView::section {
    background-color: #232832;
    color: #9097a6;
    font-weight: 600;
    padding: 6px;
    border: none;
}

QListWidget {
    background-color: #1c2027;
    border: 1px solid #2a2f3a;
    border-radius: 16px;
    color: #cdd5e0;
}

QLineEdit {
    background-color: #121418;
    border: 1px solid #2a2f3a;
    border-radius: 10px;
    padding: 8px;
    color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #ff003c;
}

QComboBox {
    background-color: #1c2027;
    border: 1px solid #2a2f3a;
    border-radius: 10px;
    padding: 6px 12px;
    color: #ffffff;
}

QComboBox:hover {
    border: 1px solid #ff003c77;
}

QComboBox QAbstractItemView {
    background-color: #1c2027;
    border: 1px solid #2a2f3a;
    selection-background-color: #343b4a;
    selection-color: #ff003c;
}

QCheckBox {
    color: #cdd5e0;
    spacing: 8px;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2a2f3a;
    border-radius: 4px;
    background-color: #121418;
}

QCheckBox::indicator:checked {
    background-color: #ff003c;
    border: 1px solid #ff003c;
}

QCheckBox::indicator:hover {
    border: 1px solid #ff003c77;
}

QLabel#statusLabel {
    font-size: 11px;
    color: #bc8cff;
    padding: 2px 0px;
}
"""
