"""publication_dialog.py — auto-generated from widgets.py."""

import os
import base64
from PyQt6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QRadioButton, QComboBox, QScrollArea, QFileDialog, QMenu, QInputDialog, QStyle, QStyleOptionButton, QGridLayout, QWidget, QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QFrame, QFormLayout, QStackedWidget, QSizePolicy, QAbstractItemView
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QCursor, QColor, QPixmap
from templates import FEED_COLORS, REACTIONS_MAP
from config import BASE_CONFIG as default_config

from ._header import FEED_COLORS, QCheckBox, QComboBox, QCursor, QDialog, QFileDialog, QFormLayout, QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QMenu, QPushButton, QRadioButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget, Qt, REACTIONS_MAP, default_config, os
from .bounce_button import BounceButton
from .media_selector import MediaSelectorDialog
from .text_editor import TextEditorDialog


# ════════════════════════════════════════════════════════════════════
#  _ExtraImageThumb — widget de miniature pour les images supplémentaires
# ════════════════════════════════════════════════════════════════════

class _ExtraImageThumb(QWidget):
    """Miniature horizontale pour la galerie d'images supplémentaires."""

    def __init__(self, index, img_path, parent_dialog):
        try:
            super().__init__()
            self._index = index
            self._img_path = img_path
            self._parent_dialog = parent_dialog

            self.setFixedHeight(64)
            self.setMinimumWidth(300)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            layout = QHBoxLayout(self)
            layout.setContentsMargins(6, 4, 6, 4)
            layout.setSpacing(8)

            # Thumbnail
            self._lbl = QLabel()
            self._lbl.setFixedSize(80, 56)
            self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._lbl.setStyleSheet("background: #1a1a1a; border-radius: 4px; border: 1px solid #333;")
            self._load_thumbnail()
            layout.addWidget(self._lbl)

            # Right column
            right_col = QVBoxLayout()
            right_col.setContentsMargins(0, 0, 0, 0)
            right_col.setSpacing(2)

            # Index + filename
            fname = os.path.basename(img_path) if img_path else ""
            if len(fname) > 35:
                fname = fname[:32] + "..."
            self._info_lbl = QLabel(f"#{index + 2}  •  {fname}")
            self._info_lbl.setStyleSheet("color: #ddd; font-size: 11px; font-weight: bold;")
            right_col.addWidget(self._info_lbl)

            # Remove button
            btn_row = QHBoxLayout()
            btn_row.setSpacing(4)
            self._btn_rm = QPushButton("✕ Retirer")
            self._btn_rm.setFixedHeight(22)
            self._btn_rm.setMinimumWidth(70)
            self._btn_rm.setStyleSheet(
                "QPushButton { background: #ef4444; color: white; border: none; border-radius: 4px; "
                "font-size: 10px; padding: 2px 8px; font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial; }"
                "QPushButton:hover { background: #dc2626; }")
            self._btn_rm.clicked.connect(self._on_remove)
            btn_row.addWidget(self._btn_rm)
            btn_row.addStretch()
            btn_w = QWidget(); btn_w.setLayout(btn_row)
            right_col.addWidget(btn_w)

            right_w = QWidget(); right_w.setLayout(right_col)
            layout.addWidget(right_w, stretch=1)

        except Exception as e:
            try:
                from helpers import log_error
                log_error("_ExtraImageThumb.__init__", e)
            except Exception:
                pass

    def _on_remove(self):
        try:
            row = self._parent_dialog._extra_list.indexAt(self.pos()).row()
            if row >= 0:
                self._parent_dialog.remove_extra_image(row)
        except Exception:
            pass

    def _load_thumbnail(self):
        try:
            full_path = self._img_path
            if self._img_path and not os.path.isabs(self._img_path) and not self._img_path.startswith("http"):
                try:
                    from config import get_video_dir, VIDEOS_DIR
                    video_dir = get_video_dir(self._parent_dialog.tid)
                    if video_dir:
                        full_path = os.path.join(video_dir, self._img_path)
                    if not os.path.exists(full_path):
                        full_path = os.path.join(VIDEOS_DIR, self._parent_dialog.tid, self._img_path)
                except Exception:
                    pass
            if self._img_path and (self._img_path.startswith("http://") or self._img_path.startswith("https://")):
                self._lbl.setText("🔗\nlien")
                return
            pix = QPixmap(full_path)
            if not pix.isNull():
                self._lbl.setPixmap(pix.scaled(76, 52, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
            else:
                self._lbl.setText("IMG")
        except Exception:
            self._lbl.setText("IMG")


class PublicationDialog(QDialog):
    def __init__(self, parent=None, pub_data=None, tid=None, platform="facebook"):
        super().__init__(parent)
        self.tid = tid
        self.platform = platform or "facebook"
        self.setWindowTitle("Configuration de la Publication")
        self.setMinimumSize(850, 600)
        # Load theme colors once for all checkboxes in this dialog
        from theme import get_theme as _gt_chk
        self._t_chk = _gt_chk()

        # Load platform capabilities early (before building sidebar/pages)
        try:
            from platforms import get_capabilities_by_id
            self.caps = get_capabilities_by_id(self.platform)
        except Exception:
            self.caps = {}

        self._apply_theme_style()

        self.selected_bg = pub_data.get("bg", "#1877f2") if pub_data else "#1877f2"
        self._main_text = ""
        self._share_text = ""
        self.color_buttons = []
        self._extra_images = []  # Images supplémentaires pour le carousel

        main_lay = QHBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # 1. Sidebar (QListWidget) — filtered by platform capabilities
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        
        items = [
            ("📌 Général", "general"),
            ("👤 Identité & Auteur", "identity"),
            ("🖼️ Média & Contenu", "media"),
        ]
        # Only show "Post Partagé" if the platform supports share
        if self.caps.get("share", True):
            items.append(("🔄 Post Partagé", "share"))
        # Only show "Engagement" if the platform supports reactions or tags
        if self.caps.get("reactions", True) or self.caps.get("tags", True) or self.caps.get("sim_action", True):
            items.append(("❤️ Engagement", "engagement"))
        for text, _ in items:
            self.sidebar.addItem(text)
            
        main_lay.addWidget(self.sidebar)

        # 2. Main Content Area (QStackedWidget)
        right_container = QWidget()
        right_lay = QVBoxLayout(right_container)
        right_lay.setContentsMargins(15, 15, 15, 15)
        right_lay.setSpacing(10)
        
        self.stacked = QStackedWidget()
        right_lay.addWidget(self.stacked)
        
        # Bottom Buttons
        btn_lay = QHBoxLayout()
        btn_ok = BounceButton("✓ Valider")
        from theme import btn_style_accent as _bsa
        btn_ok.setStyleSheet(_bsa())
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = BounceButton("✕ Annuler")
        from theme import btn_style_danger as _bsd
        btn_cancel.setStyleSheet(_bsd())
        btn_cancel.clicked.connect(self.reject)
        
        btn_lay.addStretch()
        btn_lay.addWidget(btn_cancel)
        btn_lay.addWidget(btn_ok)
        right_lay.addLayout(btn_lay)
        
        main_lay.addWidget(right_container, 1)

        # Initialize UI Components (Create all attributes here to avoid AttributeErrors)
        self._init_attributes()

        # ── Platform-specific filtering ──
        # Filter audience dropdown based on platform capabilities
        allowed_audiences = self.caps.get("audiences", ["Public", "Amis", "Amis de mes amis", "Sponsorisé", "Privé"])
        self.i_audience.clear()
        self.i_audience.addItems(allowed_audiences)
        self.i_share_audience.clear()
        self.i_share_audience.addItems(allowed_audiences)

        # Note: unsupported features are handled at page-construction time
        # in _create_page_* methods — rows for unsupported features are simply
        # not added to the layout, which avoids orphaned labels.

        # Build Pages — only add pages that have a corresponding sidebar item
        # The sidebar row index will map directly to the stacked widget index
        self._page_indices = {}  # page_key -> stacked index
        idx = 0
        self.stacked.addWidget(self._create_page_general());     self._page_indices["general"] = idx; idx += 1
        self.stacked.addWidget(self._create_page_identity());    self._page_indices["identity"] = idx; idx += 1
        self.stacked.addWidget(self._create_page_media());       self._page_indices["media"] = idx; idx += 1
        if self.caps.get("share", True):
            self.stacked.addWidget(self._create_page_share());   self._page_indices["share"] = idx; idx += 1
        if self.caps.get("reactions", True) or self.caps.get("tags", True) or self.caps.get("sim_action", True):
            self.stacked.addWidget(self._create_page_engagement()); self._page_indices["engagement"] = idx; idx += 1

        # Post-build: hide music widgets if platform doesn't support music
        # (these widgets are created in _create_page_media, so we filter after build)
        if not self.caps.get("music", True):
            try:
                self.chk_has_music.setVisible(False)
                self.music_name_widget.setVisible(False)
                self.music_url_widget.setVisible(False)
            except Exception as e:
                try:
                    from helpers import log_error
                    log_error("PublicationDialog._hide_music_widgets", e)
                except Exception:
                    pass
        
        self.sidebar.currentRowChanged.connect(self.stacked.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        # Connect signals for UI updates
        self.rb_share.toggled.connect(self.update_type_ui)
        self.rb_link.toggled.connect(self.update_type_ui)
        self.rb_text.toggled.connect(self.update_type_ui)
        self.rb_photo.toggled.connect(self.update_type_ui)
        self.rb_video.toggled.connect(self.update_type_ui)
        self.i_share_type.currentIndexChanged.connect(self.update_type_ui)
        self.chk_share_is_group.stateChanged.connect(self.update_share_group_ui)
        self.chk_is_group.stateChanged.connect(self.update_group_ui)

        # Populate with data if editing
        if pub_data:
            self._populate_data(pub_data)
        else:
            self.update_type_ui()
            
    def _create_scrollable_page(self, title):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel(title)
        header.setProperty("class", "section-header")
        lay.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_lay = QFormLayout(content)
        content_lay.setContentsMargins(5, 5, 15, 15)
        content_lay.setSpacing(12)
        scroll.setWidget(content)
        lay.addWidget(scroll)
        
        return page, content_lay

    def _init_attributes(self):
        # General
        self.rb_text = QRadioButton("📝 Texte")
        self.rb_photo = QRadioButton("📷 Image")
        self.rb_video = QRadioButton("🎥 Vidéo")
        self.rb_share = QRadioButton("🔄 Partage")
        self.rb_link = QRadioButton("🔗 Lien")
        self.rb_text.setChecked(True)
        
        self.i_text_preview = QLineEdit()
        self.i_text_preview.setReadOnly(True)
        self.i_text_preview.setPlaceholderText("Cliquez sur Éditer...")
        
        self.i_audience = QComboBox()
        self.i_audience.addItems(["Public", "Amis", "Amis de mes amis", "Sponsorisé", "Privé"])
        self.i_time = QLineEdit()
        self.i_time.setPlaceholderText("Ex: 2h")
        
        # Identity
        self.i_prof_name = QLineEdit()
        self.i_prof_name.setPlaceholderText("Laissez vide pour utiliser la cible")
        self.chk_verified = QCheckBox("✓ Vérifié")
        self.chk_verified.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.chk_has_story = QCheckBox("Story (Bleu)")
        self.chk_is_online = QCheckBox("En ligne (Vert)")
        self.i_prof_pic = QLineEdit()
        self.i_prof_pic.setPlaceholderText("URL ou Parcourir...")
        
        self.chk_use_status = QCheckBox("Phrase personnalisée")
        self.i_status = QLineEdit()
        self.i_status.setPlaceholderText("... a changé sa photo de profil")
        self.i_status.setVisible(False)
        self.chk_use_status.toggled.connect(self.i_status.setVisible)
        
        self.chk_show_subscribe = QCheckBox("Afficher bouton S'abonner")
        self.chk_show_subscribe.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.i_subscribe_text = QLineEdit()
        self.i_subscribe_text.setPlaceholderText("Ex: S'abonner")
        self.i_subscribe_text.setText("S'abonner")
        self.i_subscribe_text.setEnabled(False)
        self.chk_show_subscribe.toggled.connect(self.i_subscribe_text.setEnabled)
        self.chk_is_group = QCheckBox("Publier dans un groupe")
        
        self.group_widget = QWidget()
        group_flay = QFormLayout(self.group_widget)
        group_flay.setContentsMargins(0,0,0,0)
        self.i_group_name = QLineEdit()
        self.i_group_name.setPlaceholderText("Ex: Les passionnés de pêche")
        self.i_group_pic = QLineEdit()
        self.i_group_pic.setPlaceholderText("URL de l'image du groupe ou parcourir...")
        self.chk_show_join = QCheckBox("Afficher bouton Rejoindre")
        self.chk_show_join.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.i_join_text = QLineEdit()
        self.i_join_text.setPlaceholderText("Ex: Rejoindre")
        self.i_join_text.setText("Rejoindre")
        self.i_join_text.setEnabled(False)
        self.chk_show_join.toggled.connect(self.i_join_text.setEnabled)
        group_flay.addRow("Nom du groupe:", self.i_group_name)
        
        gp_row = QHBoxLayout()
        gp_row.addWidget(self.i_group_pic)
        btn_g = BounceButton("📂 Parcourir")
        btn_g.setFixedHeight(34)
        btn_g.setMinimumWidth(110)
        from theme import btn_style_accent as _bsa_g
        btn_g.setStyleSheet(_bsa_g())
        btn_g.clicked.connect(self.select_group_pic)
        gp_row.addWidget(btn_g)
        group_flay.addRow("Photo groupe:", gp_row)
        join_row = QHBoxLayout()
        join_row.addWidget(self.chk_show_join)
        join_row.addWidget(self.i_join_text)
        group_flay.addRow("Bouton :", join_row)
        self.group_widget.setVisible(False)
        
        # Media
        self.i_image = QLineEdit()
        self.btn_browse_pub_img = BounceButton("📷 Image")
        self.btn_browse_pub_img.setFixedHeight(34)
        self.btn_browse_pub_img.setMinimumWidth(90)
        self.btn_browse_pub_img.clicked.connect(self.select_image)
        self.btn_browse_pub_vid = BounceButton("🎥 Vidéo")
        self.btn_browse_pub_vid.setFixedHeight(34)
        self.btn_browse_pub_vid.setMinimumWidth(90)
        self.btn_browse_pub_vid.clicked.connect(self.select_video)
        
        self.chk_has_music = QCheckBox("🎵 Musique de fond")
        self.chk_has_music.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.i_music_name = QLineEdit()
        self.i_music_name.setPlaceholderText("Ex: Artiste - Titre")
        self.i_music_url = QLineEdit()
        self.i_music_url.setPlaceholderText("URL audio optionnelle ou parcourir...")
        
        self.chk_fake_video = QCheckBox("🎭 Fausse vidéo (image + bouton lecture)")
        self.i_video_resolutions = QLineEdit()
        self.i_video_resolutions.setText("720p, 480p, 360p")
        self.i_video_cover = QLineEdit()
        self.i_video_cover.setPlaceholderText("URL de la miniature")
        
        self.i_link_domain = QLineEdit()
        self.i_link_domain.setPlaceholderText("Ex: YOUTUBE.COM")
        self.i_link_title = QLineEdit()
        self.i_link_title.setPlaceholderText("Ex: Regardez cette vidéo incroyable")
        
        self.color_inner_group = QWidget()
        
        # Share
        self.i_share_type = QComboBox()
        self.i_share_type.addItems(["Texte seul", "Image", "Vidéo", "Lien"])
        self.i_share_title = QLineEdit()
        self.i_share_title.setPlaceholderText("Ex: Jean Dupont")
        self.chk_share_verified = QCheckBox("Vérifié")
        self.chk_share_has_story = QCheckBox("Story")
        self.chk_share_is_online = QCheckBox("En ligne (Vert)")
        self.chk_share_is_group = QCheckBox("Dans un groupe")
        self.share_group_widget = QWidget()
        self.i_share_group_name = QLineEdit()
        self.i_share_group_name.setPlaceholderText("Ex: Les fans de tech")
        self.i_share_group_pic = QLineEdit()
        self.i_share_group_pic.setPlaceholderText("URL de l'image du groupe")
        self.i_share_time = QLineEdit()
        self.i_share_time.setPlaceholderText("Ex: 5 h")
        self.i_share_audience = QComboBox()
        self.i_share_audience.addItems(["Public", "Amis", "Amis de mes amis", "Sponsorisé", "Privé"])
        self.i_share_pic = QLineEdit()
        self.i_share_pic.setPlaceholderText("URL photo de l'auteur partagé")
        self.i_share_desc_preview = QLineEdit()
        self.i_share_desc_preview.setReadOnly(True)
        self.chk_share_use_status = QCheckBox("Statut partagé")
        self.i_share_status = QLineEdit()
        self.i_share_status.setPlaceholderText("Ex: a publié une nouvelle vidéo.")
        self.i_share_status.setVisible(False)
        self.chk_share_use_status.toggled.connect(self.i_share_status.setVisible)
        self.chk_share_use_tags = QCheckBox("Tags partagés")
        self.i_share_tags = QLineEdit()
        self.i_share_tags.setPlaceholderText("Ex: Paul, Marie")
        self.i_share_tags.setVisible(False)
        self.i_share_tags_count = QLineEdit()
        self.i_share_tags_count.setPlaceholderText("Ex: 2")
        self.i_share_tags_count.setVisible(False)
        self.chk_share_use_tags.toggled.connect(self.i_share_tags.setVisible)
        self.chk_share_use_tags.toggled.connect(self.i_share_tags_count.setVisible)

        # Share author: subscribe/join buttons (customizable text)
        self.chk_share_show_subscribe = QCheckBox("S'abonner (auteur partagé)")
        self.chk_share_show_subscribe.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.i_share_subscribe_text = QLineEdit()
        self.i_share_subscribe_text.setPlaceholderText("Ex: S'abonner")
        self.i_share_subscribe_text.setText("S'abonner")
        self.i_share_subscribe_text.setEnabled(False)
        self.chk_share_show_subscribe.toggled.connect(self.i_share_subscribe_text.setEnabled)

        self.chk_share_show_join = QCheckBox("Rejoindre (groupe partagé)")
        self.chk_share_show_join.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.i_share_join_text = QLineEdit()
        self.i_share_join_text.setPlaceholderText("Ex: Rejoindre")
        self.i_share_join_text.setText("Rejoindre")
        self.i_share_join_text.setEnabled(False)
        self.chk_share_show_join.toggled.connect(self.i_share_join_text.setEnabled)


        # Engagement
        self.i_reactions = QLineEdit()
        self.i_likes_count = QLineEdit()
        self.i_likes_count.setPlaceholderText("Ex: 124")
        self.i_comments_count = QLineEdit()
        self.i_comments_count.setPlaceholderText("Ex: 45")
        self.i_shares_count = QLineEdit()
        self.i_shares_count.setPlaceholderText("Ex: 12")
        self.chk_sim_action = QCheckBox("Activer l'action fictive")
        self.i_sim_reaction = QComboBox()
        self.i_sim_reaction.addItems(["J'aime", "J'adore", "Solidaire", "Haha", "Wouah", "Triste", "En colère"])
        self.i_sim_reaction.setVisible(False)
        self.chk_sim_action.toggled.connect(self.i_sim_reaction.setVisible)
        self.chk_use_tags = QCheckBox("Tags")
        self.i_tags = QLineEdit()
        self.i_tags.setPlaceholderText("Ex: Paul, Marie")
        self.i_tags.setVisible(False)
        self.i_tags_count = QLineEdit()
        self.i_tags_count.setPlaceholderText("Ex: 3")
        self.i_tags_count.setVisible(False)
        self.chk_use_tags.toggled.connect(self.i_tags.setVisible)
        self.chk_use_tags.toggled.connect(self.i_tags_count.setVisible)
        self.chk_use_private = QCheckBox("Audience Privée")
        self.i_private_count = QLineEdit()
        self.i_private_count.setPlaceholderText("Ex: 4")
        self.i_private_count.setVisible(False)
        self.chk_use_private.toggled.connect(self.i_private_count.setVisible)

        # Blur / sensitive content
        self.chk_blur = QCheckBox("🫣 Contenu flou (masqué)")
        self.chk_blur.setStyleSheet(f"color: {self._t_chk['warning']}; font-weight: bold;")
        self.i_blur_reason = QLineEdit()
        self.i_blur_reason.setPlaceholderText("Ex: Contenu sensible · Nudité · Violences...")
        self.i_blur_reason.setEnabled(False)
        self.chk_blur.toggled.connect(self.i_blur_reason.setEnabled)
        self.cmb_blur_mode = QComboBox()
        self.cmb_blur_mode.addItem("Immédiat (flou direct)", "instant")
        self.cmb_blur_mode.addItem("Après lecture (son d'abord, puis flou)", "delayed")
        self.cmb_blur_mode.setEnabled(False)
        self.chk_blur.toggled.connect(self.cmb_blur_mode.setEnabled)
        self.i_blur_delay = QLineEdit()
        self.i_blur_delay.setPlaceholderText("ex: 3")
        self.i_blur_delay.setText("3")
        self.i_blur_delay.setMaximumWidth(80)
        self.i_blur_delay.setEnabled(False)
        self.chk_blur.toggled.connect(self.i_blur_delay.setEnabled)
        self.cmb_blur_mode.currentIndexChanged.connect(self._on_blur_mode_changed)

        # Sound enabled for video publications
        self.chk_sound = QCheckBox("🔊 Activer le son de la vidéo")
        self.chk_sound.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.chk_sound.setChecked(True)
        self.chk_sound.setToolTip("Si activé, le son de la vidéo sera joué dès que possible.\n"
                                   "Si désactivé, la vidéo restera muette.")

    def _on_blur_mode_changed(self):
        try:
            is_delayed = self.cmb_blur_mode.currentData() == "delayed"
            self.i_blur_delay.setEnabled(is_delayed and self.chk_blur.isChecked())
            if hasattr(self, '_blur_delay_label') and self._blur_delay_label:
                self._blur_delay_label.setVisible(is_delayed)
            self.i_blur_delay.setVisible(is_delayed)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("PublicationDialog._on_blur_mode_changed", e)
            except Exception:
                pass

    def _apply_theme_style(self):
        """Build and apply the dialog stylesheet using the current theme colors.
        Called at __init__ and again by refresh_theme() when the theme changes."""
        try:
            t = self._t_chk
            self.setStyleSheet(f'''
                QDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
                QWidget#sidebar {{ background-color: {t['bg_alt']}; border-right: 1px solid {t['border']}; }}
                QListWidget {{ background-color: transparent; border: none; outline: none; }}
                QListWidget::item {{ color: {t['text_dim']}; padding: 12px 15px; font-weight: bold; font-size: 13px; border-radius: 6px; margin: 4px 8px; }}
                QListWidget::item:hover {{ background-color: {t['border']}; color: {t['text']}; }}
                QListWidget::item:selected {{ background-color: {t['accent']}; color: white; }}

                QStackedWidget {{ background-color: {t['bg']}; }}

                /* Section Headers */
                QLabel.section-header {{ color: {t['text']}; font-size: 16px; font-weight: bold; padding-bottom: 8px; border-bottom: 1px solid {t['border']}; margin-bottom: 10px; }}

                QLabel {{ color: {t['text']}; font-size: 12px; font-weight: 500; }}
                QLineEdit, QComboBox {{
                    background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; padding: 8px 10px;
                    border-radius: 6px; color: {t['text']}; font-size: 12px;
                }}
                QLineEdit:focus, QComboBox:focus {{ border: 1px solid {t['accent']}; background-color: {t['bg']}; }}

                QCheckBox, QRadioButton {{ spacing: 6px; color: {t['text']}; font-size: 12px; font-weight: 500; }}
                QCheckBox::indicator, QRadioButton::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 2px solid {t['border_hover']}; background-color: {t['bg_alt']}; }}
                QRadioButton::indicator {{ border-radius: 9px; }}
                QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ background-color: {t['accent']}; border: 2px solid {t['accent']}; }}

                QScrollArea {{ border: none; background-color: transparent; }}
                QScrollBar:vertical {{ border: none; background: {t['bg']}; width: 8px; margin: 0; }}
                QScrollBar::handle:vertical {{ background: {t['border_hover']}; min-height: 20px; border-radius: 4px; }}
                QScrollBar::handle:vertical:hover {{ background: {t['accent']}; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; }}

                QPushButton {{ background-color: {t['bg_alt']}; color: {t['text']}; border: 1px solid {t['border_hover']}; border-radius: 6px; padding: 8px 14px; font-weight: normal; }}
                QPushButton:hover {{ background-color: {t['border_hover']}; border-color: {t['accent']}; color: {t['accent_text']}; }}
                QPushButton:pressed {{ background-color: {t['border']}; }}

                QGroupBox {{ background-color: {t['bg_alt']}; border: 1px solid {t['border']}; border-radius: 10px; margin-top: 14px; padding: 18px 14px 14px 14px; font-weight: bold; font-size: 13px; color: {t['text_dim']}; }}
                QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 2px 10px; color: {t['accent']}; }}

                QTextEdit {{ background-color: {t['bg_input']}; border: 1px solid {t['border']}; border-radius: 6px; color: {t['text']}; padding: 8px; }}
            ''')
        except Exception as e:
            try:
                from helpers import log_error
                log_error("PublicationDialog._apply_theme_style", e)
            except Exception:
                pass

    def _create_page_general(self):
        page, lay = self._create_scrollable_page("📌 Informations Générales")
        
        # Type radio buttons — only add the ones supported by this platform
        t_row = QHBoxLayout()
        t_row.addWidget(self.rb_text)
        if self.caps.get("video", True) or self.caps.get("publications", True):
            t_row.addWidget(self.rb_photo)
        if self.caps.get("video", True):
            t_row.addWidget(self.rb_video)
        if self.caps.get("share", True):
            t_row.addWidget(self.rb_share)
        if self.caps.get("links", True):
            t_row.addWidget(self.rb_link)
        t_row.addStretch()
        lay.addRow("Type :", t_row)
        
        t_lay = QHBoxLayout()
        t_lay.addWidget(self.i_text_preview)
        btn_edit = BounceButton("✏️ Éditer Texte")
        from theme import btn_style_accent as _bsa_edit
        btn_edit.setStyleSheet(_bsa_edit())
        btn_edit.clicked.connect(self.open_text_editor)
        t_lay.addWidget(btn_edit)
        lay.addRow("Texte / Légende :", t_lay)
        
        o_row = QHBoxLayout()
        o_row.addWidget(self.i_audience)
        o_row.addWidget(QLabel("Date/Heure:"))
        o_row.addWidget(self.i_time)
        lay.addRow("Audience :", o_row)
        
        return page

    def _create_page_identity(self):
        page, lay = self._create_scrollable_page("👤 Auteur & Identité")
        lay.addRow("Nom :", self.i_prof_name)
        
        # Badges — only show story/online if the platform supports them
        badge_row = QHBoxLayout()
        badge_row.addWidget(self.chk_verified)
        if self.caps.get("stories", True):
            badge_row.addWidget(self.chk_has_story)
        badge_row.addWidget(self.chk_is_online)
        badge_row.addStretch()
        lay.addRow("Badges :", badge_row)
        
        pic_row = QHBoxLayout()
        pic_row.addWidget(self.i_prof_pic)
        btn_p = BounceButton("📂 Parcourir")
        btn_p.setFixedHeight(34)
        btn_p.setMinimumWidth(110)
        from theme import btn_style_accent as _bsa_p
        btn_p.setStyleSheet(_bsa_p())
        btn_p.clicked.connect(self.select_profile_pic_pub)
        pic_row.addWidget(btn_p)
        lay.addRow("Photo :", pic_row)
        
        status_row = QHBoxLayout()
        status_row.addWidget(self.chk_use_status)
        status_row.addWidget(self.i_status)
        lay.addRow("Statut :", status_row)

        # Subscribe button — only if platform supports it (follow_label is non-empty)
        if self.caps.get("follow_label", ""):
            sub_row = QHBoxLayout()
            sub_row.addWidget(self.chk_show_subscribe)
            sub_row.addWidget(self.i_subscribe_text)
            lay.addRow("S'abonner :", sub_row)

        # Groups — only if platform supports groups
        if self.caps.get("groups", True):
            opt_row = QHBoxLayout()
            opt_row.addWidget(self.chk_is_group)
            opt_row.addStretch()
            lay.addRow("", opt_row)
            lay.addRow("", self.group_widget)
        
        return page

    def _create_page_media(self):
        page, lay = self._create_scrollable_page("🖼️ Média & Contenu Dynamique")
        
        self.media_group_widget = QWidget()
        self.media_group_layout = QVBoxLayout(self.media_group_widget)
        self.media_group_layout.setContentsMargins(0,0,0,0)
        
        self.main_media_container = QWidget()
        self.main_media_layout = QVBoxLayout(self.main_media_container)
        self.main_media_layout.setContentsMargins(0,0,0,0)
        lay.addRow(self.main_media_container)
        
        self.main_media_layout.addWidget(self.media_group_widget)
        
        # Image / Video source
        self.image_widget = QWidget()
        ilay = QFormLayout(self.image_widget)
        ilay.setContentsMargins(0,0,0,0)
        
        mi_row = QHBoxLayout()
        mi_row.addWidget(self.i_image)
        from theme import btn_style_accent as _bsa_img
        self.btn_browse_pub_img.setStyleSheet(_bsa_img())
        from theme import btn_style_accent as _bsa_vid
        self.btn_browse_pub_vid.setStyleSheet(_bsa_vid())
        mi_row.addWidget(self.btn_browse_pub_img)
        mi_row.addWidget(self.btn_browse_pub_vid)
        ilay.addRow("Source :", mi_row)

        # ── Galerie d'images supplémentaires (carousel) ──
        self._extra_images = []
        self._extra_thumbs = []
        self.extra_images_widget = QWidget()
        extra_lay = QVBoxLayout(self.extra_images_widget)
        extra_lay.setContentsMargins(0, 0, 0, 0)
        extra_lay.setSpacing(6)
        # Label
        self._extra_section_lbl = QLabel("🖼️ Images supplémentaires (carousel)")
        self._extra_section_lbl.setStyleSheet(f"color: {self._t_chk.get('text_dim', '#888')}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 6px;")
        extra_lay.addWidget(self._extra_section_lbl)
        # Liste avec drag-drop natif
        self._extra_list = QListWidget()
        self._extra_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._extra_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._extra_list.setDragEnabled(True)
        self._extra_list.setAcceptDrops(True)
        self._extra_list.setDropIndicatorShown(True)
        self._extra_list.setAutoScroll(True)
        self._extra_list.setAutoScrollMargin(50)
        self._extra_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._extra_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._extra_list.setFrameShape(QFrame.Shape.StyledPanel)
        self._extra_list.setMinimumHeight(120)
        self._extra_list.setMaximumHeight(350)
        self._extra_list.setSpacing(2)
        # Activer le scroll pendant le drag via un timer
        self._extra_scroll_timer = None
        self._extra_list.setMouseTracking(True)
        # Connecter le dropEvent pour resynchroniser après drag-drop
        self._extra_list.dropEvent = self._extra_drop_event
        # Connecter dragEnterEvent et dragMoveEvent pour le scroll automatique
        self._extra_list.dragEnterEvent = self._extra_drag_enter
        self._extra_list.dragMoveEvent = self._extra_drag_move
        extra_lay.addWidget(self._extra_list)
        # Boutons ajouter / tout effacer
        extra_btn_row = QHBoxLayout()
        extra_btn_row.setSpacing(6)
        self.btn_add_extra = BounceButton("➕ Ajouter image")
        self.btn_add_extra.setFixedHeight(30)
        self.btn_add_extra.clicked.connect(self.add_extra_image)
        extra_btn_row.addWidget(self.btn_add_extra)
        self.btn_clear_extra = BounceButton("🗑️ Tout effacer")
        self.btn_clear_extra.setFixedHeight(30)
        self.btn_clear_extra.clicked.connect(self.clear_extra_images)
        extra_btn_row.addWidget(self.btn_clear_extra)
        extra_btn_row.addStretch()
        extra_btn_w = QWidget(); extra_btn_w.setLayout(extra_btn_row)
        extra_lay.addWidget(extra_btn_w)
        ilay.addRow("", self.extra_images_widget)

        self.media_group_layout.addWidget(self.image_widget)
        
        # Music Options
        self.music_options_widget = QWidget()
        mlay = QFormLayout(self.music_options_widget)
        mlay.setContentsMargins(0,0,0,0)
        mlay.addRow("", self.chk_has_music)
        self.music_name_widget = QWidget()
        mnlay = QHBoxLayout(self.music_name_widget)
        mnlay.setContentsMargins(0,0,0,0)
        mnlay.addWidget(self.i_music_name)
        self.music_name_widget.setEnabled(False)
        mlay.addRow("Titre :", self.music_name_widget)
        
        mu_row = QHBoxLayout()
        mu_row.addWidget(self.i_music_url)
        btn_mu = BounceButton("📂 Parcourir")
        btn_mu.setFixedHeight(34)
        btn_mu.setMinimumWidth(110)
        from theme import btn_style_accent as _bsa_mu
        btn_mu.setStyleSheet(_bsa_mu())
        btn_mu.clicked.connect(self.select_music)
        mu_row.addWidget(btn_mu)

        self.music_url_widget = QWidget()
        mulay = QHBoxLayout(self.music_url_widget)
        mulay.setContentsMargins(0,0,0,0)
        mulay.addLayout(mu_row)
        self.music_url_widget.setEnabled(False)
        mlay.addRow("Audio :", self.music_url_widget)

        # Hidden music option — music plays on first click but is not shown in the feed
        self.chk_music_hidden = QCheckBox("🕵️ Cacher la musique (joue au clic)")
        self.chk_music_hidden.setStyleSheet(f"color: {self._t_chk['accent_text']}; font-weight: bold;")
        self.chk_music_hidden.setToolTip("Si activé, la musique n'est pas visible dans le feed\n"
                                          "mais elle se joue automatiquement quand la victime\n"
                                          "clique n'importe où sur la page.")
        self.chk_music_hidden.setEnabled(False)
        mlay.addRow("", self.chk_music_hidden)

        self.chk_has_music.toggled.connect(self.music_name_widget.setEnabled)
        self.chk_has_music.toggled.connect(self.music_url_widget.setEnabled)
        self.chk_has_music.toggled.connect(self.chk_music_hidden.setEnabled)
        # Only add music options to layout if platform supports music
        if self.caps.get("music", True):
            self.media_group_layout.addWidget(self.music_options_widget)
            lay.addRow(self.music_options_widget)
        else:
            self.music_options_widget.setVisible(False)
        
        # Link Options — only if platform supports links
        self.link_widget = QWidget()
        llay = QFormLayout(self.link_widget)
        llay.setContentsMargins(0,0,0,0)
        llay.addRow("Domaine :", self.i_link_domain)
        llay.addRow("Titre :", self.i_link_title)
        if self.caps.get("links", True):
            self.media_group_layout.addWidget(self.link_widget)
        else:
            self.link_widget.setVisible(False)
        
        # Video Options
        self.video_options_widget = QWidget()
        vlay = QFormLayout(self.video_options_widget)
        vlay.setContentsMargins(0,0,0,0)
        vlay.addRow("", self.chk_fake_video)
        vlay.addRow("", self.chk_sound)

        self.chk_fake_video.toggled.connect(self._on_fake_video_toggled)
        self.chk_fake_video.toggled.connect(self.update_type_ui)
        
        vc_row = QHBoxLayout()
        vc_row.addWidget(self.i_video_cover)
        btn_vc = BounceButton("📂 Parcourir")
        btn_vc.setFixedHeight(34)
        btn_vc.setMinimumWidth(110)
        from theme import btn_style_accent as _bsa_vc
        btn_vc.setStyleSheet(_bsa_vc())
        btn_vc.clicked.connect(self.select_video_cover)
        vc_row.addWidget(btn_vc)
        
        self.video_real_options = QWidget()
        vrlay = QFormLayout(self.video_real_options)
        vrlay.setContentsMargins(0,0,0,0)
        vrlay.addRow("Couverture:", vc_row)
        vrlay.addRow("Qualité:", self.i_video_resolutions)
        vlay.addRow(self.video_real_options)
        self.media_group_layout.addWidget(self.video_options_widget)
        
        # Color Background Grid
        color_lay = QFormLayout(self.color_inner_group)
        color_lay.setContentsMargins(0,0,0,0)
        
        cbtn_row = QHBoxLayout()
        btn_c_add = BounceButton("➕ Personnaliser")
        from theme import btn_style_accent as _bsa_cadd
        btn_c_add.setStyleSheet(_bsa_cadd())
        btn_c_add.clicked.connect(self.add_custom_bg_dialog)
        cbtn_row.addWidget(QLabel("Fond coloré :"))
        cbtn_row.addStretch()
        cbtn_row.addWidget(btn_c_add)
        color_lay.addRow(cbtn_row)
        
        self.color_grid_widget = QWidget()
        self.color_grid_layout = QGridLayout(self.color_grid_widget)
        color_lay.addRow(self.color_grid_widget)
        
        self.refresh_color_grid()
        lay.addRow(self.color_inner_group)
        
        return page

    def _create_page_share(self):
        page, lay = self._create_scrollable_page("🔄 Post Partagé")
        
        self.share_widget = QWidget()
        slay = QFormLayout(self.share_widget)
        slay.setContentsMargins(0,0,0,0)
        
        slay.addRow("Type post partagé :", self.i_share_type)
        
        self.share_media_container = QWidget()
        self.share_media_layout = QVBoxLayout(self.share_media_container)
        self.share_media_layout.setContentsMargins(0,0,0,0)
        slay.addRow("Média du partage :", self.share_media_container)
        
        slay.addRow("Auteur d'origine :", self.i_share_title)
        
        sbadge_row = QHBoxLayout()
        sbadge_row.addWidget(self.chk_share_verified)
        if self.caps.get("stories", True):
            sbadge_row.addWidget(self.chk_share_has_story)
        sbadge_row.addWidget(self.chk_share_is_online)
        if self.caps.get("groups", True):
            sbadge_row.addWidget(self.chk_share_is_group)
        sbadge_row.addStretch()
        slay.addRow("Badges :", sbadge_row)
        
        # Group fields — only if platform supports groups
        if self.caps.get("groups", True):
            sg_lay = QFormLayout(self.share_group_widget)
            sg_lay.setContentsMargins(0,0,0,0)
            sg_lay.addRow("Nom Groupe :", self.i_share_group_name)
            sgp_row = QHBoxLayout()
            sgp_row.addWidget(self.i_share_group_pic)
            btn_sgp = BounceButton("📂 Parcourir")
            btn_sgp.setFixedHeight(34)
            btn_sgp.setMinimumWidth(110)
            from theme import btn_style_accent as _bsa_sgp
            btn_sgp.setStyleSheet(_bsa_sgp())
            btn_sgp.clicked.connect(self.select_share_group_pic)
            sgp_row.addWidget(btn_sgp)
            sg_lay.addRow("Photo Groupe :", sgp_row)
            slay.addRow(self.share_group_widget)
            self.share_group_widget.setVisible(False)
        
        so_row = QHBoxLayout()
        so_row.addWidget(self.i_share_audience)
        so_row.addWidget(QLabel("Temps :"))
        so_row.addWidget(self.i_share_time)
        slay.addRow("Audience :", so_row)
        
        spic_row = QHBoxLayout()
        spic_row.addWidget(self.i_share_pic)
        btn_sp = BounceButton("📂 Parcourir")
        btn_sp.setFixedHeight(34)
        btn_sp.setMinimumWidth(110)
        from theme import btn_style_accent as _bsa_sp
        btn_sp.setStyleSheet(_bsa_sp())
        btn_sp.clicked.connect(self.select_share_pic)
        spic_row.addWidget(btn_sp)
        slay.addRow("Photo d'origine :", spic_row)
        
        st_row = QHBoxLayout()
        st_row.addWidget(self.i_share_desc_preview)
        btn_st = BounceButton("✏️ Éditer")
        btn_st.setFixedHeight(34)
        btn_st.setMinimumWidth(100)
        from theme import btn_style_accent as _bsa_st
        btn_st.setStyleSheet(_bsa_st())
        btn_st.clicked.connect(self.open_share_text_editor)
        st_row.addWidget(btn_st)
        slay.addRow("Texte d'origine :", st_row)
        
        sst_row = QHBoxLayout()
        sst_row.addWidget(self.chk_share_use_status)
        sst_row.addWidget(self.i_share_status)
        slay.addRow("Statut :", sst_row)
        
        # Share Tags — only if platform supports tags
        if self.caps.get("tags", True):
            stag_row = QHBoxLayout()
            stag_row.addWidget(self.chk_share_use_tags)
            stag_row.addWidget(self.i_share_tags)
            stag_row.addWidget(self.i_share_tags_count)
            slay.addRow("Tags :", stag_row)

        # Share Subscribe — only if platform has follow_label
        if self.caps.get("follow_label", ""):
            ssub_row = QHBoxLayout()
            ssub_row.addWidget(self.chk_share_show_subscribe)
            ssub_row.addWidget(self.i_share_subscribe_text)
            slay.addRow("S'abonner :", ssub_row)

        sjoin_row = QHBoxLayout()
        sjoin_row.addWidget(self.chk_share_show_join)
        sjoin_row.addWidget(self.i_share_join_text)
        slay.addRow("Rejoindre :", sjoin_row)

        lay.addRow(self.share_widget)
        return page

    def _create_page_engagement(self):
        page, lay = self._create_scrollable_page("❤️ Engagement & Statistiques")
        
        # Tags — only if platform supports tags
        if self.caps.get("tags", True):
            tag_row = QHBoxLayout()
            tag_row.addWidget(self.chk_use_tags)
            tag_row.addWidget(self.i_tags)
            tag_row.addWidget(self.i_tags_count)
            lay.addRow("Tags :", tag_row)
        
        # Audience Privée — only if platform supports it (Facebook-like feature)
        if self.caps.get("tags", True) and self.caps.get("groups", True):
            priv_row = QHBoxLayout()
            priv_row.addWidget(self.chk_use_private)
            priv_row.addWidget(self.i_private_count)
            lay.addRow("Audience Privée :", priv_row)
        
        # Contenu flou — only if platform supports blur
        if self.caps.get("blur", True):
            blur_row = QHBoxLayout()
            blur_row.addWidget(self.chk_blur)
            blur_row.addWidget(self.i_blur_reason)
            lay.addRow("Contenu flou :", blur_row)
            lay.addRow("Mode flou :", self.cmb_blur_mode)
            self._blur_delay_label = QLabel("Délai (s) :")
            lay.addRow(self._blur_delay_label, self.i_blur_delay)
        
        # Statistiques — always show (likes/comments/shares are universal)
        counts_row = QHBoxLayout()
        if self.caps.get("reactions", True):
            counts_row.addWidget(QLabel("👍 Likes:"))
            counts_row.addWidget(self.i_likes_count)
        counts_row.addWidget(QLabel("💬 Coms:"))
        counts_row.addWidget(self.i_comments_count)
        if self.caps.get("share", True):
            counts_row.addWidget(QLabel("🔁 Partages:"))
            counts_row.addWidget(self.i_shares_count)
        lay.addRow("Statistiques :", counts_row)
        
        # Action Fictive — only if platform supports sim_action
        if self.caps.get("sim_action", True):
            sim_row = QHBoxLayout()
            sim_row.addWidget(self.chk_sim_action)
            sim_row.addWidget(self.i_sim_reaction)
            sim_row.addStretch()
            lay.addRow("Action Fictive :", sim_row)
        
        # Reactions Section — only if platform supports reactions
        if self.caps.get("reactions", True):
            lbl = QLabel("Réactions :")
            lbl.setStyleSheet("font-weight: bold; margin-top: 10px;")
            lay.addRow(lbl)
            
            self.i_reactions.setPlaceholderText("Ex: Like,Love,Haha")
            btn_clear = BounceButton("🗑️ Effacer")
            from theme import btn_style_danger as _bsd_clear
            btn_clear.setStyleSheet(_bsd_clear())
            btn_clear.clicked.connect(self.i_reactions.clear)
            
            r_row = QHBoxLayout()
            r_row.addWidget(self.i_reactions)
            r_row.addWidget(btn_clear)
            lay.addRow(r_row)
            
            grid = QGridLayout()
            import templates
            # Use platform-specific reactions map if available
            try:
                from platforms import get_reactions_map_for, get_capabilities_by_id
                platform_reactions = get_reactions_map_for({"platform": self.platform})
                allowed_reaction_types = set(get_capabilities_by_id(self.platform).get("reaction_types", []))
            except Exception:
                platform_reactions = templates.REACTIONS_MAP
                allowed_reaction_types = set()
            # If allowed_reaction_types is empty, show all (backward compat for Facebook)
            reactions_to_show = platform_reactions if platform_reactions else templates.REACTIONS_MAP
            row, col = 0, 0
            for name, info in reactions_to_show.items():
                # Skip reactions not in the platform's allowed list (if list is non-empty)
                if allowed_reaction_types and name not in allowed_reaction_types:
                    continue
                btn = BounceButton(name)
                color = info.get("color", "#3b82f6")
                # Lighten the color on hover by using rgba overlay
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color}; color: white;
                        border: none; border-radius: 6px;
                        padding: 8px 12px; font-weight: bold; font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {color}; border: 1px solid #FFFFFF;
                    }}
                    QPushButton:pressed {{
                        background-color: {color}; border: 2px solid #FFFFFF;
                        padding: 7px 11px;
                    }}
                """)
                btn.clicked.connect(lambda checked, n=name: self.add_reaction(n))
                grid.addWidget(btn, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
            lay.addRow(grid)
        
        return page

    def _populate_data(self, pub_data):
        try:
            ptype = pub_data.get("type", "text")
            if ptype == "photo" or ptype == "image": self.rb_photo.setChecked(True)
            elif ptype == "video": self.rb_video.setChecked(True)
            elif ptype == "share": self.rb_share.setChecked(True)
            elif ptype == "link": self.rb_link.setChecked(True)
            else: self.rb_text.setChecked(True)

            self._main_text = pub_data.get("text", "")
            self.i_text_preview.setText(self._main_text.replace("<br>", " ")[:30] + "...")
            self.i_audience.setCurrentText(pub_data.get("audience", "Public"))
            self.i_time.setText(pub_data.get("time_ago", "2h"))

            self.i_prof_name.setText(pub_data.get("profile_name", ""))
            self.chk_verified.setChecked(pub_data.get("verified", False))
            self.chk_has_story.setChecked(pub_data.get("has_story", False))
            self.chk_is_online.setChecked(pub_data.get("is_online", False))
            self.i_prof_pic.setText(pub_data.get("profile_pic", ""))
            
            self.chk_use_status.setChecked(pub_data.get("use_status", False))
            self.i_status.setText(pub_data.get("status_text", ""))
            self.chk_show_subscribe.setChecked(pub_data.get("show_subscribe", False))
            self.i_subscribe_text.setText(pub_data.get("subscribe_text", "S'abonner") or "S'abonner")
            self.i_subscribe_text.setEnabled(pub_data.get("show_subscribe", False))
            
            self.chk_is_group.setChecked(pub_data.get("is_group", False))
            self.i_group_name.setText(pub_data.get("group_name", ""))
            self.i_group_pic.setText(pub_data.get("group_pic", ""))
            self.chk_show_join.setChecked(pub_data.get("show_join", False))
            self.i_join_text.setText(pub_data.get("join_text", "Rejoindre") or "Rejoindre")
            self.i_join_text.setEnabled(pub_data.get("show_join", False))
            self.update_group_ui()

            self.i_image.setText(pub_data.get("image", ""))
            self._extra_images = list(pub_data.get("extra_images", []))
            self._refresh_extra_gallery()
            self.i_link_domain.setText(pub_data.get("link_domain", ""))
            self.i_link_title.setText(pub_data.get("link_title", ""))

            has_music = pub_data.get("has_music", False)
            self.chk_has_music.setChecked(has_music)
            self.music_name_widget.setEnabled(has_music)
            self.music_url_widget.setEnabled(has_music)
            self.chk_music_hidden.setEnabled(has_music)
            self.chk_music_hidden.setChecked(pub_data.get("music_hidden", False))
            self.i_music_name.setText(pub_data.get("music_name", ""))
            self.i_music_url.setText(pub_data.get("music_url", ""))

            self.chk_fake_video.setChecked(pub_data.get("fake_video", False))
            self.chk_sound.setChecked(pub_data.get("sound_enabled", True))
            self.i_video_resolutions.setText(", ".join(pub_data.get("video_resolutions", ["720p", "480p", "360p"])))
            self.i_video_cover.setText(pub_data.get("video_cover", ""))
            self._on_fake_video_toggled(self.chk_fake_video.isChecked())

            self.i_share_type.setCurrentText(pub_data.get("share_type", "Texte seul"))
            self.i_share_title.setText(pub_data.get("share_title", ""))
            self.chk_share_verified.setChecked(pub_data.get("share_verified", False))
            self.chk_share_has_story.setChecked(pub_data.get("share_has_story", False))
            self.chk_share_is_online.setChecked(pub_data.get("share_is_online", False))
            self.chk_share_is_group.setChecked(pub_data.get("share_is_group", False))
            self.i_share_group_name.setText(pub_data.get("share_group_name", ""))
            self.i_share_group_pic.setText(pub_data.get("share_group_pic", ""))
            self.i_share_time.setText(pub_data.get("share_time_ago", ""))
            self.i_share_audience.setCurrentText(pub_data.get("share_audience", "Public"))
            self.i_share_pic.setText(pub_data.get("share_pic", pub_data.get("share_profile_pic", "")))
            
            self._share_text = pub_data.get("share_desc", "")
            self.i_share_desc_preview.setText(self._share_text.replace("<br>", " ")[:30] + "...")
            
            self.chk_share_use_status.setChecked(pub_data.get("share_use_status", False))
            self.i_share_status.setText(pub_data.get("share_status_text", pub_data.get("share_status", "")))
            self.chk_share_use_tags.setChecked(pub_data.get("share_use_tags", False))
            self.i_share_tags.setText(pub_data.get("share_tags", ""))
            self.i_share_tags_count.setText(pub_data.get("share_tags_count", "0"))

            # Share subscribe/join
            self.chk_share_show_subscribe.setChecked(pub_data.get("share_show_subscribe", False))
            self.i_share_subscribe_text.setText(pub_data.get("share_subscribe_text", "S'abonner") or "S'abonner")
            self.i_share_subscribe_text.setEnabled(pub_data.get("share_show_subscribe", False))
            self.chk_share_show_join.setChecked(pub_data.get("share_show_join", False))
            self.i_share_join_text.setText(pub_data.get("share_join_text", "Rejoindre") or "Rejoindre")
            self.i_share_join_text.setEnabled(pub_data.get("share_show_join", False))

            self.update_share_group_ui()

            reactions_data = pub_data.get("reactions", [])
            if isinstance(reactions_data, str):
                self.i_reactions.setText(reactions_data)
            else:
                self.i_reactions.setText(",".join([r.get("name", "") if isinstance(r, dict) else str(r) for r in reactions_data]))
            
            self.i_likes_count.setText(pub_data.get("likes", ""))
            self.i_comments_count.setText(pub_data.get("comments_count", ""))
            self.i_shares_count.setText(pub_data.get("shares_count", ""))
            
            sim_action = pub_data.get("sim_action", False)
            self.chk_sim_action.setChecked(sim_action)
            sim_reaction = pub_data.get("sim_reaction", "")
            if sim_reaction:
                idx = self.i_sim_reaction.findText(sim_reaction)
                if idx >= 0: self.i_sim_reaction.setCurrentIndex(idx)
            
            self.chk_use_tags.setChecked(pub_data.get("use_tags", False))
            self.i_tags.setText(pub_data.get("tag_name", ""))
            self.i_tags_count.setText(pub_data.get("tag_count", ""))
            
            self.chk_use_private.setChecked(pub_data.get("use_private", False))
            self.i_private_count.setText(pub_data.get("private_count", ""))
            
            self.chk_blur.setChecked(pub_data.get("blur_enabled", False))
            self.i_blur_reason.setText(pub_data.get("blur_reason", ""))
            self.i_blur_reason.setEnabled(pub_data.get("blur_enabled", False))
            _bm = pub_data.get("blur_mode", "instant") or "instant"
            for i in range(self.cmb_blur_mode.count()):
                if self.cmb_blur_mode.itemData(i) == _bm:
                    self.cmb_blur_mode.setCurrentIndex(i); break
            self.cmb_blur_mode.setEnabled(pub_data.get("blur_enabled", False))
            self.i_blur_delay.setText(str(pub_data.get("blur_delay", 3)))
            self._on_blur_mode_changed()
            
            self.update_type_ui()
            self.update_color_highlight()
            
        except Exception as e:
            from helpers import log_error
            log_error('widgets._populate_data', e)

    def refresh_color_grid(self):
        for i in reversed(range(self.color_grid_layout.count())): 
            w = self.color_grid_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        self.color_buttons.clear()
        
        row, col = 0, 0
        from templates import FEED_COLORS
        from config import BASE_CONFIG as default_config
        
        all_colors = FEED_COLORS + default_config["custom_backgrounds"]
        
        for c in all_colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            self.color_buttons.append((btn, c))
            btn.clicked.connect(lambda checked, color=c: self.select_color(color))
            
            if c in default_config["custom_backgrounds"]:
                btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, button=btn, color=c: self.show_bg_context_menu(button, color))
            
            self.color_grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= 10:
                col = 0
                row += 1
                
        self.update_color_highlight()
        
    def show_bg_context_menu(self, btn, color):
        menu = QMenu(self)
        act_modify = menu.addAction("✏️ Modifier")
        act_delete = menu.addAction("🗑️ Supprimer")
        
        from PyQt6.QtGui import QCursor
        from PyQt6.QtWidgets import QInputDialog, QFileDialog
        action = menu.exec(QCursor.pos())
        
        if action == act_delete:
            from config import BASE_CONFIG as default_config
            if color in default_config["custom_backgrounds"]:
                default_config["custom_backgrounds"].remove(color)
                if color == self.selected_bg:
                    self.selected_bg = "transparent"
                self.refresh_color_grid()
        
        elif action == act_modify:
            from config import BASE_CONFIG as default_config
            if color in default_config["custom_backgrounds"]:
                idx = default_config["custom_backgrounds"].index(color)
                
                # Determine type
                if color.startswith("#"):
                    text, ok = QInputDialog.getText(self, "Modifier la couleur", "Code Hex (ex: #ff00ff):", text=color)
                    if ok and text:
                        text = text.strip()
                        if not text.startswith("#"): text = "#" + text
                        default_config["custom_backgrounds"][idx] = text
                        if self.selected_bg == color:
                            self.selected_bg = text
                        self.refresh_color_grid()
                elif color.startswith("http") or color.startswith("data:image"):
                    text, ok = QInputDialog.getText(self, "Modifier l'URL", "URL de l'image:", text=color)
                    if ok and text.startswith("http"):
                        default_config["custom_backgrounds"][idx] = text
                        if self.selected_bg == color:
                            self.selected_bg = text
                        self.refresh_color_grid()
                elif color.startswith("bg_"):
                    file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un nouvel arrière-plan", "", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)")
                    if file_path:
                        try:
                            import shutil, time, os
                            from config import get_video_dir
                            video_dir = get_video_dir(self.tid)
                            os.makedirs(video_dir, exist_ok=True)
                            filename = os.path.basename(file_path)
                            safe_filename = f"bg_{int(time.time())}_{filename.replace(' ', '_')}"
                            dest_path = os.path.join(video_dir, safe_filename)
                            shutil.copy2(file_path, dest_path)
                            
                            # Update config
                            default_config["custom_backgrounds"][idx] = safe_filename
                            if self.selected_bg == color:
                                self.selected_bg = safe_filename
                                
                            self.refresh_color_grid()
                        except Exception as e:
                            try:
                                from helpers import log_error
                                log_error("PublicationDialog._handle_bg_action.replace", e)
                            except Exception:
                                pass

    def select_color(self, color):
        self.selected_bg = color
        self.update_color_highlight()

    def add_custom_bg_dialog(self):
        menu = QMenu()
        act_color = menu.addAction("🎨 Couleur Hex")
        act_img = menu.addAction("🖼️ Image locale")
        act_url = menu.addAction("🔗 URL Image")
        
        from PyQt6.QtGui import QCursor
        from PyQt6.QtWidgets import QInputDialog, QFileDialog
        action = menu.exec(QCursor.pos())
        if action == act_color:
            text, ok = QInputDialog.getText(self, "Ajouter une couleur", "Code Hex (ex: #ff00ff):")
            if ok and text:
                text = text.strip()
                if not text.startswith("#"): text = "#" + text
                from config import BASE_CONFIG as default_config
                default_config["custom_backgrounds"].append(text)
                self.refresh_color_grid()
        elif action == act_img:
            file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un arrière-plan", "", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)")
            if file_path:
                try:
                    import shutil, time, os
                    from config import get_video_dir, BASE_CONFIG as default_config
                    video_dir = get_video_dir(self.tid)
                    os.makedirs(video_dir, exist_ok=True)
                    filename = os.path.basename(file_path)
                    safe_filename = f"bg_{int(time.time())}_{filename.replace(' ', '_')}"
                    dest_path = os.path.join(video_dir, safe_filename)
                    shutil.copy2(file_path, dest_path)
                    default_config["custom_backgrounds"].append(safe_filename)
                    self.refresh_color_grid()
                except Exception as e:
                    try:
                        from helpers import log_error
                        log_error("PublicationDialog._handle_bg_action.add", e)
                    except Exception:
                        pass
        elif action == act_url:
            text, ok = QInputDialog.getText(self, "Ajouter une URL", "URL de l'image:")
            if ok and text.startswith("http"):
                from config import BASE_CONFIG as default_config
                default_config["custom_backgrounds"].append(text)
                self.refresh_color_grid()

    def update_color_highlight(self):
        for btn, c in self.color_buttons:
            is_sel = (c == self.selected_bg)
            btn.setText("") # Reset text
            if c == "transparent":
                btn.setStyleSheet(f"QPushButton {{ background-color: {self._t_chk['border']}; color: {'white' if is_sel else self._t_chk['text_dim']}; border: {3 if is_sel else 2}px solid {'white' if is_sel else 'transparent'}; border-radius: 6px; font-size: 10px; font-weight: normal; }}")
            elif c.startswith("data:image") or c.startswith("http"):
                btn.setText("URL")
                btn.setStyleSheet(f"QPushButton {{ background-color: {self._t_chk['border_hover']}; color: {'white' if is_sel else self._t_chk['text_dim']}; border: {3 if is_sel else 2}px solid {'white' if is_sel else 'transparent'}; border-radius: 6px; font-weight: normal; font-size: 10px; }}")
            elif c.startswith("bg_"):
                from config import get_video_dir
                abs_path = os.path.join(get_video_dir(self.tid), c).replace('\\', '/')
                btn.setStyleSheet(f"QPushButton {{ border-image: url('{abs_path}'); border: {3 if is_sel else 2}px solid {'white' if is_sel else 'transparent'}; border-radius: 6px; }}")
            else:
                btn.setStyleSheet(f"QPushButton {{ background-color: {c}; border: {3 if is_sel else 2}px solid {'white' if is_sel else 'transparent'}; border-radius: 6px; }}")

    def update_type_ui(self):
        try:
            is_share = self.rb_share.isChecked()
            is_link = self.rb_link.isChecked()
            is_text = self.rb_text.isChecked()
            is_video = self.rb_video.isChecked()
            is_photo = self.rb_photo.isChecked()
            is_media = is_photo or is_video

            # Share section handling is in sidebar, just toggle its visibility in the sidebar maybe?
            # Or we let users configure it always, and it's ignored if type != share.
            
            show_img = is_media or is_link or (is_share and self.i_share_type.currentText() in ["Image", "Vidéo", "Lien"])
            self.image_widget.setVisible(show_img)
        
            is_fake_video = self.chk_fake_video.isChecked() if self.video_options_widget.isVisible() else False
            
            show_img_btn = is_photo or is_link or (is_share and self.i_share_type.currentText() in ["Image", "Lien"]) or (is_video and is_fake_video) or (is_share and self.i_share_type.currentText() == "Vidéo" and is_fake_video)
            show_vid_btn = (is_video and not is_fake_video) or (is_share and self.i_share_type.currentText() == "Vidéo" and not is_fake_video)
            
            self.btn_browse_pub_img.setVisible(show_img_btn)
            self.btn_browse_pub_vid.setVisible(show_vid_btn)
        
            self.video_options_widget.setVisible(is_video or (is_share and self.i_share_type.currentText() == "Vidéo"))
            self.music_options_widget.setVisible(True)
            self.color_inner_group.setVisible(is_text or (is_share and self.i_share_type.currentText() == "Texte seul"))
            self.link_widget.setVisible(is_link or (is_share and self.i_share_type.currentText() == "Lien"))

            # ── Galerie d'images supplémentaires : visible uniquement pour les photos ──
            # Pas pour les vidéos, textes, liens, ou partages
            if hasattr(self, 'extra_images_widget'):
                self.extra_images_widget.setVisible(is_photo)

            if is_photo or (is_share and self.i_share_type.currentText() == "Image") or is_fake_video:
                self.i_image.setPlaceholderText("URL Image ou Parcourir 📂")
            elif is_video or (is_share and self.i_share_type.currentText() == "Vidéo"):
                self.i_image.setPlaceholderText("URL Vidéo ou Parcourir 📂")
            elif is_link or (is_share and self.i_share_type.currentText() == "Lien"):
                self.i_image.setPlaceholderText("URL de l'image de couverture du lien")
            
            if self.video_options_widget.isVisible():
                self._on_fake_video_toggled(self.chk_fake_video.isChecked())
                
            # Disable the "Post Partagé" tab if the publication is not of type "share"
            share_item = self.sidebar.item(3) # "🔄 Post Partagé" is index 3
            if share_item:
                if is_share:
                    share_item.setFlags(share_item.flags() | Qt.ItemFlag.ItemIsEnabled)
                    share_item.setForeground(Qt.GlobalColor.white)
                else:
                    share_item.setFlags(share_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    share_item.setForeground(Qt.GlobalColor.gray)
                    # If we disable it while the user is viewing it, force navigation back to general
                    if self.sidebar.currentRow() == 3:
                        self.sidebar.setCurrentRow(0)
                        
            # Reparent the media group to the share tab or media tab
            if is_share:
                self.share_media_layout.addWidget(self.media_group_widget)
            else:
                self.main_media_layout.addWidget(self.media_group_widget)

        except Exception as e:
            from helpers import log_error
            log_error('widgets.update_type_ui', e)

    def _on_fake_video_toggled(self, checked):
        self.video_real_options.setVisible(not checked)

    def update_share_group_ui(self):
        self.share_group_widget.setVisible(self.chk_share_is_group.isChecked())

    def update_group_ui(self):
        self.group_widget.setVisible(self.chk_is_group.isChecked())

    def open_text_editor(self):
        dialog = TextEditorDialog(self, self._main_text)
        if dialog.exec():
            self._main_text = dialog.get_text()
            self.i_text_preview.setText(self._main_text.replace("<br>", " ")[:30] + "...")

    def open_share_text_editor(self):
        dialog = TextEditorDialog(self, self._share_text)
        if dialog.exec():
            self._share_text = dialog.get_text()
            self.i_share_desc_preview.setText(self._share_text.replace("<br>", " ")[:30] + "...")

    def select_image(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner une image de publication", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "img")
            if media: self.i_image.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_image', e)

    def add_extra_image(self):
        """Ajoute une image supplémentaire pour le carousel via la galerie."""
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Image supplémentaire (carousel)", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "extra")
            if media and media not in self._extra_images:
                self._extra_images.append(media)
                self._refresh_extra_gallery()
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog.add_extra_image', e)
            except Exception:
                pass

    def clear_extra_images(self):
        """Efface toutes les images supplémentaires."""
        try:
            self._extra_images = []
            self._refresh_extra_gallery()
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog.clear_extra_images', e)
            except Exception:
                pass

    def remove_extra_image(self, idx):
        """Supprime une image supplémentaire par son index."""
        try:
            if 0 <= idx < len(self._extra_images):
                self._extra_images.pop(idx)
                self._refresh_extra_gallery()
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog.remove_extra_image', e)
            except Exception:
                pass

    def _on_extra_reordered(self):
        """Resynchronise la liste après un drag-drop dans la galerie."""
        try:
            new_list = []
            for i in range(self._extra_list.count()):
                item = self._extra_list.item(i)
                thumb = self._extra_list.itemWidget(item)
                if thumb is not None:
                    new_list.append(thumb._img_path)
            self._extra_images = new_list
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._on_extra_reordered', e)
            except Exception:
                pass

    def _extra_drop_event(self, event):
        """Handler personnalisé pour le dropEvent de la galerie."""
        try:
            # Arrêter le timer de scroll
            if self._extra_scroll_timer:
                self._extra_scroll_timer.stop()
                self._extra_scroll_timer = None
            QListWidget.dropEvent(self._extra_list, event)
            self._on_extra_reordered()
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._extra_drop_event', e)
            except Exception:
                pass

    def _extra_drag_enter(self, event):
        """Démarre le scroll quand un drag entre dans la liste."""
        try:
            QListWidget.dragEnterEvent(self._extra_list, event)
            self._extra_start_scroll_timer()
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._extra_drag_enter', e)
            except Exception:
                pass

    def _extra_drag_move(self, event):
        """Maintient le scroll pendant le déplacement."""
        try:
            QListWidget.dragMoveEvent(self._extra_list, event)
            # Le timer tourne déjà, rien de plus à faire ici
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._extra_drag_move', e)
            except Exception:
                pass

    def _extra_start_scroll_timer(self):
        """Démarre un timer pour faire défiler la liste pendant le drag."""
        try:
            from PyQt6.QtCore import QTimer
            if self._extra_scroll_timer is None:
                self._extra_scroll_timer = QTimer(self)
                self._extra_scroll_timer.timeout.connect(self._extra_do_scroll)
            self._extra_scroll_timer.start(100)  # toutes les 100ms
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._extra_start_scroll_timer', e)
            except Exception:
                pass

    def _extra_do_scroll(self):
        """Fait défiler la liste vers le haut ou le bas selon la position de la souris."""
        try:
            from PyQt6.QtGui import QCursor
            pos = self._extra_list.mapFromGlobal(QCursor.pos())
            rect = self._extra_list.viewport().rect()
            margin = 50
            if pos.y() < margin:
                # Scroller vers le haut
                bar = self._extra_list.verticalScrollBar()
                bar.setValue(bar.value() - 15)
            elif pos.y() > rect.height() - margin:
                # Scroller vers le bas
                bar = self._extra_list.verticalScrollBar()
                bar.setValue(bar.value() + 15)
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._extra_do_scroll', e)
            except Exception:
                pass

    def _refresh_extra_gallery(self):
        """Reconstruit la galerie des images supplémentaires."""
        try:
            self._extra_list.blockSignals(True)
            self._extra_list.clear()
            self._extra_thumbs = []
            for idx, img_path in enumerate(self._extra_images):
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 70))
                thumb = _ExtraImageThumb(idx, img_path, self)
                self._extra_list.addItem(item)
                self._extra_list.setItemWidget(item, thumb)
                self._extra_thumbs.append(thumb)
            self._extra_list.blockSignals(False)
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.PublicationDialog._refresh_extra_gallery', e)
            except Exception:
                pass
            try:
                self._extra_list.blockSignals(False)
            except Exception:
                pass

    def select_video(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner une vidéo de publication", "Vidéos (*.mp4 *.webm *.ogg *.mov *.avi)", "vid")
            if media: self.i_image.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_video', e)

    def select_video_cover(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner une couverture (Aperçu) pour la vidéo", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "cov")
            if media: self.i_video_cover.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_video_cover', e)

    def select_profile_pic_pub(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner une photo de profil", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "prf")
            if media: self.i_prof_pic.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_profile_pic_pub', e)

    def select_group_pic(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner une photo de groupe", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "grp")
            if media: self.i_group_pic.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_group_pic', e)

    def add_reaction(self, name):
        try:
            curr = self.i_reactions.text()
            if not curr: self.i_reactions.setText(name)
            else:
                if name not in curr: self.i_reactions.setText(curr + "," + name)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.add_reaction', e)

    def select_music(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner une musique", "Audio (*.mp3 *.wav *.ogg *.m4a)", "mus")
            if media: self.i_music_url.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_music', e)

    def select_share_pic(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner la photo de l'auteur partagé", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "share")
            if media: self.i_share_pic.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_share_pic', e)

    def select_share_group_pic(self):
        try:
            media = MediaSelectorDialog.get_media(self, self.tid, "Sélectionner la photo du groupe partagé", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "sgp")
            if media: self.i_share_group_pic.setText(media)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.select_share_group_pic', e)

    def get_data(self):
        try:
            pub_type = "text"
            if self.rb_photo.isChecked(): pub_type = "image"
            elif self.rb_video.isChecked(): pub_type = "video"
            elif self.rb_share.isChecked(): pub_type = "share"
            elif self.rb_link.isChecked(): pub_type = "link"

            reactions = []
            if self.i_reactions.text():
                from templates import REACTIONS_MAP
                for rt in self.i_reactions.text().split(","):
                    rt = rt.strip()
                    if rt in REACTIONS_MAP:
                        reactions.append({"name": rt, "icon": REACTIONS_MAP[rt]["icon"], "color": REACTIONS_MAP[rt]["color"]})
    
            is_video_post = pub_type == "video" or (pub_type == "share" and self.i_share_type.currentText() == "Vidéo")
            
            video_cover_field = self.i_video_cover.text() if is_video_post else ""
            if is_video_post and self.chk_fake_video.isChecked() and not video_cover_field:
                video_cover_field = self.i_image.text()
                
            image_val = self.i_image.text() if (pub_type in ["image", "video"] or (pub_type == "share" and self.i_share_type.currentText() in ["Vidéo", "Image", "Lien"])) else ""
            link_domain_val = self.i_link_domain.text() if pub_type == "link" else ""
            link_title_val = self.i_link_title.text() if pub_type == "link" else ""
            
            share_pic_val = self.i_share_pic.text() if pub_type == "share" else ""
            
            # Allow bg for text posts AND share posts with share_type "Texte seul"
            is_share_text = (pub_type == "share" and self.i_share_type.currentText() == "Texte seul")
            bg_val = self.selected_bg if (pub_type == "text" or is_share_text) else "transparent"
            if pub_type != "text" and not is_share_text and self.selected_bg != "transparent":
                self.selected_bg = "transparent"
                self.update_color_highlight()
    
            return {
                "type": pub_type,
                "platform": self.platform,
                "text": self._main_text,
                "bg": bg_val,
                "audience": self.i_audience.currentText(),
                "time_ago": self.i_time.text() or "2h",
                "profile_name": self.i_prof_name.text(),
                "verified": self.chk_verified.isChecked(),
                "has_story": self.chk_has_story.isChecked(),
                "is_online": self.chk_is_online.isChecked(),
                "profile_pic": self.i_prof_pic.text(),
                "use_status": self.chk_use_status.isChecked(),
                "status_text": self.i_status.text(),
                "show_subscribe": self.chk_show_subscribe.isChecked(),
                "subscribe_text": self.i_subscribe_text.text() if self.chk_show_subscribe.isChecked() else "",
                "is_group": self.chk_is_group.isChecked(),
                "group_name": self.i_group_name.text() if self.chk_is_group.isChecked() else "",
                "group_pic": self.i_group_pic.text() if self.chk_is_group.isChecked() else "",
                "show_join": self.chk_show_join.isChecked(),
                "join_text": self.i_join_text.text() if self.chk_show_join.isChecked() else "",
                "image": image_val,
                "extra_images": list(self._extra_images) if (pub_type == "image" and self._extra_images) else [],
                "link_domain": link_domain_val,
                "link_title": link_title_val,
                "reactions": reactions,
                "likes": self.i_likes_count.text(),
                "comments_count": self.i_comments_count.text(),
                "shares_count": self.i_shares_count.text(),
                "sim_action": self.chk_sim_action.isChecked(),
                "sim_reaction": self.i_sim_reaction.currentText() if self.chk_sim_action.isChecked() else "",
                "use_tags": self.chk_use_tags.isChecked(),
                "tag_name": self.i_tags.text() if self.chk_use_tags.isChecked() else "",
                "tag_count": self.i_tags_count.text() if self.chk_use_tags.isChecked() else "",
                "use_private": self.chk_use_private.isChecked(),
                "private_count": self.i_private_count.text(),
                "blur_enabled": self.chk_blur.isChecked(),
                "blur_reason": self.i_blur_reason.text().strip() if self.chk_blur.isChecked() else "",
                "blur_mode": self.cmb_blur_mode.currentData() if self.chk_blur.isChecked() else "instant",
                "blur_delay": int(self.i_blur_delay.text().strip()) if self.i_blur_delay.text().strip().isdigit() and self.chk_blur.isChecked() else 3,
                "share_type": self.i_share_type.currentText(),
                "share_title": self.i_share_title.text(),
                "share_verified": self.chk_share_verified.isChecked(),
                "share_has_story": self.chk_share_has_story.isChecked(),
                "share_is_online": self.chk_share_is_online.isChecked(),
                "share_is_group": self.chk_share_is_group.isChecked(),
                "share_group_name": self.i_share_group_name.text() if self.chk_share_is_group.isChecked() else "",
                "share_group_pic": self.i_share_group_pic.text() if self.chk_share_is_group.isChecked() else "",
                "share_time_ago": self.i_share_time.text(),
                "share_audience": self.i_share_audience.currentText(),
                "share_pic": share_pic_val,
                "share_desc": self._share_text,
                "share_use_status": self.chk_share_use_status.isChecked(),
                "share_status_text": self.i_share_status.text(),
                "share_use_tags": self.chk_share_use_tags.isChecked(),
                "share_tags": self.i_share_tags.text() if self.chk_share_use_tags.isChecked() else "",
                "share_tags_count": self.i_share_tags_count.text() if self.chk_share_use_tags.isChecked() else "",
                "share_show_subscribe": self.chk_share_show_subscribe.isChecked(),
                "share_subscribe_text": self.i_share_subscribe_text.text() if self.chk_share_show_subscribe.isChecked() else "",
                "share_show_join": self.chk_share_show_join.isChecked(),
                "share_join_text": self.i_share_join_text.text() if self.chk_share_show_join.isChecked() else "",
                "video_resolutions": [r.strip() for r in self.i_video_resolutions.text().split(",")] if is_video_post else [],
                "video_cover": video_cover_field,
                "fake_video": self.chk_fake_video.isChecked() if is_video_post else False,
                "sound_enabled": self.chk_sound.isChecked() if is_video_post else True,
                "has_music": self.chk_has_music.isChecked(),
                "music_name": self.i_music_name.text(),
                "music_url": self.i_music_url.text(),
                "music_hidden": self.chk_music_hidden.isChecked() if self.chk_has_music.isChecked() else False,
            }
        except Exception as e:
            from helpers import log_error
            log_error('widgets.PublicationDialog.get_data', e)
            return {}
