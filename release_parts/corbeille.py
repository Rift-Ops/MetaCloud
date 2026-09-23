"""corbeille.py — auto-generated from Release.py."""

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
from config import active_servers, sandbox_config, get_cfg, TARGETS_DIR, BASE_CONFIG, TRASH_DIR, is_target_hidden, set_target_hidden, rename_target_meta, remove_target_meta, mask_name, is_hide_names
from widgets import BounceButton, TextEditorDialog, PublicationDialog, ModernToggleSwitch
from helpers import is_port_in_use, ajouter_log, BANNER_ASCII, log_error

from ._header import BounceButton, QAbstractItemView, QEasingCurve, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPropertyAnimation, QVBoxLayout, QWidget, Qt, TARGETS_DIR, TRASH_DIR, json, log_error, log_error_to_file, os, remove_target_meta, rename_target_meta

class CorbeilleWindow(QWidget):
    """Window to manage soft-deleted targets: restore, delete permanently, or empty trash."""

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.setWindowTitle("🗑️ Corbeille")
        self.setMinimumSize(620, 520)
        self._apply_theme_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # ── Header ──
        header_lay = QHBoxLayout()
        title = QLabel("🗑️ Corbeille")
        from theme import get_theme as _gt
        _t = _gt()
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {_t['danger']};")
        header_lay.addWidget(title)
        header_lay.addStretch()
        self.lbl_count = QLabel("0 cible(s)")
        self.lbl_count.setStyleSheet(f"color: {_t['text_dim']}; font-weight: bold;")
        header_lay.addWidget(self.lbl_count)
        layout.addLayout(header_lay)

        info = QLabel("Sélectionnez une ou plusieurs cibles pour les restaurer ou les supprimer définitivement.")
        info.setStyleSheet(f"color: {_t['text_dim']}; font-style: italic;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # ── Action buttons ──
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)

        self.btn_select_all = BounceButton("☑ Tout sélectionner")
        from theme import btn_style_neutral as _bsn
        self.btn_select_all.setStyleSheet(_bsn())
        self.btn_select_all.clicked.connect(self.select_all)
        btn_lay.addWidget(self.btn_select_all)

        self.btn_deselect_all = BounceButton("☐ Tout désélectionner")
        from theme import btn_style_neutral as _bsn2
        self.btn_deselect_all.setStyleSheet(_bsn2())
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        btn_lay.addWidget(self.btn_deselect_all)

        # ── Hide/Show victim names toggle ──
        # Mirrors the dashboard toggle. When ON, victim names are masked in the trash list.
        self.btn_hide_names = BounceButton("🙈 Noms masqués" if is_hide_names() else "👁️ Noms visibles")
        self.btn_hide_names.clicked.connect(self._toggle_hide_names)
        self._update_hide_names_button_style()
        btn_lay.addWidget(self.btn_hide_names)

        btn_lay.addStretch()

        self.btn_restore = BounceButton("♻ Restaurer la sélection")
        from theme import btn_style_success as _bss
        self.btn_restore.setStyleSheet(_bss())
        self.btn_restore.clicked.connect(self.restore_selected)
        btn_lay.addWidget(self.btn_restore)

        self.btn_delete = BounceButton("❌ Supprimer définitivement")
        from theme import btn_style_danger as _bsd
        self.btn_delete.setStyleSheet(_bsd())
        self.btn_delete.clicked.connect(self.delete_selected)
        btn_lay.addWidget(self.btn_delete)

        self.btn_empty = BounceButton("🧹 Vider la corbeille")
        from theme import btn_style_danger as _bsd2
        self.btn_empty.setStyleSheet(_bsd2())
        self.btn_empty.clicked.connect(self.empty_corbeille)
        btn_lay.addWidget(self.btn_empty)

        layout.addLayout(btn_lay)

        # ── List of trashed targets ──
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        from theme import list_widget_style as _lws
        self.list_widget.setStyleSheet(_lws())
        layout.addWidget(self.list_widget, stretch=1)

        self.refresh_list()

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
                QScrollArea {{ border: 1px solid {t['border']}; border-radius: 8px; background: {t['bg']}; }}
                QListWidget {{
                    background-color: {t['bg']}; border: 1px solid {t['border']}; border-radius: 8px;
                    padding: 6px; color: {t['text']}; outline: none;
                }}
                QListWidget::item {{
                    background-color: {t['bg_alt']}; border: 1px solid {t['border']}; border-radius: 8px;
                    padding: 10px; margin-bottom: 6px;
                }}
                QListWidget::item:selected {{
                    background-color: {t['border']}; border: 1px solid {t['accent']};
                }}
                QListWidget::item:hover {{ background-color: {t['border_hover']}; }}
                QCheckBox {{ color: {t['text']}; spacing: 8px; }}
                QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 2px solid {t['border_hover']}; background: {t['bg_alt']}; }}
                QCheckBox::indicator:checked {{ background: {t['danger']}; border: 2px solid {t['danger']}; }}
            """)
            # Re-apply individual button stylesheets so they pick up the new theme
            from theme import btn_style_neutral, btn_style_success, btn_style_danger
            if hasattr(self, 'btn_select_all') and self.btn_select_all:
                self.btn_select_all.setStyleSheet(btn_style_neutral())
            if hasattr(self, 'btn_deselect_all') and self.btn_deselect_all:
                self.btn_deselect_all.setStyleSheet(btn_style_neutral())
            if hasattr(self, 'btn_restore') and self.btn_restore:
                self.btn_restore.setStyleSheet(btn_style_success())
            if hasattr(self, 'btn_delete') and self.btn_delete:
                self.btn_delete.setStyleSheet(btn_style_danger())
            if hasattr(self, 'btn_empty') and self.btn_empty:
                self.btn_empty.setStyleSheet(btn_style_danger())
            if hasattr(self, 'btn_hide_names') and self.btn_hide_names:
                self._update_hide_names_button_style()
            # Refresh list so row colors pick up the new theme
            try:
                self.refresh_list()
            except Exception:
                pass
        except Exception as e:
            log_error_to_file('CorbeilleWindow._apply_theme_style', e)

    # ── Helpers ──
    def _list_trashed(self):
        try:
            if not os.path.exists(TRASH_DIR):
                os.makedirs(TRASH_DIR, exist_ok=True)
                return []
            return sorted([f[:-5] for f in os.listdir(TRASH_DIR) if f.endswith(".json")])
        except Exception as e:
            log_error_to_file("CorbeilleWindow._list_trashed", e)
            return []

    def _get_victim_photo_for_trashed(self, tid):
        """Read victim_photo path from a trashed target JSON."""
        try:
            path = os.path.join(TRASH_DIR, f"{tid}.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f).get("victim_photo", "")
        except Exception as e:
            log_error_to_file("CorbeilleWindow._get_victim_photo_for_trashed", e)
            log_error("CorbeilleWindow._get_victim_photo_for_trashed", e)
        return ""

    def refresh_list(self):
        # Guard: list_widget may not exist yet during __init__ / theme refresh
        if not hasattr(self, 'list_widget') or self.list_widget is None:
            return
        try:
            self.list_widget.clear()
            tids = self._list_trashed()
            for tid in tids:
                item = QListWidgetItem(self.list_widget)
                item.setData(Qt.ItemDataRole.UserRole, tid)

                row = QWidget()
                row.setStyleSheet("QWidget { background: transparent; }")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(10, 6, 10, 6)
                rl.setSpacing(10)

                # Round avatar
                victim_photo = self._get_victim_photo_for_trashed(tid)
                if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                    avatar = self.main_win.config_win._make_round_avatar(victim_photo, size=36)
                else:
                    avatar = QLabel("👤")
                rl.addWidget(avatar)

                lbl = QLabel(f"🗑️  {mask_name(tid)}")
                from theme import get_theme as _gt_lbl
                _t_lbl = _gt_lbl()
                lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {_t_lbl['text']}; background: transparent;")
                rl.addWidget(lbl, stretch=1)

                item.setSizeHint(row.sizeHint())
                self.list_widget.setItemWidget(item, row)

            count = len(tids)
            self.lbl_count.setText(f"{count} cible(s) dans la corbeille")
            has_items = count > 0
            self.btn_restore.setEnabled(has_items)
            self.btn_delete.setEnabled(has_items)
            self.btn_empty.setEnabled(has_items)
            self.btn_select_all.setEnabled(has_items)
            self.btn_deselect_all.setEnabled(has_items)
        except Exception as e:
            log_error_to_file("CorbeilleWindow.refresh_list", e)
            log_error("CorbeilleWindow.refresh_list", e)

    def select_all(self):
        self.list_widget.blockSignals(True)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(True)
        self.list_widget.blockSignals(False)

    def deselect_all(self):
        self.list_widget.blockSignals(True)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(False)
        self.list_widget.blockSignals(False)

    def _toggle_hide_names(self):
        """Toggle the global hide_names flag and refresh this window."""
        try:
            from config import set_hide_names
            new_state = not is_hide_names()
            set_hide_names(new_state)
            self._update_hide_names_button_style()
            self.refresh_list()
            # Notify the main dashboard so its button stays in sync
            if hasattr(self, 'main_win') and self.main_win:
                if hasattr(self.main_win, '_update_hide_names_button_style'):
                    try:
                        self.main_win._update_hide_names_button_style()
                    except Exception as e:
                        log_error_to_file("CorbeilleWindow._toggle_hide_names.sync_btn", e)
                if hasattr(self.main_win, 'rebuild_target_list'):
                    try:
                        QTimer.singleShot(0, self.main_win.rebuild_target_list)
                    except Exception as e:
                        log_error_to_file("CorbeilleWindow._toggle_hide_names.rebuild", e)
                # Also notify credentials window if open
                if hasattr(self.main_win, 'credentials_win') and self.main_win.credentials_win:
                    try:
                        if hasattr(self.main_win.credentials_win, 'refresh_for_hide_names'):
                            self.main_win.credentials_win.refresh_for_hide_names()
                    except Exception as e:
                        log_error_to_file("CorbeilleWindow._toggle_hide_names.creds", e)
                # Also notify sandbox window if open
                if hasattr(self.main_win, 'sandbox_win') and self.main_win.sandbox_win:
                    try:
                        if hasattr(self.main_win.sandbox_win, 'refresh_for_hide_names'):
                            self.main_win.sandbox_win.refresh_for_hide_names()
                    except Exception as e:
                        log_error_to_file("CorbeilleWindow._toggle_hide_names.sandbox", e)
                # Also notify target config window if open
                if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                    try:
                        if hasattr(self.main_win.config_win, 'refresh_for_hide_names'):
                            self.main_win.config_win.refresh_for_hide_names()
                    except Exception as e:
                        log_error_to_file("CorbeilleWindow._toggle_hide_names.config", e)
        except Exception as e:
            log_error_to_file("CorbeilleWindow._toggle_hide_names", e)
            log_error("CorbeilleWindow._toggle_hide_names", e)

    def _update_hide_names_button_style(self):
        """Update the hide-names toggle button label + color based on current state."""
        try:
            if is_hide_names():
                self.btn_hide_names.setText("🙈 Noms masqués")
                self.btn_hide_names.setStyleSheet("""
                    QPushButton { background-color: #ef4444; color: white; border: none;
                                  border-radius: 6px; padding: 8px 14px; font-weight: bold; }
                    QPushButton:hover { background-color: #dc2626; }
                """)
            else:
                self.btn_hide_names.setText("👁️ Noms visibles")
                self.btn_hide_names.setStyleSheet("""
                    QPushButton { background-color: #334155; color: #E2E8F0; border: 1px solid #475569;
                                  border-radius: 6px; padding: 8px 14px; font-weight: normal; }
                    QPushButton:hover { background-color: #475569; }
                """)
        except Exception as e:
            log_error_to_file("CorbeilleWindow._update_hide_names_button_style", e)

    def refresh_for_hide_names(self):
        """Called by the dashboard when the global hide_names flag changes,
        so this window picks up the new mask state."""
        try:
            self._update_hide_names_button_style()
            self.refresh_list()
        except Exception as e:
            log_error_to_file("CorbeilleWindow.refresh_for_hide_names", e)

    def _selected_tids(self):
        tids = []
        for item in self.list_widget.selectedItems():
            tid = item.data(Qt.ItemDataRole.UserRole)
            if tid:
                tids.append(tid)
        return tids

    def _safe_name(self, tid):
        """If a target with the same name already exists in targets/, suffix it."""
        if os.path.exists(os.path.join(TARGETS_DIR, f"{tid}.json")):
            import time as _t
            return f"{tid}_restored_{int(_t.time())}"
        return tid

    def restore_selected(self):
        tids = self._selected_tids()
        if not tids:
            QMessageBox.information(self, "Aucune sélection", "Veuillez sélectionner au moins une cible à restaurer.")
            return

        reply = QMessageBox.question(
            self, "Restaurer", f"Restaurer {len(tids)} cible(s) ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            restored = 0
            skipped = 0
            for tid in tids:
                src = os.path.join(TRASH_DIR, f"{tid}.json")
                if not os.path.exists(src):
                    skipped += 1
                    continue
                new_tid = self._safe_name(tid)
                dst = os.path.join(TARGETS_DIR, f"{new_tid}.json")
                os.rename(src, dst)
                # Carry over the hidden metadata if present
                if new_tid != tid:
                    rename_target_meta(tid, new_tid)
                restored += 1

            self.refresh_list()
            # Refresh parent windows
            if hasattr(self.main_win, 'rebuild_target_list'):
                self.main_win.rebuild_target_list()
            if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                self.main_win.config_win.refresh_targets_list()
            if hasattr(self.main_win, 'sandbox_win') and self.main_win.sandbox_win and self.main_win.sandbox_win.isVisible():
                self.main_win.sandbox_win.refresh_targets()

            QMessageBox.information(self, "Restauration terminée",
                                    f"{restored} cible(s) restaurée(s)." +
                                    (f" {skipped} introuvable(s)." if skipped else ""))
        except Exception as e:
            log_error_to_file("CorbeilleWindow.restore_selected", e)
            log_error("CorbeilleWindow.restore_selected", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la restauration : {e}")

    def delete_selected(self):
        tids = self._selected_tids()
        if not tids:
            QMessageBox.information(self, "Aucune sélection",
                                    "Veuillez sélectionner au moins une cible à supprimer définitivement.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Suppression définitive")
        msg.setText(f"Supprimer définitivement {len(tids)} cible(s) ?")
        msg.setInformativeText("⚠️ Cette action est IRRÉVERSIBLE. Les fichiers JSON, "
                               "le dossier vidéo associé et toutes les publications seront perdus.")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Oui, supprimer définitivement")
        msg.button(QMessageBox.StandardButton.No).setText("Annuler")
        from theme import get_theme as _gt_msg
        _t_msg = _gt_msg()
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {_t_msg['bg']}; color: {_t_msg['text']}; }}
            QLabel {{ color: {_t_msg['text']}; font-size: 13px; }}
            QPushButton {{ background-color: {_t_msg['bg_alt']}; color: {_t_msg['text']}; border: 1px solid {_t_msg['border_hover']};
                          padding: 8px 16px; border-radius: 6px; font-weight: normal; }}
            QPushButton:hover {{ background-color: {_t_msg['border_hover']}; border-color: {_t_msg['accent']}; color: {_t_msg['accent_text']}; }}
        """)
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return

        try:
            from config import VIDEOS_DIR
            deleted = 0
            for tid in tids:
                # Delete JSON from trash
                json_path = os.path.join(TRASH_DIR, f"{tid}.json")
                if os.path.exists(json_path):
                    os.remove(json_path)
                # Delete associated video folder (sandbox media)
                vid_dir = os.path.join(VIDEOS_DIR, tid)
                if os.path.exists(vid_dir) and os.path.isdir(vid_dir):
                    try:
                        import shutil
                        shutil.rmtree(vid_dir, ignore_errors=True)
                    except Exception as e:
                        log_error_to_file("CorbeilleWindow.delete_selected.video_dir", e)
                # Remove metadata entry
                remove_target_meta(tid)
                deleted += 1

            self.refresh_list()
            if hasattr(self.main_win, 'rebuild_target_list'):
                self.main_win.rebuild_target_list()
            if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                self.main_win.config_win.refresh_targets_list()

            QMessageBox.information(self, "Suppression terminée",
                                    f"{deleted} cible(s) supprimée(s) définitivement.")
        except Exception as e:
            log_error_to_file("CorbeilleWindow.delete_selected", e)
            log_error("CorbeilleWindow.delete_selected", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def empty_corbeille(self):
        tids = self._list_trashed()
        if not tids:
            QMessageBox.information(self, "Corbeille vide", "La corbeille est déjà vide.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Vider la corbeille")
        msg.setText(f"Vider toute la corbeille ? ({len(tids)} cible(s))")
        msg.setInformativeText("⚠️ Cette action est IRRÉVERSIBLE. Toutes les cibles de la corbeille "
                               "ainsi que leurs dossiers vidéo associés seront définitivement supprimés.")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Oui, tout supprimer")
        msg.button(QMessageBox.StandardButton.No).setText("Annuler")
        from theme import get_theme as _gt_msg
        _t_msg = _gt_msg()
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {_t_msg['bg']}; color: {_t_msg['text']}; }}
            QLabel {{ color: {_t_msg['text']}; font-size: 13px; }}
            QPushButton {{ background-color: {_t_msg['bg_alt']}; color: {_t_msg['text']}; border: 1px solid {_t_msg['border_hover']};
                          padding: 8px 16px; border-radius: 6px; font-weight: normal; }}
            QPushButton:hover {{ background-color: {_t_msg['border_hover']}; border-color: {_t_msg['accent']}; color: {_t_msg['accent_text']}; }}
        """)
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return

        try:
            from config import VIDEOS_DIR
            import shutil
            deleted = 0
            for tid in tids:
                json_path = os.path.join(TRASH_DIR, f"{tid}.json")
                if os.path.exists(json_path):
                    os.remove(json_path)
                vid_dir = os.path.join(VIDEOS_DIR, tid)
                if os.path.exists(vid_dir) and os.path.isdir(vid_dir):
                    shutil.rmtree(vid_dir, ignore_errors=True)
                remove_target_meta(tid)
                deleted += 1

            self.refresh_list()
            if hasattr(self.main_win, 'rebuild_target_list'):
                self.main_win.rebuild_target_list()
            if hasattr(self.main_win, 'config_win') and self.main_win.config_win:
                self.main_win.config_win.refresh_targets_list()

            QMessageBox.information(self, "Corbeille vidée",
                                    f"{deleted} cible(s) supprimée(s) définitivement.")
        except Exception as e:
            log_error_to_file("CorbeilleWindow.empty_corbeille", e)
            log_error("CorbeilleWindow.empty_corbeille", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors du vidage : {e}")

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        self.center()
        self.refresh_list()
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
