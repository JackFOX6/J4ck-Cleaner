import collections
from typing import List
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout, QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from j4ck_cleaner.ui.theme import (
    CARD_BG, CARD_BORDER, ACCENT_CRIMSON, ACCENT_CYAN, TEXT_PRIMARY, TEXT_SECONDARY
)


class SystemHealthGaugeWidget(QWidget):
    """
    Custom QPainter Radial Progress Gauge showing 0-100% System Health Index.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(140, 140)
        self.health_score = 100
        self.status_text = "ÓPTIMO"

    def set_health(self, score: int, status_text: str = ""):
        """Update health score (0-100) and trigger repaint."""
        self.health_score = max(0, min(100, score))
        self.status_text = status_text or ("ÓPTIMO" if score >= 75 else "MEDIO" if score >= 50 else "ALERTA")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)
        
        rect = QRectF((width - side) / 2 + 10, (height - side) / 2 + 10, side - 20, side - 20)

        # Background Arc
        pen_bg = QPen(QColor(CARD_BORDER), 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 225 * 16, -270 * 16)

        # Dynamic Color selection
        if self.health_score >= 75:
            arc_color = QColor(ACCENT_CYAN)
        elif self.health_score >= 50:
            arc_color = QColor("#ffaa00")
        else:
            arc_color = QColor(ACCENT_CRIMSON)

        # Foreground Health Arc
        pen_fg = QPen(arc_color, 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_fg)
        span_angle = int(-270 * (self.health_score / 100.0) * 16)
        painter.drawArc(rect, 225 * 16, span_angle)

        # Text Value
        painter.setPen(QColor(TEXT_PRIMARY))
        font_score = QFont("Inter", 18, QFont.Bold)
        painter.setFont(font_score)
        painter.drawText(rect, Qt.AlignCenter, f"{self.health_score}%")

        # Subtext Label
        painter.setPen(QColor(TEXT_SECONDARY))
        font_sub = QFont("Inter", 9, QFont.Normal)
        painter.setFont(font_sub)
        sub_rect = QRectF(rect.x(), rect.y() + 28, rect.width(), rect.height())
        painter.drawText(sub_rect, Qt.AlignCenter, self.status_text)


class MetricCard(QFrame):
    """
    Custom card widget for displaying system telemetry (Temp, Usage, RAM).
    """

    def __init__(self, title: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.unit = unit

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        # Header Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")

        # Main Value
        self.value_label = QLabel(f"-- {unit}")
        self.value_label.setObjectName("cardValue")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Subtext / Status
        self.subtext_label = QLabel("Muestreando...")
        self.subtext_label.setObjectName("cardSubtext")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.subtext_label)

    def update_metric(self, value: float, max_val: float = 100.0, subtext: str = ""):
        """Update card value, progress bar, and status subtext."""
        val_str = f"{value:.1f} {self.unit}".strip()
        self.value_label.setText(val_str)
        
        pct = int(min(100.0, max(0.0, (value / max_val) * 100.0)))
        self.progress_bar.setValue(pct)

        if subtext:
            self.subtext_label.setText(subtext)


class CpuCoreMatrixWidget(QFrame):
    """
    Visual per-core matrix widget showing individual bars and frequencies for each CPU core.
    """

    def __init__(self, num_cores: int = 4, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.num_cores = num_cores
        self.core_bars: List[QProgressBar] = []
        self.core_labels: List[QLabel] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel("MATRIZ DE NÚCLEOS CPU")
        header.setObjectName("cardTitle")
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(12)

        for i in range(num_cores):
            lbl = QLabel(f"Core {i}: -- %")
            lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #c9d1d9;")
            
            pbar = QProgressBar()
            pbar.setRange(0, 100)
            pbar.setValue(0)
            
            grid.addWidget(lbl, i, 0)
            grid.addWidget(pbar, i, 1)

            self.core_labels.append(lbl)
            self.core_bars.append(pbar)

        layout.addLayout(grid)

    def update_cores(self, core_percents: List[float], freq_mhz: float = 0.0):
        """Update individual core percentage bars and labels."""
        for i, pct in enumerate(core_percents):
            if i < len(self.core_bars):
                self.core_bars[i].setValue(int(pct))
                self.core_labels[i].setText(f"Núcleo {i}: {pct:.1f}%")


class RealtimePlotWidget(FigureCanvas):
    """
    High-performance real-time telemetry graph using Matplotlib QTAgg.
    """

    def __init__(self, title: str = "Historial Térmico (°C)", max_points: int = 40, parent=None):
        self.fig = Figure(figsize=(5, 2.5), facecolor='#1c2027')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1c2027')

        super().__init__(self.fig)
        self.setParent(parent)
        
        self.max_points = max_points
        self.data_history = collections.deque([0.0] * max_points, maxlen=max_points)
        self.title = title
        
        # Configure dark aesthetic
        self.ax.spines['bottom'].set_color('#2a2f3a')
        self.ax.spines['top'].set_color('#2a2f3a')
        self.ax.spines['right'].set_color('#2a2f3a')
        self.ax.spines['left'].set_color('#2a2f3a')
        self.ax.tick_params(colors='#9097a6', labelsize=8)
        self.ax.grid(True, color='#232832', linestyle='--', alpha=0.6)

    def add_point(self, value: float):
        """Add new data point to plot and redraw efficiently."""
        self.data_history.append(value)
        self.ax.clear()
        
        self.ax.set_facecolor('#1c2027')
        self.ax.grid(True, color='#232832', linestyle='--', alpha=0.6)
        self.ax.spines['bottom'].set_color('#2a2f3a')
        self.ax.spines['top'].set_color('#2a2f3a')
        self.ax.spines['right'].set_color('#2a2f3a')
        self.ax.spines['left'].set_color('#2a2f3a')
        self.ax.tick_params(colors='#9097a6', labelsize=8)

        # Line and fill
        x_data = range(len(self.data_history))
        self.ax.plot(x_data, self.data_history, color='#ff003c', linewidth=2)
        self.ax.fill_between(x_data, self.data_history, color='#ff003c', alpha=0.15)
        
        self.ax.set_ylim(min(30, min(self.data_history)), max(85, max(self.data_history) + 5))
        self.draw_idle()
