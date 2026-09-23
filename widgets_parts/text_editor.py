"""text_editor.py — auto-generated from widgets.py."""

import os
import base64
from PyQt6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QRadioButton, QComboBox, QScrollArea, QFileDialog, QMenu, QInputDialog, QStyle, QStyleOptionButton, QGridLayout, QWidget, QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QFrame, QFormLayout, QStackedWidget
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation, pyqtSignal
from PyQt6.QtGui import QPainter, QCursor, QColor
from templates import FEED_COLORS, REACTIONS_MAP
from config import BASE_CONFIG as default_config

from ._header import QDialog, QHBoxLayout, QPushButton, QVBoxLayout

class TextEditorDialog(QDialog):
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Éditeur de texte")
        self.setMinimumSize(500, 400)
        self._apply_theme_style()

        from PyQt6.QtWidgets import QTextEdit
        lay = QVBoxLayout(self)
        self.editor = QTextEdit()
        self.editor.setPlainText(initial_text)
        self.editor.setAcceptRichText(False)
        lay.addWidget(self.editor)

        btn_lay = QHBoxLayout()
        btn_ok = QPushButton("✓ Enregistrer")
        from theme import btn_style_success as _bss
        btn_ok.setStyleSheet(_bss())
        btn_ok.clicked.connect(self.accept)
        btn_lay.addStretch()
        btn_lay.addWidget(btn_ok)
        lay.addLayout(btn_lay)

    def _apply_theme_style(self):
        """Build and apply the dialog stylesheet using the current theme colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
                QTextEdit {{ background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; border-radius: 6px; padding: 10px; font-size: 14px; font-family: monospace; color: {t['text']}; }}
                QPushButton {{ background-color: {t['success']}; color: white; border: none; border-radius: 6px; font-weight: normal; padding: 10px 20px; }}
                QPushButton:hover {{ background-color: #16a34a; }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("TextEditorDialog._apply_theme_style", e)
            except Exception:
                pass

    def get_text(self):
        return self.editor.toPlainText()
