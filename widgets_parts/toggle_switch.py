"""toggle_switch.py — auto-generated from widgets.py."""

import os
import base64
from PyQt6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QRadioButton, QComboBox, QScrollArea, QFileDialog, QMenu, QInputDialog, QStyle, QStyleOptionButton, QGridLayout, QWidget, QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QFrame, QFormLayout, QStackedWidget
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation, pyqtSignal
from PyQt6.QtGui import QPainter, QCursor, QColor
from templates import FEED_COLORS, REACTIONS_MAP
from config import BASE_CONFIG as default_config

from ._header import QColor, QEasingCurve, QPainter, QVariantAnimation, QWidget, Qt, pyqtSignal

class ModernToggleSwitch(QWidget):
    """Modern animated toggle switch widget with improved design"""
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None, size="medium"):
        super().__init__(parent)
        self.is_on = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.size_mode = size
        
        # Size modes
        sizes = {
            "small": (48, 26),
            "medium": (55, 30),
            "large": (64, 36)
        }
        self.width, self.height = sizes.get(size, sizes["medium"])
        self.setFixedSize(self.width, self.height)
        
        # Animation
        self._anim = QVariantAnimation()
        self._anim.setDuration(250)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._anim.valueChanged.connect(self._on_animation)
        self._progress = 0.0
        
        # Hover state
        self._hovered = False
    
    def set_state(self, state):
        """Set the toggle state without animation"""
        self.is_on = state
        self._progress = 1.0 if state else 0.0
        self.update()
    
    def toggle(self):
        """Toggle the state with animation"""
        self.is_on = not self.is_on
        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(1.0 if self.is_on else 0.0)
        self._anim.start()
    
    def _on_animation(self, value):
        """Update animation progress"""
        self._progress = value
        self.update()
    
    def mousePressEvent(self, event):
        """Handle click to toggle"""
        self.toggle()
        self.toggled.emit(self.is_on)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect"""
        self._hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._hovered = False
        self.update()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """Paint the toggle switch with modern premium design.
        Colors are read from the active theme (theme.py) so the toggle
        automatically picks up the global color scheme."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Dimensions
        radius = self.height // 2
        circle_size = self.height - 4

        # ── Read colors from the active theme ──
        # Default to hardcoded values if the theme module is unavailable.
        accent = QColor(34, 197, 94)       # default green
        accent_hover = QColor(52, 211, 153)
        accent_pressed = QColor(22, 163, 74)
        border_hover = QColor(75, 85, 99)
        try:
            from theme import get_theme
            t = get_theme()
            accent = QColor(t["accent"])
            accent_hover = QColor(t["accent_hover"])
            accent_pressed = QColor(t["accent_pressed"])
            border_hover = QColor(t["border_hover"])
        except Exception:
            pass

        # Determine colors based on state
        if self.is_on:
            bg_color = accent
            border_color = accent_pressed
            circle_color = QColor(255, 255, 255)  # White
            shadow_color = accent
        else:
            bg_color = border_hover
            border_color = QColor(75, 85, 99)
            circle_color = QColor(255, 255, 255)  # White
            shadow_color = border_hover

        # Hover effect - slightly brighter
        if self._hovered:
            if self.is_on:
                bg_color = accent_hover
            else:
                bg_color = QColor(156, 163, 175)  # Lighter gray on hover

        # Draw shadow/depth effect
        shadow = QColor(0, 0, 0, 20)
        painter.fillRect(1, 2, self.width - 2, self.height - 2, shadow)

        # Draw background (rounded rectangle)
        painter.fillRect(0, 0, self.width, self.height, bg_color)
        painter.drawRoundedRect(0, 0, self.width - 1, self.height - 1, radius, radius)

        # Draw border for clarity
        pen = painter.pen()
        pen.setColor(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(0, 0, self.width - 1, self.height - 1, radius, radius)

        # Calculate circle position with smooth animation
        circle_x = 2 + self._progress * (self.width - circle_size - 4)
        circle_y = 2

        # Draw circle with white color and shadow
        painter.setPen(Qt.PenStyle.NoPen)

        # Shadow under circle
        circle_shadow = QColor(0, 0, 0, 30)
        painter.setBrush(circle_shadow)
        painter.drawEllipse(int(circle_x) + 1, int(circle_y) + 1, int(circle_size), int(circle_size))

        # Main circle
        painter.setBrush(circle_color)
        painter.drawEllipse(int(circle_x), int(circle_y), int(circle_size), int(circle_size))

        # Add center dot for clarity
        dot_color = shadow_color if self.is_on else QColor(107, 114, 128)
        painter.setBrush(dot_color)
        dot_size = 4
        center_x = int(circle_x + circle_size / 2)
        center_y = int(circle_y + circle_size / 2)
        painter.drawEllipse(center_x - dot_size // 2, center_y - dot_size // 2, dot_size, dot_size)
