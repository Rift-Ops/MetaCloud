"""system_settings.py — Global system settings window (debug mode, credentials folder, ...).

The window is resizable and uses a QScrollArea so it can be shrunk below its
natural content size. The Annuler / Confirmer buttons stay fixed at the bottom
(outside the scroll area) so they are always reachable.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QPushButton, QLineEdit, QFileDialog,
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt
import config as _config
from widgets import ModernToggleSwitch


class SystemSettingsWindow(QDialog):
    """Modal dialog for global system settings.

    Layout:
      ┌─────────────────────────────────────┐
      │  ┌─ QScrollArea (resizable) ──────┐ │
      │  │  Apparence (theme color)       │ │
      │  │  Débogage                      │ │
      │  │  Affichage (hide names)        │ │
      │  │  Sécurité (hide credentials)   │ │
      │  │  Dossier des identifiants      │ │
      │  └────────────────────────────────┘ │
      │  [Annuler]            [Confirmer]   │  ← fixed at bottom
      └─────────────────────────────────────┘
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres système")
        # Resizable window with a small minimum — the scroll area handles overflow.
        self.setMinimumSize(480, 360)
        self.resize(620, 680)
        self._apply_theme_style()
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint
                            | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

        # Local pending values (not applied until Confirmer)
        self._pending_debug = _config.debug_mode
        self._pending_credentials_folder = _config.get_credentials_folder()
        self._pending_hide_names = _config.is_hide_names()
        self._pending_hide_credentials = _config.is_hide_credentials()
        self._pending_theme_color = _config.get_theme_color()
        self._pending_encrypt_files = _config.is_encrypt_files()
        self._pending_notifications = _config.is_notifications_enabled()

        # ── Outer layout: scroll area (top) + buttons (bottom) ──
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(14)

        # ═══════════════════ Scrollable content ═══════════════════
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        root = QVBoxLayout(scroll_content)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # ── Appearance section (theme color) ──
        grp_theme = QGroupBox("Apparence")
        theme_lay = QVBoxLayout(grp_theme)

        lbl_theme_desc = QLabel("Couleur de l'interface :")
        from theme import get_theme as _gt
        _t = _gt()
        lbl_theme_desc.setStyleSheet(f"color: {_t['text']}; font-size: 12px;")
        theme_lay.addWidget(lbl_theme_desc)

        # 4 color buttons in a row
        from theme import THEMES
        colors_row = QHBoxLayout()
        colors_row.setSpacing(10)
        self._theme_buttons = {}
        for key, t in THEMES.items():
            btn = QPushButton(f"{t['icon']} {t['name']}")
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            if key == self._pending_theme_color:
                btn.setChecked(True)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t['accent']}; color: white; border: 2px solid {t['text']};
                        border-radius: 8px; font-weight: bold; padding: 8px 14px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t['bg_alt']}; color: {t['text']};
                        border: 2px solid {t['accent']};
                        border-radius: 8px; font-weight: normal; padding: 8px 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {t['accent']}; color: white;
                    }}
                """)
            btn.clicked.connect(lambda checked, k=key: self._on_theme_color_selected(k))
            colors_row.addWidget(btn)
            self._theme_buttons[key] = btn
        theme_lay.addLayout(colors_row)

        root.addWidget(grp_theme)

        # ── Debug section ──
        grp_debug = QGroupBox("Débogage")
        debug_lay = QHBoxLayout(grp_debug)

        lbl_desc = QLabel("Mode Debug : afficher les erreurs dans les\nlogs des victimes en temps réel")
        lbl_desc.setWordWrap(True)
        debug_lay.addWidget(lbl_desc, stretch=1)

        self.toggle_debug = ModernToggleSwitch()
        self.toggle_debug.set_state(self._pending_debug)
        self.toggle_debug.toggled.connect(self._on_debug_toggled)
        debug_lay.addWidget(self.toggle_debug, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_debug)

        # ── Display section (hide victim names) ──
        grp_display = QGroupBox("Affichage")
        display_lay = QHBoxLayout(grp_display)

        lbl_names = QLabel("Masquer les noms des victimes :\n"
                           "Les noms sont remplacés par 'Cible #XXXX'\n"
                           "dans le dashboard, les identifiants et la corbeille.")
        lbl_names.setWordWrap(True)
        display_lay.addWidget(lbl_names, stretch=1)

        self.toggle_hide_names = ModernToggleSwitch()
        self.toggle_hide_names.set_state(self._pending_hide_names)
        self.toggle_hide_names.toggled.connect(self._on_hide_names_toggled)
        display_lay.addWidget(self.toggle_hide_names, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_display)

        # ── Security section (hide credentials) ──
        grp_security = QGroupBox("Sécurité")
        security_lay = QHBoxLayout(grp_security)

        lbl_cred = QLabel("Masquer les identifiants capturés :\n"
                          "Les emails et mots de passe sont masqués\n"
                          "jusqu'à ce que vous cliquiez sur '👁️ Voir'.")
        lbl_cred.setWordWrap(True)
        security_lay.addWidget(lbl_cred, stretch=1)

        self.toggle_hide_credentials = ModernToggleSwitch()
        self.toggle_hide_credentials.set_state(self._pending_hide_credentials)
        self.toggle_hide_credentials.toggled.connect(self._on_hide_credentials_toggled)
        security_lay.addWidget(self.toggle_hide_credentials, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_security)

        # ── Notifications section (show toast when credentials are captured) ──
        grp_notif = QGroupBox("Notifications")
        notif_lay = QVBoxLayout(grp_notif)

        lbl_notif = QLabel("Afficher une notification système quand un identifiant est capturé :\n"
                           "Utilise les notifications natives du système d'exploitation\n"
                           "(Windows toast, Linux libnotify, macOS Notification Center)\n"
                           "via le module plyer.")
        lbl_notif.setWordWrap(True)
        notif_lay.addWidget(lbl_notif)

        # Description du comportement de masquage
        lbl_notif_mask = QLabel("ℹ️ Les paramètres « Masquer les noms des victimes » et\n"
                                "« Masquer les identifiants capturés » ci-dessus s'appliquent\n"
                                "aussi aux notifications : le nom de la cible et les valeurs\n"
                                "des identifiants seront masqués si ces options sont activées.")
        from theme import get_theme as _gt_notif
        _t_notif = _gt_notif()
        lbl_notif_mask.setStyleSheet(f"color: {_t_notif['text_dim']}; font-size: 11px; font-style: italic;")
        lbl_notif_mask.setWordWrap(True)
        notif_lay.addWidget(lbl_notif_mask)

        # Toggle row
        notif_toggle_row = QHBoxLayout()
        notif_toggle_row.addWidget(QLabel("Activer les notifications de capture :"), stretch=1)
        self.toggle_notifications = ModernToggleSwitch()
        self.toggle_notifications.set_state(self._pending_notifications)
        self.toggle_notifications.toggled.connect(self._on_notifications_toggled)
        notif_toggle_row.addWidget(self.toggle_notifications, alignment=Qt.AlignmentFlag.AlignRight)
        notif_lay.addLayout(notif_toggle_row)

        root.addWidget(grp_notif)

        # ── Encryption section (file encryption on disk) ──
        grp_encrypt = QGroupBox("Chiffrement des fichiers")
        encrypt_lay = QHBoxLayout(grp_encrypt)

        lbl_encrypt = QLabel("Chiffrer les identifiants sur disque :\n"
                             "Les fichiers JSON d'identifiants sont chiffrés.\n"
                             "Désactivé = stockage en clair.")
        lbl_encrypt.setWordWrap(True)
        encrypt_lay.addWidget(lbl_encrypt, stretch=1)

        self.toggle_encrypt_files = ModernToggleSwitch()
        self.toggle_encrypt_files.set_state(self._pending_encrypt_files)
        self.toggle_encrypt_files.toggled.connect(self._on_encrypt_files_toggled)
        encrypt_lay.addWidget(self.toggle_encrypt_files, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_encrypt)

        # ── Chiffrement credentials.txt ──
        grp_encrypt_cred = QGroupBox("Chiffrement credentials.txt")
        encrypt_cred_lay = QHBoxLayout(grp_encrypt_cred)

        lbl_encrypt_cred = QLabel("Chiffrer le fichier credentials.txt sur disque :\n"
                                  "Le fichier de logs d'identifiants sera chiffré.\n"
                                  "Désactivé = stockage en clair.")
        lbl_encrypt_cred.setWordWrap(True)
        encrypt_cred_lay.addWidget(lbl_encrypt_cred, stretch=1)

        self._pending_encrypt_credentials_txt = _config.get_global_setting("encrypt_credentials_txt", False)
        self.toggle_encrypt_credentials_txt = ModernToggleSwitch()
        self.toggle_encrypt_credentials_txt.set_state(self._pending_encrypt_credentials_txt)
        self.toggle_encrypt_credentials_txt.toggled.connect(self._on_encrypt_credentials_txt_toggled)
        encrypt_cred_lay.addWidget(self.toggle_encrypt_credentials_txt, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_encrypt_cred)

        # ── Chiffrement global_settings.json ──
        grp_encrypt_settings = QGroupBox("Chiffrement global_settings.json")
        encrypt_settings_lay = QHBoxLayout(grp_encrypt_settings)

        lbl_encrypt_settings = QLabel("Chiffrer le fichier global_settings.json sur disque :\n"
                                      "Les paramètres globaux seront chiffrés.\n"
                                      "Désactivé = stockage en clair.")
        lbl_encrypt_settings.setWordWrap(True)
        encrypt_settings_lay.addWidget(lbl_encrypt_settings, stretch=1)

        self._pending_encrypt_global_settings = _config.get_global_setting("encrypt_global_settings", False)
        self.toggle_encrypt_global_settings = ModernToggleSwitch()
        self.toggle_encrypt_global_settings.set_state(self._pending_encrypt_global_settings)
        self.toggle_encrypt_global_settings.toggled.connect(self._on_encrypt_global_settings_toggled)
        encrypt_settings_lay.addWidget(self.toggle_encrypt_global_settings, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_encrypt_settings)

        # ── Chiffrement targets_meta.json ──
        grp_encrypt_meta = QGroupBox("Chiffrement targets_meta.json")
        encrypt_meta_lay = QHBoxLayout(grp_encrypt_meta)

        lbl_encrypt_meta = QLabel("Chiffrer le fichier targets_meta.json sur disque :\n"
                                  "Les métadonnées des cibles seront chiffrées.\n"
                                  "Désactivé = stockage en clair.")
        lbl_encrypt_meta.setWordWrap(True)
        encrypt_meta_lay.addWidget(lbl_encrypt_meta, stretch=1)

        self._pending_encrypt_targets_meta = _config.get_global_setting("encrypt_targets_meta", False)
        self.toggle_encrypt_targets_meta = ModernToggleSwitch()
        self.toggle_encrypt_targets_meta.set_state(self._pending_encrypt_targets_meta)
        self.toggle_encrypt_targets_meta.toggled.connect(self._on_encrypt_targets_meta_toggled)
        encrypt_meta_lay.addWidget(self.toggle_encrypt_targets_meta, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(grp_encrypt_meta)

        # ── Credentials folder section ──
        grp_cred = QGroupBox("Dossier des identifiants capturés")
        cred_lay = QVBoxLayout(grp_cred)

        lbl_cred_desc = QLabel("Dossier où sont stockés les identifiants capturés (JSON).\n"
                               "Par défaut : targets/<cible>/credentials/\n"
                               "Personnalisé : <dossier choisi>/<cible>/")
        lbl_cred_desc.setWordWrap(True)
        from theme import get_theme as _gt2
        _t2 = _gt2()
        lbl_cred_desc.setStyleSheet(f"color: {_t2['text_dim']}; font-size: 11px;")
        cred_lay.addWidget(lbl_cred_desc)

        # Folder path display + browse + reset buttons
        folder_row = QHBoxLayout()
        folder_row.setSpacing(8)

        folder_row.addWidget(QLabel("Dossier :"))

        self.txt_cred_folder = QLineEdit()
        self.txt_cred_folder.setReadOnly(True)
        self.txt_cred_folder.setPlaceholderText("(par défaut : targets/<cible>/credentials/)")
        if self._pending_credentials_folder:
            self.txt_cred_folder.setText(self._pending_credentials_folder)
        folder_row.addWidget(self.txt_cred_folder, stretch=1)

        self.btn_browse_cred = QPushButton("📂 Parcourir")
        self.btn_browse_cred.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; color: white; border: none;
                font-weight: bold; border-radius: 6px; padding: 8px 14px; font-size: 12px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton:pressed { background-color: #1d4ed8; }
        """)
        self.btn_browse_cred.clicked.connect(self._browse_cred_folder)
        folder_row.addWidget(self.btn_browse_cred)

        self.btn_reset_cred = QPushButton("↺ Par défaut")
        self.btn_reset_cred.setStyleSheet("""
            QPushButton {
                background-color: #475569; color: #E2E8F0; border: 1px solid #64748B;
                font-weight: bold; border-radius: 6px; padding: 8px 14px; font-size: 12px;
            }
            QPushButton:hover { background-color: #64748B; }
            QPushButton:pressed { background-color: #334155; }
        """)
        self.btn_reset_cred.clicked.connect(self._reset_cred_folder)
        folder_row.addWidget(self.btn_reset_cred)

        cred_lay.addLayout(folder_row)

        root.addWidget(grp_cred)

        root.addStretch()

        # Install the scroll content
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll, stretch=1)

        # ═══════════════════ Fixed bottom buttons ═══════════════════
        btn_lay = QHBoxLayout()
        btn_close = QPushButton("Annuler")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #475569; color: #E2E8F0; border: none;
                font-weight: bold; border-radius: 8px; padding: 10px 28px; font-size: 13px;
            }
            QPushButton:hover { background-color: #64748B; }
            QPushButton:pressed { background-color: #334155; }
        """)
        btn_close.clicked.connect(self.reject)
        btn_lay.addWidget(btn_close)

        btn_confirm = QPushButton("Confirmer")
        btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #22c55e; color: white; border: none;
                font-weight: bold; border-radius: 8px; padding: 10px 28px; font-size: 13px;
            }
            QPushButton:hover { background-color: #16a34a; }
            QPushButton:pressed { background-color: #15803d; }
        """)
        btn_confirm.clicked.connect(self._confirm)
        btn_lay.addWidget(btn_confirm)

        outer.addLayout(btn_lay)

    def _apply_theme_style(self):
        """Build and apply the window stylesheet using the current theme colors.
        Called at __init__ and again by refresh_theme() when the theme changes.
        Does NOT modify the window structure — only colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {t['bg']};
                    color: {t['text']};
                }}
                QGroupBox {{
                    background-color: {t['bg_alt']};
                    border: 1px solid {t['border']};
                    border-radius: 10px;
                    margin-top: 14px;
                    padding: 18px 14px 14px 14px;
                    font-weight: bold;
                    font-size: 13px;
                    color: {t['text_dim']};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 2px 10px;
                    color: {t['accent']};
                }}
                QLabel {{
                    color: {t['text']};
                    font-size: 12px;
                }}
                QLineEdit {{
                    background-color: {t['bg_input']};
                    border: 1px solid {t['border_hover']};
                    border-radius: 6px;
                    padding: 8px 10px;
                    color: {t['text']};
                    font-size: 12px;
                }}
                QLineEdit:read-only {{
                    color: {t['text_dim']};
                    background-color: {t['bg_alt']};
                }}
                QScrollArea {{
                    background-color: {t['bg']};
                    border: none;
                }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("SystemSettingsWindow._apply_theme_style", e)
            except Exception:
                pass

    # ── Handlers ──
    def _on_debug_toggled(self, state):
        """Only update the local pending value (no save yet)."""
        self._pending_debug = bool(state)

    def _on_hide_names_toggled(self, state):
        """Only update the local pending value (no save yet)."""
        self._pending_hide_names = bool(state)

    def _on_hide_credentials_toggled(self, state):
        """Only update the local pending value (no save yet)."""
        self._pending_hide_credentials = bool(state)

    def _on_notifications_toggled(self, state):
        """Only update the local pending value (no save yet)."""
        self._pending_notifications = bool(state)

    def _on_encrypt_files_toggled(self, state):
        """Only update the local pending value (no save yet)."""
        self._pending_encrypt_files = bool(state)

    def _on_encrypt_credentials_txt_toggled(self, state):
        """Toggle chiffrement credentials.txt."""
        self._pending_encrypt_credentials_txt = bool(state)

    def _on_encrypt_global_settings_toggled(self, state):
        """Toggle chiffrement global_settings.json."""
        self._pending_encrypt_global_settings = bool(state)

    def _on_encrypt_targets_meta_toggled(self, state):
        """Toggle chiffrement targets_meta.json."""
        self._pending_encrypt_targets_meta = bool(state)

    def _on_theme_color_selected(self, color_key):
        """Update the selected theme color and refresh the button highlights.
        The theme is NOT applied yet — only on Confirm."""
        try:
            from theme import THEMES
            if color_key not in THEMES:
                return
            self._pending_theme_color = color_key
            # Refresh all theme button styles to show the new selection
            for key, btn in self._theme_buttons.items():
                t = THEMES[key]
                if key == color_key:
                    btn.setChecked(True)
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {t['accent']}; color: white; border: 2px solid {t['text']};
                            border-radius: 8px; font-weight: bold; padding: 8px 14px;
                        }}
                    """)
                else:
                    btn.setChecked(False)
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {t['bg_alt']}; color: {t['text']};
                            border: 2px solid {t['accent']};
                            border-radius: 8px; font-weight: normal; padding: 8px 14px;
                        }}
                        QPushButton:hover {{
                            background-color: {t['accent']}; color: white;
                        }}
                    """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("SystemSettingsWindow._on_theme_color_selected", e)
            except Exception as e2:
                try:
                    import sys as _sys
                    _sys.stderr.write(f"[SystemSettings._on_theme_color_selected] log failed: {e2}\n")
                except Exception:
                    pass

    def _browse_cred_folder(self):
        """Open a folder picker and store the chosen path in the pending value."""
        try:
            start_dir = self._pending_credentials_folder or _config.ROOT_DIR
            folder = QFileDialog.getExistingDirectory(
                self, "Choisir le dossier des identifiants", start_dir,
                QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
            )
            if folder:
                self._pending_credentials_folder = folder
                self.txt_cred_folder.setText(folder)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("SystemSettingsWindow._browse_cred_folder", e)
            except Exception as e2:
                try:
                    import sys as _sys
                    _sys.stderr.write(f"[SystemSettings._browse] log failed: {e2}\n")
                except Exception:
                    pass

    def _reset_cred_folder(self):
        """Reset the credentials folder to the default location."""
        self._pending_credentials_folder = ""
        self.txt_cred_folder.setText("")

    def _confirm(self):
        """Apply & persist all pending settings."""
        try:
            _config.debug_mode = self._pending_debug
            _config.set_debug_mode(self._pending_debug)
            _config.set_credentials_folder(self._pending_credentials_folder)
            _config.set_hide_names(self._pending_hide_names)
            _config.set_hide_credentials(self._pending_hide_credentials)
            _config.set_theme_color(self._pending_theme_color)
            _config.set_notifications_enabled(self._pending_notifications)

            # Handle file encryption toggle
            old_encrypt = _config.is_encrypt_files()
            _config.set_encrypt_files(self._pending_encrypt_files)
            new_encrypt = _config.is_encrypt_files()

            # ── Sauvegarder les nouveaux toggles de chiffrement ──
            try:
                _config.set_global_setting("encrypt_credentials_txt", self._pending_encrypt_credentials_txt)
                _config.set_global_setting("encrypt_global_settings", self._pending_encrypt_global_settings)
                _config.set_global_setting("encrypt_targets_meta", self._pending_encrypt_targets_meta)
            except Exception as e:
                try:
                    from helpers import log_error
                    log_error("SystemSettingsWindow._confirm.encrypt_toggles", e)
                except Exception:
                    pass

            # ── Appliquer le chiffrement aux fichiers concernés ──
            try:
                from crypto import is_encrypted, encrypt_text, decrypt_text
                import os as _os

                # credentials.txt — chiffrer ou déchiffrer
                cred_path = _os.path.join(_config.ROOT_DIR, "credentials.txt")
                if _os.path.exists(cred_path):
                    try:
                        with open(cred_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if content.strip():
                            currently_encrypted = is_encrypted(content)
                            if self._pending_encrypt_credentials_txt and not currently_encrypted:
                                # Chiffrer
                                with open(cred_path, 'w', encoding='utf-8') as f:
                                    f.write(encrypt_text(content))
                            elif not self._pending_encrypt_credentials_txt and currently_encrypted:
                                # Déchiffrer
                                with open(cred_path, 'w', encoding='utf-8') as f:
                                    f.write(decrypt_text(content))
                    except Exception as e:
                        from helpers import log_error
                        log_error("SystemSettings.encrypt_credentials_txt", e)

                # global_settings.json
                gs_path = _config.GLOBAL_SETTINGS_FILE
                if _os.path.exists(gs_path):
                    try:
                        with open(gs_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if self._pending_encrypt_global_settings:
                            if content and not is_encrypted(content):
                                with open(gs_path, 'w', encoding='utf-8') as f:
                                    f.write(encrypt_text(content))
                        else:
                            if content and is_encrypted(content):
                                decrypted = decrypt_text(content)
                                with open(gs_path, 'w', encoding='utf-8') as f:
                                    f.write(decrypted)
                    except Exception as e:
                        from helpers import log_error
                        log_error("SystemSettings.encrypt_global_settings", e)

                # targets_meta.json
                tm_path = _config.TARGETS_META_FILE
                if _os.path.exists(tm_path):
                    try:
                        with open(tm_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if self._pending_encrypt_targets_meta:
                            if content and not is_encrypted(content):
                                with open(tm_path, 'w', encoding='utf-8') as f:
                                    f.write(encrypt_text(content))
                        else:
                            if content and is_encrypted(content):
                                decrypted = decrypt_text(content)
                                with open(tm_path, 'w', encoding='utf-8') as f:
                                    f.write(decrypted)
                    except Exception as e:
                        from helpers import log_error
                        log_error("SystemSettings.encrypt_targets_meta", e)
            except Exception as e:
                try:
                    from helpers import log_error
                    log_error("SystemSettingsWindow._confirm.file_encryption", e)
                except Exception:
                    pass

            # If the encryption setting changed, migrate existing files
            if old_encrypt != new_encrypt:
                try:
                    self._migrate_encryption(new_encrypt)
                except Exception as mig_err:
                    try:
                        from helpers import log_error
                        log_error("SystemSettingsWindow._confirm.migrate_encryption", mig_err)
                    except Exception:
                        pass

            # Apply the new theme globally (refreshes all open windows + buttons)
            try:
                from theme import refresh_theme
                refresh_theme()
            except Exception as e:
                try:
                    from helpers import log_error
                    log_error("SystemSettingsWindow._confirm.refresh_theme", e)
                except Exception:
                    pass

            # ── Notify the parent dashboard so it can refresh itself AND propagate
            # the hide_names change to its child windows (sandbox, credentials,
            # corbeille, target config). Each child window implements
            # refresh_for_hide_names() to re-mask its UI labels.
            try:
                parent = self.parent()
                if parent is not None:
                    # Dashboard itself
                    if hasattr(parent, 'rebuild_target_list'):
                        try:
                            from PyQt6.QtCore import QTimer
                            QTimer.singleShot(0, parent.rebuild_target_list)
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("SystemSettingsWindow._confirm.rebuild_target_list", e)
                            except Exception:
                                pass
                    if hasattr(parent, 'selected_tid') and parent.selected_tid:
                        try:
                            from config import mask_name
                            if hasattr(parent, 'lbl_log_title') and parent.lbl_log_title:
                                parent.lbl_log_title.setText(f"<b>Logs :</b> {mask_name(parent.selected_tid)}")
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("SystemSettingsWindow._confirm.lbl_log_title", e)
                            except Exception:
                                pass
                    # Sandbox window
                    if hasattr(parent, 'sandbox_win') and parent.sandbox_win:
                        try:
                            if hasattr(parent.sandbox_win, 'refresh_for_hide_names'):
                                parent.sandbox_win.refresh_for_hide_names()
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("SystemSettingsWindow._confirm.sandbox_refresh", e)
                            except Exception:
                                pass
                    # Config window (target editor)
                    if hasattr(parent, 'config_win') and parent.config_win:
                        try:
                            if hasattr(parent.config_win, 'refresh_for_hide_names'):
                                parent.config_win.refresh_for_hide_names()
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("SystemSettingsWindow._confirm.config_refresh", e)
                            except Exception:
                                pass
                    # Credentials window
                    if hasattr(parent, 'credentials_win') and parent.credentials_win:
                        try:
                            if hasattr(parent.credentials_win, 'refresh_for_hide_names'):
                                parent.credentials_win.refresh_for_hide_names()
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("SystemSettingsWindow._confirm.creds_refresh", e)
                            except Exception:
                                pass
                    # Corbeille (trash) window
                    if hasattr(parent, 'corbeille_win') and parent.corbeille_win:
                        try:
                            if hasattr(parent.corbeille_win, 'refresh_for_hide_names'):
                                parent.corbeille_win.refresh_for_hide_names()
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("SystemSettingsWindow._confirm.corbeille_refresh", e)
                            except Exception:
                                pass
            except Exception as e:
                try:
                    from helpers import log_error
                    log_error("SystemSettingsWindow._confirm.notify_children", e)
                except Exception:
                    pass
        except Exception as e:
            try:
                from helpers import log_error
                log_error("SystemSettingsWindow._confirm", e)
            except Exception as e2:
                try:
                    import sys as _sys
                    _sys.stderr.write(f"[SystemSettings._confirm] log failed: {e2}\n")
                except Exception:
                    pass
        self.accept()

    def _migrate_encryption(self, encrypt_mode):
        """Migrate existing credential and log files between encrypted/plaintext.
        encrypt_mode=True → encrypt all plaintext files
        encrypt_mode=False → decrypt all encrypted files"""
        try:
            import os
            import glob
            from crypto import encrypt_file, is_encrypted, encrypt_text, decrypt_text

            # 1. Migrate credential JSON files
            try:
                import credentials_manager as cm
                for _target_id, cred_dir in cm._iter_all_cred_dirs():
                    if not os.path.isdir(cred_dir):
                        continue
                    for fpath in glob.glob(os.path.join(cred_dir, "*.json")):
                        try:
                            with open(fpath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            if encrypt_mode and not is_encrypted(content):
                                # Encrypt plaintext file
                                encrypted = encrypt_text(content)
                                with open(fpath, 'w', encoding='utf-8') as f:
                                    f.write(encrypted)
                            elif not encrypt_mode and is_encrypted(content):
                                # Decrypt encrypted file
                                decrypted = decrypt_text(content)
                                with open(fpath, 'w', encoding='utf-8') as f:
                                    f.write(decrypted)
                        except Exception as file_err:
                            try:
                                from helpers import log_error
                                log_error(f"SystemSettings._migrate_encryption[{fpath}]", file_err)
                            except Exception:
                                pass
            except Exception as cred_err:
                try:
                    from helpers import log_error
                    log_error("SystemSettings._migrate_encryption.credentials", cred_err)
                except Exception:
                    pass

            # 2. Error log files are NOT migrated — they stay plaintext for performance
            # (error logs use fast append, not read-rewrite)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("SystemSettings._migrate_encryption", e)
            except Exception:
                pass
