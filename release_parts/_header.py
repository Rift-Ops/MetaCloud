"""_header.py — auto-generated from Release.py."""

import sys
import os
import time
import threading
import subprocess
import socket
import requests
from werkzeug.serving import make_server
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QTextEdit, QGroupBox, QSplitter, QRadioButton, QCheckBox, QFrame,
                             QScrollArea, QDialog, QGridLayout, QTabWidget, QFileDialog, QComboBox,
                             QMenu, QInputDialog, QStyle, QStyleOptionButton, QMessageBox,
                             QListWidget, QListWidgetItem, QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, QAbstractAnimation
from PyQt6.QtGui import QTextCursor, QFont, QColor, QCursor, QPainter
import json
import base64

from routes import app
from config import (active_servers, sandbox_config, get_cfg, TARGETS_DIR, BASE_CONFIG,
                    TRASH_DIR, is_target_hidden, set_target_hidden,
                    rename_target_meta, remove_target_meta)
import config as _config
from widgets import BounceButton, TextEditorDialog, PublicationDialog, ModernToggleSwitch
from helpers import is_port_in_use, ajouter_log, BANNER_ASCII, log_error

# ═══════════════ Centralized Error Logging ═══════════════
def log_error_to_file(function_name, error, error_type="ERROR"):
    """Log an error to the canonical error log file (errors_logs.txt) AND, when
    debug mode is ON, forward it to all victim log panels + the sandbox log
    panel so the operator sees errors in real time.

    This is a thin wrapper around helpers.log_error() — the two functions used
    to write to two different files (logs_error.txt vs errors_logs.txt), which
    split error traces across files and caused duplicate entries when callers
    invoked both. Now everything goes through helpers.log_error(), so:
      • ONE canonical file: errors_logs.txt (with full traceback)
      • ONE debug-mode forward to victim logs + sandbox
      • Callers can keep using either entry point interchangeably.

    Parameters
    ----------
    function_name : str
        Human-readable context (function / module name).
    error : Exception | str
        The exception object or a description of the error.
    error_type : str
        Optional severity tag. When non-default ("ERROR"), it is prepended to
        the context so log readers can still filter by severity.
    """
    try:
        from helpers import log_error as _hle
        # Preserve the error_type tag in the context line when it's meaningful
        # (i.e. not the default "ERROR").
        if error_type and error_type != "ERROR":
            ctx = f"[{error_type}] {function_name}"
        else:
            ctx = function_name
        _hle(ctx, error)
    except Exception as e:
        # Last-resort fallback: write to stderr so we at least see the failure.
        try:
            import sys as _sys
            _sys.stderr.write(f"[log_error_to_file] failed to delegate: {e}\n")
        except Exception:
            pass

# ═══════════════ Button State Manager ═══════════════
class ButtonStateManager:
    """Manages button states to prevent conflicts"""
    def __init__(self):
        self.locked_buttons = set()
        self.lock = threading.Lock()
    
    def lock_button(self, button_id):
        """Lock a button to prevent multiple clicks"""
        with self.lock:
            self.locked_buttons.add(button_id)
    
    def unlock_button(self, button_id):
        """Unlock a button"""
        with self.lock:
            self.locked_buttons.discard(button_id)
    
    def is_locked(self, button_id):
        """Check if a button is locked"""
        with self.lock:
            return button_id in self.locked_buttons

button_manager = ButtonStateManager()



class ReorderableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.parent_win = parent

    def dropEvent(self, event):
        super().dropEvent(event)
        if self.parent_win and hasattr(self.parent_win, "on_list_reordered"):
            self.parent_win.on_list_reordered()
