"""dialog.py — Fenêtre de création de publication Instagram.

Style unique : barre bleue Instagram, fond sombre, colonne unique compacte.
Champs essentiels : type, source, légende, musique, profil, engagement.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QRadioButton, QButtonGroup, QPushButton, QFileDialog,
    QWidget, QScrollArea, QFrame, QMessageBox, QComboBox,
)
from PyQt6.QtCore import Qt

from widgets_parts.bounce_button import BounceButton
from widgets_parts.media_selector import MediaSelectorDialog
from widgets_parts.text_editor import TextEditorDialog


class InstagramPublicationDialog(QDialog):
    """Éditeur de publication Instagram — style compact avec accent bleu."""

    def __init__(self, parent=None, pub_data=None, tid=None, platform="instagram"):
        try:
            super().__init__(parent)
            self.tid = tid
            self.platform = "instagram"
            self.setWindowTitle("Instagram — Nouvelle publication")
            self.setMinimumSize(460, 560)
            self.resize(480, 620)

            from theme import get_theme as _gt
            self._t = _gt()
            self._apply_style()

            outer = QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

            outer.addWidget(self._build_header())

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            form_widget = QWidget()
            self._form = QFormLayout(form_widget)
            self._form.setContentsMargins(16, 14, 16, 14)
            self._form.setSpacing(10)
            self._build_fields()
            scroll.setWidget(form_widget)
            outer.addWidget(scroll, stretch=1)

            outer.addLayout(self._build_buttons())

            self._populate(pub_data or {})
            # Initialiser l'affichage des champs selon le type par défaut (Image)
            self._on_type_changed()
        except Exception as e:
            try: from helpers import log_error; log_error("IG.__init__", e)
            except Exception: pass

    def _apply_style(self):
        try:
            t = self._t
            self.setStyleSheet(f"""
                QDialog {{ background-color: {t['bg']}; }}
                QScrollArea {{ background-color: {t['bg']}; border: none; }}
                QLabel {{ color: {t['text']}; font-size: 12px; }}
                QLineEdit {{
                    background-color: {t['bg_input']};
                    border: 1px solid {t['border']};
                    border-radius: 6px; padding: 7px 10px;
                    color: {t['text']}; font-size: 12px;
                }}
                QLineEdit:focus {{ border: 2px solid #0095f6; }}
                QCheckBox, QRadioButton {{ color: {t['text']}; font-size: 12px; spacing: 6px; }}
                QCheckBox::indicator, QRadioButton::indicator {{
                    width: 16px; height: 16px; border-radius: 4px;
                    border: 2px solid {t['border_hover']}; background: {t['bg_input']};
                }}
                QRadioButton::indicator {{ border-radius: 8px; }}
                QCheckBox::indicator:checked {{ background: #0095f6; border-color: #0095f6; }}
                QRadioButton::indicator:checked {{ background: #0095f6; border-color: #0095f6; }}
                QScrollBar:vertical {{ border: none; background: {t['bg']}; width: 6px; }}
                QScrollBar::handle:vertical {{ background: {t['border_hover']}; border-radius: 3px; min-height: 20px; }}
                QPushButton {{ font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial; }}
            """)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._apply_style", e)
            except Exception: pass

    def _build_header(self):
        try:
            header = QFrame()
            header.setFixedHeight(48)
            header.setStyleSheet("QFrame { background-color: #0095f6; border: none; }")
            lay = QHBoxLayout(header)
            lay.setContentsMargins(16, 0, 16, 0)
            lbl = QLabel("📷  Instagram")
            lbl.setStyleSheet("color: #fff; font-size: 15px; font-weight: 800;")
            lay.addWidget(lbl)
            lay.addStretch()
            return header
        except Exception as e:
            try: from helpers import log_error; log_error("IG._build_header", e)
            except Exception: pass
            return QFrame()

    def _build_buttons(self):
        try:
            lay = QHBoxLayout()
            lay.setContentsMargins(16, 8, 16, 14)
            lay.setSpacing(10)
            cancel = BounceButton("✕  Annuler")
            cancel.setFixedHeight(36)
            cancel.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._t['bg_alt']};
                    color: {self._t['text']};
                    border: 1px solid {self._t['border_hover']};
                    border-radius: 8px; padding: 8px 18px;
                    font-size: 13px; font-weight: 600;
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                }}
                QPushButton:hover {{ border-color: #ef4444; color: #ef4444; background-color: {self._t['border']}; }}
                QPushButton:pressed {{ background-color: {self._t['border_hover']}; }}
            """)
            cancel.clicked.connect(self.reject)
            ok = BounceButton("✓  Valider")
            ok.setFixedHeight(36)
            ok.setStyleSheet("""
                QPushButton {
                    background-color: #0095f6; color: #fff; border: none;
                    border-radius: 8px; padding: 8px 24px;
                    font-size: 13px; font-weight: 800;
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                }
                QPushButton:hover { background-color: #0077c6; }
                QPushButton:pressed { background-color: #0062a8; padding-top: 9px; }
            """)
            ok.clicked.connect(self._validate)
            lay.addStretch()
            lay.addWidget(cancel)
            lay.addWidget(ok)
            return lay
        except Exception as e:
            try: from helpers import log_error; log_error("IG._build_buttons", e)
            except Exception: pass
            return QHBoxLayout()

    def _add_section_label(self, text):
        try:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {self._t['text_dim']}; font-size: 11px; font-weight: 700; "
                              f"text-transform: uppercase; letter-spacing: 1px; margin-top: 6px;")
            self._form.addRow(lbl)
            return lbl
        except Exception:
            return None

    # ── Système de cases à cocher pour activer/désactiver les champs ──
    def _add_toggle_field(self, key, label_text, field_widget, default_checked=True, store_label_attr=None):
        """Ajoute une ligne au formulaire avec une case à cocher comme label.
        store_label_attr: nom de l'attribut pour stocker la case (ex: '_cover_toggle')
        pour pouvoir la gérer dans _on_type_changed."""
        try:
            if not hasattr(self, '_toggles'):
                self._toggles = {}
            if not hasattr(self, '_toggle_widgets'):
                self._toggle_widgets = {}
            chk = QCheckBox(label_text)
            chk.setChecked(default_checked)
            chk.setStyleSheet("QCheckBox { font-size: 12px; font-weight: 600; }")
            self._toggles[key] = chk
            self._toggle_widgets[key] = field_widget
            if store_label_attr:
                setattr(self, store_label_attr, chk)
            chk.toggled.connect(lambda checked, k=key: self._on_toggle_changed(k, checked))
            self._form.addRow(chk, field_widget)
            self._apply_toggle_state(key, default_checked)
            return chk
        except Exception as e:
            try: from helpers import log_error; log_error("IG._add_toggle_field", e)
            except Exception: pass
            self._form.addRow(label_text, field_widget)
            return None

    def _on_toggle_changed(self, key, checked):
        try:
            self._apply_toggle_state(key, checked)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._on_toggle_changed", e)
            except Exception: pass

    def _apply_toggle_state(self, key, checked):
        try:
            widget = self._toggle_widgets.get(key)
            if widget is None:
                return
            self._set_widget_enabled_recursive(widget, checked)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._apply_toggle_state", e)
            except Exception: pass

    def _set_widget_enabled_recursive(self, widget, enabled):
        try:
            widget.setEnabled(enabled)
            if hasattr(widget, 'layout') and widget.layout() is not None:
                layout = widget.layout()
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item.widget():
                        self._set_widget_enabled_recursive(item.widget(), enabled)
        except Exception:
            try:
                widget.setEnabled(enabled)
            except Exception:
                pass

    def _is_toggle_on(self, key):
        try:
            chk = self._toggles.get(key) if hasattr(self, '_toggles') else None
            if chk is None:
                return True
            return chk.isChecked()
        except Exception:
            return True

    def _on_type_changed(self):
        """Affiche/masque les champs selon le type sélectionné."""
        try:
            is_text = self.rb_text.isChecked()
            is_video = self.rb_video.isChecked()
            is_image = self.rb_image.isChecked()
            # Média visible si Image ou Vidéo, masqué si Texte
            self._media_label.setVisible(not is_text)
            self._media_widget.setVisible(not is_text)
            if hasattr(self, '_media_section_label') and self._media_section_label:
                self._media_section_label.setVisible(not is_text)
            # Couverture visible seulement si Vidéo
            # La case à cocher "Couverture" sert de label
            if hasattr(self, '_cover_toggle') and self._cover_toggle:
                self._cover_toggle.setVisible(is_video)
            if hasattr(self, '_cover_widget') and self._cover_widget:
                self._cover_widget.setVisible(is_video)
            # ── Flou visible pour TOUS les types ──
            # La case à cocher "Floutter", la raison et le label de section
            # sont toujours visibles. Le mode (immédiat/après lecture) et le
            # délai ne sont visibles QUE pour les vidéos.
            for attr in ('_blur_chk_label', 'chk_blur', '_blur_reason_label', 'i_blur_reason'):
                w = getattr(self, attr, None)
                if w: w.setVisible(True)
            if hasattr(self, '_blur_section_label') and self._blur_section_label:
                self._blur_section_label.setVisible(True)
            # Mode et délai visibles seulement pour Vidéo
            for attr in ('_blur_mode_label', 'cmb_blur_mode', '_blur_delay_label', 'i_blur_delay'):
                w = getattr(self, attr, None)
                if w: w.setVisible(is_video)
            # Pour les types non-vidéo, forcer le mode "immédiat"
            if not is_video and hasattr(self, 'cmb_blur_mode'):
                try:
                    self.cmb_blur_mode.setCurrentIndex(0)  # "Immédiat"
                except Exception:
                    pass
            # Texte visible si Texte, masqué sinon
            self._text_label.setVisible(is_text)
            self.i_text_content.setVisible(is_text)
            if hasattr(self, '_text_section_label') and self._text_section_label:
                self._text_section_label.setVisible(is_text)
            # Hashtags visibles uniquement pour Vidéo (pas pour Image ni Texte)
            # La case à cocher "Hashtags" sert de label
            if hasattr(self, '_tags_toggle') and self._tags_toggle:
                self._tags_toggle.setVisible(is_video)
            if hasattr(self, 'i_tags') and self.i_tags:
                self.i_tags.setVisible(is_video)
            # Mettre à jour l'icône du bouton Parcourir selon le type
            if hasattr(self, '_browse_btn') and self._browse_btn:
                if is_image:
                    self._browse_btn.setText("🖼️ Parcourir")
                elif is_video:
                    self._browse_btn.setText("🎥 Parcourir")
                else:
                    self._browse_btn.setText("📂 Parcourir")
        except Exception as e:
            try: from helpers import log_error; log_error("IG._on_type_changed", e)
            except Exception: pass

    def _on_blur_mode_changed(self):
        try:
            is_delayed = self.cmb_blur_mode.currentData() == "delayed"
            is_video = self.rb_video.isChecked()
            # Le délai n'est visible que pour les vidéos ET en mode "delayed"
            self.i_blur_delay.setEnabled(is_delayed and self.chk_blur.isChecked() and is_video)
            if hasattr(self, '_blur_delay_label') and self._blur_delay_label:
                self._blur_delay_label.setVisible(is_delayed and is_video)
            self.i_blur_delay.setVisible(is_delayed and is_video)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._on_blur_mode_changed", e)
            except Exception: pass

    def _build_fields(self):
        try:
            # ── Initialiser les dictionnaires de toggles ──
            self._toggles = {}
            self._toggle_widgets = {}

            # ── Type ──
            self._add_section_label("📌 Type")
            type_row = QHBoxLayout()
            type_row.setSpacing(10)
            self.rb_text = QRadioButton("📝 Texte")
            self.rb_image = QRadioButton("📷 Image")
            self.rb_video = QRadioButton("🎥 Vidéo")
            self.rb_image.setChecked(True)
            self._type_group = QButtonGroup(self)
            self._type_group.addButton(self.rb_text)
            self._type_group.addButton(self.rb_image)
            self._type_group.addButton(self.rb_video)
            type_row.addWidget(self.rb_text)
            type_row.addWidget(self.rb_image)
            type_row.addWidget(self.rb_video)
            type_row.addStretch()
            type_w = QWidget(); type_w.setLayout(type_row)
            self._form.addRow("Type :", type_w)
            # Connecter les radio buttons pour afficher/masquer les champs selon le type
            self.rb_text.toggled.connect(self._on_type_changed)
            self.rb_image.toggled.connect(self._on_type_changed)
            self.rb_video.toggled.connect(self._on_type_changed)

            # ── Média (visible seulement si Image ou Vidéo) ──
            self._media_section_label = self._add_section_label("🖼️ Média")
            self.i_source = QLineEdit()
            self.i_source.setPlaceholderText("URL ou fichier local")
            self._media_label = QLabel("Source :")
            self._media_widget, self._browse_btn = self._make_browse_row(self.i_source, self._browse_media)
            self._form.addRow(self._media_label, self._media_widget)

            # Couverture (visible seulement si Vidéo) — avec case à cocher
            self.i_cover = QLineEdit()
            self.i_cover.setPlaceholderText("Image de couverture (optionnel)")
            self._cover_widget, _ = self._make_browse_row(self.i_cover, self._browse_cover)
            self._add_toggle_field("cover", "Couverture", self._cover_widget, store_label_attr='_cover_toggle')

            # ── Flou (visible pour TOUS les types, mode/délai seulement pour Vidéo) ──
            self._blur_section_label = self._add_section_label("🌫️ Flou")
            self.chk_blur = QCheckBox("Floutter le contenu")
            self.chk_blur.setToolTip("Active un flou sur le contenu dans le feed.\nLa victime verra la raison + un bouton « Se connecter pour voir ».\nPour les vidéos, vous pouvez choisir un mode différé avec délai.")
            self._blur_chk_label = QLabel("")
            self._form.addRow(self._blur_chk_label, self.chk_blur)
            self.i_blur_reason = QLineEdit()
            self.i_blur_reason.setPlaceholderText("Raison affichée à la victime (ex: Contenu sensible)")
            self.i_blur_reason.setEnabled(False)
            self.chk_blur.toggled.connect(self.i_blur_reason.setEnabled)
            self._blur_reason_label = QLabel("Raison :")
            self._form.addRow(self._blur_reason_label, self.i_blur_reason)
            self.cmb_blur_mode = QComboBox()
            self.cmb_blur_mode.addItem("Immédiat (flou direct)", "instant")
            self.cmb_blur_mode.addItem("Après lecture (son d'abord, puis flou)", "delayed")
            self.cmb_blur_mode.setEnabled(False)
            self.chk_blur.toggled.connect(self.cmb_blur_mode.setEnabled)
            self._blur_mode_label = QLabel("Mode :")
            self._form.addRow(self._blur_mode_label, self.cmb_blur_mode)
            self.i_blur_delay = QLineEdit()
            self.i_blur_delay.setPlaceholderText("Délai en secondes (ex: 3)")
            self.i_blur_delay.setText("3")
            self.i_blur_delay.setMaximumWidth(80)
            self.i_blur_delay.setEnabled(False)
            self.chk_blur.toggled.connect(self.i_blur_delay.setEnabled)
            self.cmb_blur_mode.currentIndexChanged.connect(self._on_blur_mode_changed)
            self._blur_delay_label = QLabel("Délai :")
            self._form.addRow(self._blur_delay_label, self.i_blur_delay)

            # ── Texte (visible seulement si Texte) ──
            self._text_section_label = self._add_section_label("📝 Texte")
            self.i_text_content = QLineEdit()
            self.i_text_content.setPlaceholderText("Contenu du texte")
            self._text_label = QLabel("Contenu :")
            self._text_widget = QWidget()
            self._form.addRow(self._text_label, self.i_text_content)

            # ── Contenu ──
            self._add_section_label("✍️ Contenu")
            self.i_caption = QLineEdit()
            self.i_caption.setPlaceholderText("Légende")
            # Bouton "Éditer" à côté de la légende pour coller n'importe quel texte
            caption_row = QHBoxLayout()
            caption_row.setSpacing(6)
            caption_row.addWidget(self.i_caption, stretch=1)
            self.btn_edit_caption = BounceButton("✏️ Éditer")
            self.btn_edit_caption.setFixedWidth(100)
            self.btn_edit_caption.setFixedHeight(32)
            self.btn_edit_caption.setToolTip("Ouvrir l'éditeur de texte avancé")
            self.btn_edit_caption.setStyleSheet(f"""
                QPushButton {{
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                    background-color: {self._t['bg_alt']};
                    color: {self._t['text']};
                    border: 1px solid {self._t['border_hover']};
                    border-radius: 8px; padding: 5px 12px;
                    font-size: 11px; font-weight: 600;
                }}
                QPushButton:hover {{ border-color: #0095f6; background-color: {self._t['border']}; }}
                QPushButton:pressed {{ background-color: {self._t['border_hover']}; }}
            """)
            self.btn_edit_caption.clicked.connect(self._open_caption_editor)
            caption_row.addWidget(self.btn_edit_caption)
            caption_w = QWidget(); caption_w.setLayout(caption_row)
            self._add_toggle_field("caption", "Légende", caption_w)

            # Hashtags (uniquement pour vidéo — masqué pour image/texte) — avec case à cocher
            self.i_tags = QLineEdit()
            self.i_tags.setPlaceholderText("#hashtags")
            self._add_toggle_field("tags", "Hashtags", self.i_tags, store_label_attr='_tags_toggle')

            # ── Profil ──
            self._add_section_label("👤 Profil")
            self.i_prof_name = QLineEdit()
            self.i_prof_name.setPlaceholderText("Nom (vide = cible)")
            self._add_toggle_field("prof_name", "Nom", self.i_prof_name)

            self.i_prof_pic = QLineEdit()
            self.i_prof_pic.setPlaceholderText("Photo de profil (optionnel)")
            _pic_widget, _ = self._make_browse_row(self.i_prof_pic, self._browse_pic)
            self._add_toggle_field("prof_pic", "Photo", _pic_widget)

            self.chk_verified = QCheckBox("✓ Compte vérifié")
            self._form.addRow("", self.chk_verified)

            # ── Engagement ──
            self._add_section_label("📊 Engagement")
            eng_row = QHBoxLayout()
            eng_row.setSpacing(6)
            self.i_likes = QLineEdit(); self.i_likes.setPlaceholderText("👍")
            self.i_comments = QLineEdit(); self.i_comments.setPlaceholderText("💬")
            self.i_shares = QLineEdit(); self.i_shares.setPlaceholderText("➤")
            eng_row.addWidget(self.i_likes)
            eng_row.addWidget(self.i_comments)
            eng_row.addWidget(self.i_shares)
            eng_w = QWidget(); eng_w.setLayout(eng_row)
            self._add_toggle_field("stats", "Stats", eng_w)

            self.chk_visible = QCheckBox("Visible dans le feed")
            self.chk_visible.setChecked(True)
            self._form.addRow("", self.chk_visible)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._build_fields", e)
            except Exception: pass

    def _make_browse_row(self, line_edit, callback):
        try:
            row = QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(line_edit, stretch=1)
            btn = BounceButton("🖼️ Parcourir")
            btn.setFixedHeight(32)
            btn.setMinimumWidth(110)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                    background-color: {self._t['bg_alt']};
                    color: {self._t['text']};
                    border: 1px solid {self._t['border_hover']};
                    border-radius: 8px; padding: 5px 12px;
                    font-size: 11px; font-weight: 600;
                }}
                QPushButton:hover {{ border-color: #0095f6; background-color: {self._t['border']}; }}
                QPushButton:pressed {{ background-color: {self._t['border_hover']}; }}
            """)
            btn.clicked.connect(callback)
            row.addWidget(btn)
            w = QWidget(); w.setLayout(row)
            return w, btn
        except Exception:
            return line_edit, None

    def _browse_media(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Média",
                "Médias (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.mp4 *.webm *.mov *.avi *.mkv *.flv *.m4v);;Tous les fichiers (*)", "ig")
            if m: self.i_source.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._browse_media", e)
            except Exception: pass

    def _browse_cover(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Couverture",
                "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "cov")
            if m: self.i_cover.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._browse_cover", e)
            except Exception: pass

    def _browse_pic(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Profil", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "prf")
            if m: self.i_prof_pic.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("IG._browse_pic", e)
            except Exception: pass

    def _open_caption_editor(self):
        """Ouvre l'éditeur de texte avancé pour permettre de coller n'importe quel texte."""
        try:
            current_text = self.i_caption.text()
            editor = TextEditorDialog(self, initial_text=current_text)
            if editor.exec() == QDialog.DialogCode.Accepted:
                new_text = editor.get_text()
                # Remplacer les retours à la ligne par des espaces pour le QLineEdit
                self.i_caption.setText(new_text.replace('\n', ' ').replace('\r', ' '))
        except Exception as e:
            try: from helpers import log_error; log_error("IG._open_caption_editor", e)
            except Exception: pass

    def _validate(self):
        try:
            if self.rb_text.isChecked():
                if not self.i_text_content.text().strip():
                    QMessageBox.warning(self, "Texte manquant", "Saisissez le contenu du texte.")
                    return
            else:
                if not self.i_source.text().strip():
                    QMessageBox.warning(self, "Média manquant", "Sélectionnez un média avant de valider.")
                    return
            self.accept()
        except Exception as e:
            try: from helpers import log_error; log_error("IG._validate", e)
            except Exception: pass
            self.accept()

    def _populate(self, d):
        try:
            ptype = d.get("type", "image")
            if ptype == "text": self.rb_text.setChecked(True)
            elif ptype == "video": self.rb_video.setChecked(True)
            else: self.rb_image.setChecked(True)
            self.i_source.setText(d.get("image", "") or "")
            self.i_cover.setText(d.get("video_cover", "") or "")
            self.chk_blur.setChecked(bool(d.get("blur_enabled", False)))
            self.i_blur_reason.setText(d.get("blur_reason", "") or "")
            self.i_blur_reason.setEnabled(self.chk_blur.isChecked())
            _bm = d.get("blur_mode", "instant") or "instant"
            for i in range(self.cmb_blur_mode.count()):
                if self.cmb_blur_mode.itemData(i) == _bm:
                    self.cmb_blur_mode.setCurrentIndex(i); break
            self.cmb_blur_mode.setEnabled(self.chk_blur.isChecked())
            self.i_blur_delay.setText(str(d.get("blur_delay", 3)))
            self._on_blur_mode_changed()
            self.i_text_content.setText(d.get("text", "") or d.get("caption", "") or "")
            self.i_caption.setText(d.get("caption", "") or "")
            self.i_tags.setText(d.get("tags", "") or "")
            self.i_prof_name.setText(d.get("profile_name", "") or "")
            self.i_prof_pic.setText(d.get("profile_pic", "") or "")
            self.chk_verified.setChecked(bool(d.get("verified", False)))
            self.i_likes.setText(str(d.get("likes", "") or ""))
            self.i_comments.setText(str(d.get("comments_count", d.get("comments", "")) or ""))
            self.i_shares.setText(str(d.get("shares_count", d.get("shares", "")) or ""))
            self.chk_visible.setChecked(bool(d.get("visible", True)))
            # Déclencher la mise à jour visuelle selon le type
            self._on_type_changed()
            # ── Restaurer les états des cases à cocher ──
            _saved_toggles = d.get("toggle_states", {}) or {}
            if hasattr(self, '_toggles') and _saved_toggles:
                for k, chk in self._toggles.items():
                    if k in _saved_toggles:
                        chk.setChecked(bool(_saved_toggles[k]))
        except Exception as e:
            try: from helpers import log_error; log_error("IG._populate", e)
            except Exception: pass

    def get_data(self):
        try:
            ptype = "text" if self.rb_text.isChecked() else ("video" if self.rb_video.isChecked() else "image")
            # ── Lire les valeurs selon l'état des cases à cocher ──
            caption = self.i_caption.text().strip() if self._is_toggle_on("caption") else ""
            # Hashtags uniquement pour vidéo ET si toggle est activé
            tags = self.i_tags.text().strip() if (ptype == "video" and self._is_toggle_on("tags")) else ""
            src = self.i_source.text().strip()
            text_content = self.i_text_content.text().strip()
            cover = self.i_cover.text().strip() if self._is_toggle_on("cover") else ""
            prof_name = self.i_prof_name.text().strip() if self._is_toggle_on("prof_name") else ""
            prof_pic = self.i_prof_pic.text().strip() if self._is_toggle_on("prof_pic") else ""

            if self._is_toggle_on("stats"):
                likes = self.i_likes.text().strip() or "0"
                comments = self.i_comments.text().strip() or "0"
                shares = self.i_shares.text().strip() or "0"
            else:
                likes = comments = shares = "0"

            toggle_states = {}
            if hasattr(self, '_toggles'):
                for k, chk in self._toggles.items():
                    toggle_states[k] = chk.isChecked()

            # ── Blur : pour les types non-vidéo, force le mode "instant" ──
            _blur_enabled = self.chk_blur.isChecked() if hasattr(self, 'chk_blur') else False
            _blur_reason = self.i_blur_reason.text().strip() if hasattr(self, 'chk_blur') and _blur_enabled else ""
            if ptype == "video":
                _blur_mode = self.cmb_blur_mode.currentData() if hasattr(self, 'cmb_blur_mode') and _blur_enabled else "instant"
                _blur_delay = int(self.i_blur_delay.text().strip()) if hasattr(self, 'i_blur_delay') and self.i_blur_delay.text().strip().isdigit() and _blur_enabled else 3
            else:
                # Non-vidéo → toujours instant, pas de délai
                _blur_mode = "instant"
                _blur_delay = 3

            # Si type texte, le contenu va dans text et caption
            if ptype == "text":
                full = (text_content + "\n" + tags).strip() if tags else text_content
                return {
                    "type": "text", "platform": "instagram",
                    "video_mode": "facebook_post",
                    "image": "", "video_cover": cover,
                    "blur_enabled": _blur_enabled,
                    "blur_reason": _blur_reason,
                    "blur_mode": _blur_mode,
                    "blur_delay": _blur_delay,
                    "profile_name": prof_name,
                    "profile_pic": prof_pic,
                    "verified": self.chk_verified.isChecked(),
                    "text": full, "caption": text_content, "tags": tags,
                    "music_name": "", "sound_name": "", "has_music": False,
                    "sound_image": "", "music_image": "",
                    "music_url": "", "sound_url": "", "has_sound_file": False,
                    "likes": likes,
                    "comments_count": comments,
                    "shares_count": shares,
                    "comments": comments,
                    "shares": shares,
                    "visible": self.chk_visible.isChecked(),
                    "audience": "Public", "time_ago": "À l'instant",
                    "fake_video": False, "sound_enabled": True,
                    "video_resolutions": [],
                    "toggle_states": toggle_states,
                }
            else:
                full = (caption + "\n" + tags).strip() if tags else caption
                return {
                    "type": ptype, "platform": "instagram",
                    "video_mode": "facebook_post",
                    "image": src, "video_cover": cover,
                    "blur_enabled": _blur_enabled,
                    "blur_reason": _blur_reason,
                    "blur_mode": _blur_mode,
                    "blur_delay": _blur_delay,
                    "profile_name": prof_name,
                    "profile_pic": prof_pic,
                    "verified": self.chk_verified.isChecked(),
                    "text": full, "caption": caption, "tags": tags,
                    "music_name": "", "sound_name": "", "has_music": False,
                    "sound_image": "", "music_image": "",
                    "music_url": "", "sound_url": "", "has_sound_file": False,
                    "likes": likes,
                    "comments_count": comments,
                    "shares_count": shares,
                    "comments": comments,
                    "shares": shares,
                    "visible": self.chk_visible.isChecked(),
                    "audience": "Public", "time_ago": "À l'instant",
                    "fake_video": False, "sound_enabled": True,
                    "video_resolutions": [],
                    "toggle_states": toggle_states,
                }
        except Exception as e:
            try: from helpers import log_error; log_error("IG.get_data", e)
            except Exception: pass
            return {}
