"""_video_dialog.py - VideoPublicationDialog de base pour Snapchat et TikTok.

Cette classe est importee par platforms/snapchat/dialog.py et platforms/tiktok/dialog.py.
"""

"""video_publication_dialog.py — Video publication editor for Snapchat & TikTok.

Uses the SAME visual style as the classic PublicationDialog (sidebar +
QStackedWidget + scrollable pages) so the user gets a consistent experience
across all platforms.

The dialog has 5 sidebar pages:
  1. 📌 Général — video source, cover, blur
  2. 👤 Auteur — profile name, profile pic, verified
  3. ✍️ Contenu — caption, tags/hashtags
  4. 🎵 Son — sound name, audio file, disc image
  5. 📊 Engagement — likes, comments, shares

The returned dict is COMPATIBLE with the existing feed pipeline.
"""

import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QFileDialog, QWidget, QScrollArea,
    QListWidget, QStackedWidget, QMessageBox, QPlainTextEdit,
)
from PyQt6.QtCore import Qt

from widgets_parts.bounce_button import BounceButton
from widgets_parts.media_selector import MediaSelectorDialog
from widgets_parts.text_editor import TextEditorDialog


class VideoPublicationDialog(QDialog):
    """Video-focused publication editor for Snapchat & TikTok.

    Uses the same sidebar + stacked-widget layout as PublicationDialog
    so the visual experience is consistent across all platforms.
    """

    def __init__(self, parent=None, pub_data=None, tid=None, platform="snapchat"):
        try:
            super().__init__(parent)
            self.tid = tid
            self.platform = (platform or "snapchat").lower().strip()
            if self.platform not in ("snapchat", "tiktok"):
                self.platform = "snapchat"

            self.setWindowTitle(f"Configuration de la Vidéo {self.platform.title()}")
            self.setMinimumSize(850, 600)

            # Load theme colors once
            from theme import get_theme as _gt
            self._t = _gt()

            self._apply_theme_style()

            # ── Main layout: sidebar (left) + content area (right) ──
            main_lay = QHBoxLayout(self)
            main_lay.setContentsMargins(0, 0, 0, 0)
            main_lay.setSpacing(0)

            # 1. Sidebar
            self.sidebar = QListWidget()
            self.sidebar.setObjectName("sidebar")
            self.sidebar.setFixedWidth(200)
            items = [
                "📌 Général",
                "👤 Auteur",
                "✍️ Contenu",
                "🎵 Son",
                "📊 Engagement",
            ]
            for text in items:
                self.sidebar.addItem(text)
            main_lay.addWidget(self.sidebar)

            # 2. Content area
            right_container = QWidget()
            right_lay = QVBoxLayout(right_container)
            right_lay.setContentsMargins(15, 15, 15, 15)
            right_lay.setSpacing(10)

            self.stacked = QStackedWidget()
            right_lay.addWidget(self.stacked)

            # Bottom buttons
            btn_lay = QHBoxLayout()
            btn_ok = BounceButton("✓ Valider")
            from theme import btn_style_accent as _bsa
            btn_ok.setStyleSheet(_bsa())
            btn_ok.clicked.connect(self._validate_and_accept)

            btn_cancel = BounceButton("✕ Annuler")
            from theme import btn_style_danger as _bsd
            btn_cancel.setStyleSheet(_bsd())
            btn_cancel.clicked.connect(self.reject)

            btn_lay.addStretch()
            btn_lay.addWidget(btn_cancel)
            btn_lay.addWidget(btn_ok)
            right_lay.addLayout(btn_lay)

            main_lay.addWidget(right_container, 1)

            # Build pages
            self.stacked.addWidget(self._create_page_general())
            self.stacked.addWidget(self._create_page_author())
            self.stacked.addWidget(self._create_page_content())
            self.stacked.addWidget(self._create_page_sound())
            self.stacked.addWidget(self._create_page_engagement())

            self.sidebar.currentRowChanged.connect(self.stacked.setCurrentIndex)
            self.sidebar.setCurrentRow(0)

            # Connect blur checkbox
            self.chk_blur.toggled.connect(self.i_blur_reason.setEnabled)
            self.i_blur_reason.setEnabled(False)

            # Populate from existing data
            self._populate(pub_data or {})
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog.__init__", e)
            except Exception:
                pass

    # ════════════════════════════════════════════════════════════════════
    #  Theme
    # ════════════════════════════════════════════════════════════════════
    def _apply_theme_style(self):
        """Apply the same stylesheet as PublicationDialog."""
        try:
            t = self._t
            self.setStyleSheet(f'''
                QDialog {{ background-color: {t['bg']}; color: {t['text']}; }}
                QWidget#sidebar {{ background-color: {t['bg_alt']}; border-right: 1px solid {t['border']}; }}
                QListWidget {{ background-color: transparent; border: none; outline: none; }}
                QListWidget::item {{ color: {t['text_dim']}; padding: 12px 15px; font-weight: bold; font-size: 13px; border-radius: 6px; margin: 4px 8px; }}
                QListWidget::item:hover {{ background-color: {t['border']}; color: {t['text']}; }}
                QListWidget::item:selected {{ background-color: {t['accent']}; color: white; }}

                QStackedWidget {{ background-color: {t['bg']}; }}

                QLabel.section-header {{ color: {t['text']}; font-size: 16px; font-weight: bold; padding-bottom: 8px; border-bottom: 1px solid {t['border']}; margin-bottom: 10px; }}

                QLabel {{ color: {t['text']}; font-size: 12px; font-weight: 500; }}
                QLineEdit, QComboBox, QPlainTextEdit {{
                    background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; padding: 8px 10px;
                    border-radius: 6px; color: {t['text']}; font-size: 12px;
                }}
                QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{ border: 1px solid {t['accent']}; background-color: {t['bg']}; }}
                QPlainTextEdit {{ min-height: 80px; max-height: 200px; }}

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
            ''')
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._apply_theme_style", e)
            except Exception:
                pass

    # ════════════════════════════════════════════════════════════════════
    #  Page builders — same structure as PublicationDialog
    # ════════════════════════════════════════════════════════════════════
    def _create_scrollable_page(self, title):
        """Create a scrollable page with a section header — same as PublicationDialog."""
        try:
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
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._create_scrollable_page", e)
            except Exception:
                pass
            page = QWidget()
            return page, QFormLayout(page)

    def _create_page_general(self):
        """Page 1: Général — video source, cover, blur."""
        try:
            page, lay = self._create_scrollable_page("📌 Vidéo — Source & Options")

            # Video source
            src_row = QHBoxLayout()
            src_row.setSpacing(8)
            self.i_source = QLineEdit()
            self.i_source.setPlaceholderText("https://example.com/video.mp4  —  ou cliquez sur Parcourir")
            src_row.addWidget(self.i_source, stretch=1)

            self.btn_browse_video = BounceButton("📁 Parcourir")
            self.btn_browse_video.clicked.connect(self._browse_video)
            src_row.addWidget(self.btn_browse_video)

            src_widget = QWidget()
            src_widget.setLayout(src_row)
            lay.addRow("Source vidéo :", src_widget)

            # Hint
            hint = QLabel("💡 La vidéo démarre en pause ; un appui la lance avec le son.")
            hint.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
            hint.setWordWrap(True)
            lay.addRow("", hint)

            # Cover
            cov_row = QHBoxLayout()
            cov_row.setSpacing(8)
            self.i_cover = QLineEdit()
            self.i_cover.setPlaceholderText("URL ou fichier local (optionnel)")
            cov_row.addWidget(self.i_cover, stretch=1)

            self.btn_browse_cover = BounceButton("📁 Parcourir")
            self.btn_browse_cover.clicked.connect(self._browse_cover)
            cov_row.addWidget(self.btn_browse_cover)

            cov_widget = QWidget()
            cov_widget.setLayout(cov_row)
            lay.addRow("Couverture :", cov_widget)

            # Blur
            self.chk_blur = QCheckBox("Floutter la vidéo")
            self.chk_blur.setToolTip("Active un flou sur la vidéo dans le feed.\nLa victime verra la raison + un bouton « Se connecter pour voir ».")
            lay.addRow("", self.chk_blur)

            self.i_blur_reason = QLineEdit()
            self.i_blur_reason.setPlaceholderText("Raison affichée à la victime (ex: Contenu sensible)")
            self.i_blur_reason.setEnabled(False)
            lay.addRow("Raison du flou :", self.i_blur_reason)

            return page
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._create_page_general", e)
            except Exception:
                pass
            return QWidget()

    def _create_page_author(self):
        """Page 2: Auteur — profile name, profile pic, verified."""
        try:
            page, lay = self._create_scrollable_page("👤 Auteur")

            self.i_prof_name = QLineEdit()
            self.i_prof_name.setPlaceholderText("Laissez vide pour utiliser le nom de la cible")
            lay.addRow("Nom affiché :", self.i_prof_name)

            pic_row = QHBoxLayout()
            pic_row.setSpacing(8)
            self.i_prof_pic = QLineEdit()
            self.i_prof_pic.setPlaceholderText("URL ou fichier local (optionnel)")
            pic_row.addWidget(self.i_prof_pic, stretch=1)

            self.btn_browse_pic = BounceButton("📁 Parcourir")
            self.btn_browse_pic.clicked.connect(self._browse_profile_pic)
            pic_row.addWidget(self.btn_browse_pic)

            pic_widget = QWidget()
            pic_widget.setLayout(pic_row)
            lay.addRow("Photo de profil :", pic_widget)

            self.chk_verified = QCheckBox("✓ Compte vérifié")
            lay.addRow("", self.chk_verified)

            return page
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._create_page_author", e)
            except Exception:
                pass
            return QWidget()

    def _create_page_content(self):
        """Page 3: Contenu — caption + hashtags."""
        try:
            page, lay = self._create_scrollable_page("✍️ Contenu")

            self.i_caption = QPlainTextEdit()
            self.i_caption.setPlaceholderText("Texte affiché en overlay sur la vidéo (multi-lignes supporté)")
            self.i_caption.setTabChangesFocus(True)
            self.i_caption.setMinimumHeight(80)
            self.i_caption.setMaximumHeight(200)

            # Bouton "Éditer" à côté de la légende pour coller n'importe quel texte
            caption_row = QHBoxLayout()
            caption_row.setSpacing(6)
            caption_row.addWidget(self.i_caption, stretch=1)
            self.btn_edit_caption = BounceButton("✏️ Éditer")
            self.btn_edit_caption.setFixedWidth(100)
            self.btn_edit_caption.setToolTip("Ouvrir l'éditeur de texte avancé pour coller n'importe quel texte")
            self.btn_edit_caption.clicked.connect(self._open_caption_editor)
            caption_row.addWidget(self.btn_edit_caption, alignment=Qt.AlignmentFlag.AlignTop)
            caption_w = QWidget()
            caption_w.setLayout(caption_row)
            lay.addRow("Légende :", caption_w)

            self.i_tags = QLineEdit()
            self.i_tags.setPlaceholderText("#fyp #viral #pourtoi")
            lay.addRow("Hashtags :", self.i_tags)

            return page
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._create_page_content", e)
            except Exception:
                pass
            return QWidget()

    def _open_caption_editor(self):
        """Ouvre l'éditeur de texte avancé pour permettre de coller n'importe quel texte."""
        try:
            current_text = self.i_caption.toPlainText()
            editor = TextEditorDialog(self, initial_text=current_text)
            if editor.exec() == QDialog.DialogCode.Accepted:
                new_text = editor.get_text()
                self.i_caption.setPlainText(new_text)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._open_caption_editor", e)
            except Exception:
                pass

    def _create_page_sound(self):
        """Page 4: Son — sound name, audio file, disc image."""
        try:
            page, lay = self._create_scrollable_page("🎵 Son")

            self.i_sound = QLineEdit()
            if self.platform == "tiktok":
                self.i_sound.setPlaceholderText("ex: Son original - @username")
            else:
                self.i_sound.setPlaceholderText("ex: Drake - God's Plan")
            lay.addRow("Titre du son :", self.i_sound)

            # Audio file
            audio_row = QHBoxLayout()
            audio_row.setSpacing(8)
            self.i_sound_file = QLineEdit()
            self.i_sound_file.setPlaceholderText("URL ou fichier local (.mp3, .wav, .m4a...) — optionnel")
            audio_row.addWidget(self.i_sound_file, stretch=1)

            self.btn_browse_sound = BounceButton("📁 Parcourir")
            self.btn_browse_sound.clicked.connect(self._browse_sound_file)
            audio_row.addWidget(self.btn_browse_sound)

            audio_widget = QWidget()
            audio_widget.setLayout(audio_row)
            lay.addRow("Fichier audio :", audio_widget)

            hint = QLabel("💡 Si renseigné, l'audio se joue en parallèle de la vidéo (le son natif de la vidéo est coupé).")
            hint.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
            hint.setWordWrap(True)
            lay.addRow("", hint)

            # Disc image
            disc_row = QHBoxLayout()
            disc_row.setSpacing(8)
            self.i_disc_image = QLineEdit()
            self.i_disc_image.setPlaceholderText("URL ou fichier local (affiché dans le disque tournant)")
            disc_row.addWidget(self.i_disc_image, stretch=1)

            self.btn_browse_disc = BounceButton("📁 Parcourir")
            self.btn_browse_disc.clicked.connect(self._browse_disc_image)
            disc_row.addWidget(self.btn_browse_disc)

            disc_widget = QWidget()
            disc_widget.setLayout(disc_row)
            lay.addRow("Image du disque :", disc_widget)

            return page
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._create_page_sound", e)
            except Exception:
                pass
            return QWidget()

    def _create_page_engagement(self):
        """Page 5: Engagement — likes, comments, shares, favorites."""
        try:
            page, lay = self._create_scrollable_page("📊 Engagement")

            self.i_likes = QLineEdit()
            self.i_likes.setPlaceholderText("ex: 1240")
            lay.addRow("👍 J'aime :", self.i_likes)

            self.i_comments = QLineEdit()
            self.i_comments.setPlaceholderText("ex: 89")
            lay.addRow("💬 Commentaires :", self.i_comments)

            self.i_shares = QLineEdit()
            self.i_shares.setPlaceholderText("ex: 45")
            lay.addRow("➤ Partages :", self.i_shares)

            self.i_favorites = QLineEdit()
            self.i_favorites.setPlaceholderText("ex: 230")
            lay.addRow("🔖 Favoris :", self.i_favorites)

            # Visibility
            self.chk_visible = QCheckBox("Visible dans le feed")
            self.chk_visible.setChecked(True)
            self.chk_visible.setToolTip("Décochez pour masquer cette vidéo du feed sans la supprimer.")
            lay.addRow("", self.chk_visible)

            return page
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._create_page_engagement", e)
            except Exception:
                pass
            return QWidget()

    # ════════════════════════════════════════════════════════════════════
    #  File pickers
    # ════════════════════════════════════════════════════════════════════
    def _browse_video(self):
        try:
            media = MediaSelectorDialog.get_media(
                self, self.tid, "Sélectionner une vidéo",
                "Vidéos (*.mp4 *.webm *.ogg *.mov *.avi *.mkv *.flv *.m4v)", "vid")
            if media:
                self.i_source.setText(media)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._browse_video", e)
            except Exception:
                pass

    def _browse_cover(self):
        try:
            media = MediaSelectorDialog.get_media(
                self, self.tid, "Sélectionner une image de couverture",
                "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "cov")
            if media:
                self.i_cover.setText(media)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._browse_cover", e)
            except Exception:
                pass

    def _browse_profile_pic(self):
        try:
            media = MediaSelectorDialog.get_media(
                self, self.tid, "Sélectionner une photo de profil",
                "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "prf")
            if media:
                self.i_prof_pic.setText(media)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._browse_profile_pic", e)
            except Exception:
                pass

    def _browse_disc_image(self):
        try:
            media = MediaSelectorDialog.get_media(
                self, self.tid, "Sélectionner l'image du disque musical",
                "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "dsc")
            if media:
                self.i_disc_image.setText(media)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._browse_disc_image", e)
            except Exception:
                pass

    def _browse_sound_file(self):
        try:
            media = MediaSelectorDialog.get_media(
                self, self.tid, "Sélectionner un fichier audio",
                "Audio (*.mp3 *.wav *.ogg *.m4a *.aac *.flac)", "snd")
            if media:
                self.i_sound_file.setText(media)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._browse_sound_file", e)
            except Exception:
                pass

    # ════════════════════════════════════════════════════════════════════
    #  Validate + accept
    # ════════════════════════════════════════════════════════════════════
    def _validate_and_accept(self):
        try:
            src = self.i_source.text().strip()
            if not src:
                QMessageBox.warning(
                    self, "Vidéo manquante",
                    "Veuillez sélectionner une vidéo (URL ou fichier local) avant de valider.")
                return
            # Security: if music file/URL is provided, music name is required
            has_music_file = bool(self.i_sound_file.text().strip()) if hasattr(self, 'i_sound_file') else False
            has_music_name = bool(self.i_sound.text().strip()) if hasattr(self, 'i_sound') else False
            if has_music_file and not has_music_name:
                QMessageBox.warning(
                    self, "Musique incomplète",
                    "Vous avez sélectionné un fichier/lien musique mais vous n'avez pas mis le nom.\n"
                    "Veuillez saisir le nom de la musique.")
                return
            self.accept()
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._validate_and_accept", e)
            except Exception:
                pass
            self.accept()

    # ════════════════════════════════════════════════════════════════════
    #  Populate / get_data
    # ════════════════════════════════════════════════════════════════════
    def _populate(self, pub_data):
        try:
            self.i_source.setText(pub_data.get("image", "") or "")
            self.i_cover.setText(pub_data.get("video_cover", "") or "")
            self.chk_blur.setChecked(bool(pub_data.get("blur_enabled", False)))
            self.i_blur_reason.setText(pub_data.get("blur_reason", "") or "")
            self.i_blur_reason.setEnabled(self.chk_blur.isChecked())
            self.i_prof_name.setText(pub_data.get("profile_name", "") or "")
            self.i_prof_pic.setText(pub_data.get("profile_pic", "") or "")
            self.chk_verified.setChecked(bool(pub_data.get("verified", False)))
            self.i_caption.setPlainText(pub_data.get("caption", "") or pub_data.get("text", "") or "")
            self.i_tags.setText(pub_data.get("tags", "") or pub_data.get("tag_name", "") or pub_data.get("share_tags", "") or "")
            self.i_sound.setText(pub_data.get("sound_name") or pub_data.get("music_name", "") or "")
            self.i_disc_image.setText(pub_data.get("sound_image") or pub_data.get("music_image", "") or "")
            self.i_sound_file.setText(pub_data.get("music_url") or pub_data.get("sound_url", "") or "")
            self.i_likes.setText(str(pub_data.get("likes", "") or ""))
            self.i_comments.setText(str(pub_data.get("comments_count", pub_data.get("comments", "")) or ""))
            self.i_shares.setText(str(pub_data.get("shares_count", pub_data.get("shares", "")) or ""))
            self.i_favorites.setText(str(pub_data.get("favorites_count", pub_data.get("favorites", "")) or ""))
            self.chk_visible.setChecked(bool(pub_data.get("visible", True)))
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog._populate", e)
            except Exception:
                pass

    def get_data(self):
        try:
            caption = self.i_caption.toPlainText().strip()
            tags_raw = self.i_tags.text().strip()
            sound = self.i_sound.text().strip()
            full_text = caption
            if tags_raw:
                full_text = (caption + "\n" + tags_raw).strip() if caption else tags_raw
            src = self.i_source.text().strip()
            is_external = src.startswith("http://") or src.startswith("https://")

            return {
                "type":           "video",
                "platform":       self.platform,
                "video_mode":     "snapchat_spotlight" if self.platform == "snapchat" else "tiktok_fullscreen",
                "image":          src,
                "video_cover":    self.i_cover.text().strip(),
                "_is_external":   is_external,
                "blur_enabled":   self.chk_blur.isChecked(),
                "blur_reason":    self.i_blur_reason.text().strip() if self.chk_blur.isChecked() else "",
                "profile_name":   self.i_prof_name.text().strip(),
                "profile_pic":    self.i_prof_pic.text().strip(),
                "verified":       self.chk_verified.isChecked(),
                "text":           full_text,
                "caption":        caption,
                "tags":           tags_raw,
                "music_name":     sound,
                "sound_name":     sound,
                "has_music":      bool(sound),
                "sound_image":    self.i_disc_image.text().strip(),
                "music_image":    self.i_disc_image.text().strip(),
                "music_url":      self.i_sound_file.text().strip(),
                "sound_url":      self.i_sound_file.text().strip(),
                "has_sound_file": bool(self.i_sound_file.text().strip()),
                "likes":          self.i_likes.text().strip() or "0",
                "comments_count": self.i_comments.text().strip() or "0",
                "shares_count":   self.i_shares.text().strip() or "0",
                "favorites_count":self.i_favorites.text().strip() or "0",
                "favorites":      self.i_favorites.text().strip() or "0",
                "comments":       self.i_comments.text().strip() or "0",
                "shares":         self.i_shares.text().strip() or "0",
                "visible":        self.chk_visible.isChecked(),
                "audience":       "Public",
                "time_ago":       "À l'instant",
                "fake_video":     False,
                "sound_enabled":  True,
                "video_resolutions": [],
            }
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VideoPublicationDialog.get_data", e)
            except Exception:
                pass
            return {}
