"""dialog.py — Fenêtre de création de publication TikTok.

Style unique : barre rouge TikTok, fond sombre, colonne unique compacte.
Champs essentiels uniquement : vidéo, couverture, légende, hashtags,
son, profil, engagement.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QFileDialog, QWidget, QScrollArea, QFrame,
    QMessageBox, QComboBox, QSizePolicy, QApplication,
    QListWidget, QListWidgetItem, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from widgets_parts.bounce_button import BounceButton
from widgets_parts.media_selector import MediaSelectorDialog
from widgets_parts.text_editor import TextEditorDialog


# ════════════════════════════════════════════════════════════════════
#  CarouselThumbnail — widget de miniature (une ligne horizontale)
#  Affiche l'image en grand + infos + boutons flou/supprimer
# ════════════════════════════════════════════════════════════════════


class CarouselThumbnail(QWidget):
    """Ligne horizontale: grande miniature + numéro + nom + boutons.
    Pas de drag manuel — le QListWidget parent gère le réordonnancement."""

    def __init__(self, index, img_path, blur_info, parent_dialog, list_widget):
        try:
            super().__init__()
            self._index = index
            self._img_path = img_path
            self._blur_info = blur_info
            self._parent_dialog = parent_dialog
            self._list_widget = list_widget

            self.setFixedHeight(90)
            self.setMinimumWidth(260)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            layout = QHBoxLayout(self)
            layout.setContentsMargins(6, 4, 6, 4)
            layout.setSpacing(8)

            # Thumbnail image (large enough to see clearly)
            self._lbl = QLabel()
            self._lbl.setFixedSize(110, 80)
            self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            is_blurred = blur_info.get("blur", False)
            if is_blurred:
                self._lbl.setStyleSheet("background: #2a1a1a; border-radius: 6px; border: 2px solid #ef4444;")
            else:
                self._lbl.setStyleSheet("background: #1a1a1a; border-radius: 6px; border: 1px solid #333;")
            self._load_thumbnail()
            layout.addWidget(self._lbl)

            # Right column: index + filename + buttons
            right_col = QVBoxLayout()
            right_col.setContentsMargins(0, 0, 0, 0)
            right_col.setSpacing(3)

            # Index label (includes blur reason if blurred)
            idx_text = f"#{index + 1}"
            if is_blurred:
                reason = blur_info.get('reason', '')
                idx_text += f"  •  🌫️ {reason}" if reason else "  •  🌫️ Flou"
            self._index_lbl = QLabel(idx_text)
            self._index_lbl.setStyleSheet("color: #ddd; font-size: 11px; font-weight: bold;")
            right_col.addWidget(self._index_lbl)

            # Filename (truncated) or URL indicator
            if img_path and (img_path.startswith("http://") or img_path.startswith("https://")):
                fname = "🔗 URL"
            else:
                fname = os.path.basename(img_path) if img_path else ""
                if len(fname) > 30:
                    fname = fname[:27] + "..."
            self._name_lbl = QLabel(fname)
            self._name_lbl.setStyleSheet("color: #888; font-size: 10px;")
            right_col.addWidget(self._name_lbl)

            # Button row
            btn_row = QHBoxLayout()
            btn_row.setSpacing(4)

            # Blur toggle button
            self._btn_blur = QPushButton("🌫️ Flou" if is_blurred else "👁️ Voir")
            self._btn_blur.setFixedHeight(24)
            self._btn_blur.setMinimumWidth(70)
            self._btn_blur.setToolTip(f"Flou: {'ON - ' + blur_info.get('reason', '') if is_blurred else 'OFF'}")
            if is_blurred:
                self._btn_blur.setStyleSheet(
                    "QPushButton { background: #f59e0b; color: white; border: none; border-radius: 4px; font-size: 10px; padding: 2px 8px; }"
                    "QPushButton:hover { background: #d97706; }")
            else:
                self._btn_blur.setStyleSheet(
                    "QPushButton { background: #374151; color: white; border: none; border-radius: 4px; font-size: 10px; padding: 2px 8px; }"
                    "QPushButton:hover { background: #4b5563; }")
            self._btn_blur.clicked.connect(self._on_blur_clicked)
            btn_row.addWidget(self._btn_blur)

            # Remove button
            self._btn_rm = QPushButton("✕ Retirer")
            self._btn_rm.setFixedHeight(24)
            self._btn_rm.setMinimumWidth(70)
            self._btn_rm.setStyleSheet(
                "QPushButton { background: #ef4444; color: white; border: none; border-radius: 4px; "
                "font-size: 10px; padding: 2px 8px; } QPushButton:hover { background: #dc2626; }")
            self._btn_rm.clicked.connect(self._on_remove_clicked)
            btn_row.addWidget(self._btn_rm)

            btn_row.addStretch()
            btn_w = QWidget()
            btn_w.setLayout(btn_row)
            right_col.addWidget(btn_w)
            right_col.addStretch()

            right_w = QWidget()
            right_w.setLayout(right_col)
            layout.addWidget(right_w, stretch=1)

        except Exception as e:
            try:
                from helpers import log_error
                log_error("CarouselThumbnail.__init__", e)
            except Exception:
                pass

    def _on_blur_clicked(self):
        """Blur button — find our current row in the list and toggle blur."""
        try:
            row = self._list_widget.indexAt(self.pos()).row()
            if row >= 0:
                self._parent_dialog._toggle_carousel_blur(row)
        except Exception as e:
            try: from helpers import log_error; log_error("CarouselThumbnail._on_blur_clicked", e)
            except Exception: pass

    def _on_remove_clicked(self):
        """Remove button — find our current row in the list and remove."""
        try:
            row = self._list_widget.indexAt(self.pos()).row()
            if row >= 0:
                self._parent_dialog._remove_carousel_image(row)
        except Exception as e:
            try: from helpers import log_error; log_error("CarouselThumbnail._on_remove_clicked", e)
            except Exception: pass

    def _load_thumbnail(self):
        """Charge l'image depuis le disque, ou affiche 'lien' pour les URLs."""
        try:
            full_path = self._img_path
            # Si c'est une URL, afficher "lien" au lieu de charger l'image
            if self._img_path and (self._img_path.startswith("http://") or self._img_path.startswith("https://")):
                self._lbl.setText("🔗\nlien")
                return
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
            pix = QPixmap(full_path)
            if not pix.isNull():
                self._lbl.setPixmap(pix.scaled(104, 74, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
            else:
                self._lbl.setText("IMG")
        except Exception:
            self._lbl.setText("IMG")


# ════════════════════════════════════════════════════════════════════
#  CarouselListWidget — QListWidget avec drag & drop natif (InternalMove)
#  Qt gère automatiquement le réordonnancement des éléments
# ════════════════════════════════════════════════════════════════════


class CarouselListWidget(QListWidget):
    """Liste verticale d'images avec drag-drop natif pour réordonner."""

    def __init__(self, parent_dialog):
        try:
            super().__init__()
            self._parent_dialog = parent_dialog
            # InternalMove = drag-drop natif pour réordonner les éléments
            self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
            self.setDropIndicatorShown(True)
            # Auto-scroll pendant le drag — permet de défiler vers le bas/haut
            # automatiquement quand on glisse un élément près des bords
            self.setAutoScroll(True)
            self.setAutoScrollMargin(40)  # 40px de marge pour déclencher l'auto-scroll
            # Pas de scroll horizontal, scroll vertical oui
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setFrameShape(QFrame.Shape.StyledPanel)
            self.setMinimumHeight(220)
            self.setMaximumHeight(320)
            self.setSpacing(2)
        except Exception as e:
            try: from helpers import log_error; log_error("CarouselListWidget.__init__", e)
            except Exception: pass

    def dropEvent(self, event):
        """Sur le drop, on laisse Qt réordonner visuellement, puis on
        resynchronise les listes internes _carousel_images et _carousel_blur."""
        try:
            super().dropEvent(event)
            self._parent_dialog._on_carousel_reordered()
        except Exception as e:
            try: from helpers import log_error; log_error("CarouselListWidget.dropEvent", e)
            except Exception: pass

class TikTokPublicationDialog(QDialog):
    """Éditeur de vidéo TikTok — style compact avec accent rouge."""

    def __init__(self, parent=None, pub_data=None, tid=None, platform="tiktok"):
        try:
            super().__init__(parent)
            self.tid = tid
            self.platform = "tiktok"
            self.setWindowTitle("TikTok — Nouvelle vidéo")
            self.setMinimumSize(520, 600)
            self.resize(540, 680)

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
        except Exception as e:
            try:
                from helpers import log_error
                log_error("TikTokPublicationDialog.__init__", e)
            except Exception:
                pass

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
                QLineEdit:focus {{ border: 2px solid #fe2c55; }}
                QCheckBox {{ color: {t['text']}; font-size: 12px; spacing: 6px; }}
                QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px;
                    border: 2px solid {t['border_hover']}; background: {t['bg_input']}; }}
                QCheckBox::indicator:checked {{ background: #fe2c55; border-color: #fe2c55; }}
                QScrollBar:vertical {{ border: none; background: {t['bg']}; width: 6px; }}
                QScrollBar::handle:vertical {{ background: {t['border_hover']}; border-radius: 3px; min-height: 20px; }}
                QPushButton {{ font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial; }}
            """)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._apply_style", e)
            except Exception: pass

    def _build_header(self):
        try:
            header = QFrame()
            header.setFixedHeight(48)
            header.setStyleSheet("QFrame { background-color: #fe2c55; border: none; }")
            lay = QHBoxLayout(header)
            lay.setContentsMargins(16, 0, 16, 0)
            lbl = QLabel("🎵  TikTok For You")
            lbl.setStyleSheet("color: #fff; font-size: 15px; font-weight: 800;")
            lay.addWidget(lbl)
            lay.addStretch()
            return header
        except Exception as e:
            try: from helpers import log_error; log_error("TT._build_header", e)
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
                    background-color: #fe2c55; color: #fff; border: none;
                    border-radius: 8px; padding: 8px 24px;
                    font-size: 13px; font-weight: 800;
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                }
                QPushButton:hover { background-color: #e0274d; }
                QPushButton:pressed { background-color: #c4213f; padding-top: 9px; }
            """)
            ok.clicked.connect(self._validate)
            lay.addStretch()
            lay.addWidget(cancel)
            lay.addWidget(ok)
            return lay
        except Exception as e:
            try: from helpers import log_error; log_error("TT._build_buttons", e)
            except Exception: pass
            return QHBoxLayout()

    def _add_section_label(self, text):
        try:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {self._t['text_dim']}; font-size: 11px; font-weight: 700; "
                              f"text-transform: uppercase; letter-spacing: 1px; margin-top: 6px;")
            self._form.addRow(lbl)
        except Exception:
            pass

    # ── Système de cases à cocher pour activer/désactiver les champs ──
    def _add_toggle_field(self, key, label_text, field_widget, default_checked=True):
        """Ajoute une ligne au formulaire avec une case à cocher comme label.
        Quand la case est décochée, le champ est désactivé et sa valeur
        ne sera pas sauvegardée dans get_data().
        
        Args:
            key: identifiant unique du champ (ex: 'cover', 'caption')
            label_text: texte affiché à côté de la case
            field_widget: widget du champ (QLineEdit ou QWidget composite)
            default_checked: état initial de la case
        
        Returns:
            la case à cocher (QCheckBox)
        """
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
            # Connecter le toggle pour activer/désactiver le champ
            chk.toggled.connect(lambda checked, k=key: self._on_toggle_changed(k, checked))
            self._form.addRow(chk, field_widget)
            # Appliquer l'état initial
            self._apply_toggle_state(key, default_checked)
            return chk
        except Exception as e:
            try: from helpers import log_error; log_error("TT._add_toggle_field", e)
            except Exception: pass
            self._form.addRow(label_text, field_widget)
            return None

    def _on_toggle_changed(self, key, checked):
        """Callback quand une case à cocher de champ est basculée."""
        try:
            self._apply_toggle_state(key, checked)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._on_toggle_changed", e)
            except Exception: pass

    def _apply_toggle_state(self, key, checked):
        """Active ou désactive le champ associé à une case à cocher."""
        try:
            widget = self._toggle_widgets.get(key)
            if widget is None:
                return
            self._set_widget_enabled_recursive(widget, checked)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._apply_toggle_state", e)
            except Exception: pass

    def _set_widget_enabled_recursive(self, widget, enabled):
        """Active/désactive un widget et tous ses enfants récursivement."""
        try:
            widget.setEnabled(enabled)
            # Si c'est un QWidget composite (avec layout), désactiver les enfants aussi
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
        """Vérifie si la case à cocher d'un champ est cochée.
        Retourne True si cochée ou si la case n'existe pas (par défaut activé)."""
        try:
            chk = self._toggles.get(key) if hasattr(self, '_toggles') else None
            if chk is None:
                return True
            return chk.isChecked()
        except Exception:
            return True

    def _on_blur_mode_changed(self):
        """Active/désactive le champ délai selon le mode de flou sélectionné."""
        try:
            is_delayed = self.cmb_blur_mode.currentData() == "delayed"
            self.i_blur_delay.setEnabled(is_delayed and self.chk_blur.isChecked())
            # Masquer/afficher le label et le champ via setVisible
            _delay_label = self._form.labelForField(self.i_blur_delay)
            if _delay_label:
                _delay_label.setVisible(is_delayed)
            self.i_blur_delay.setVisible(is_delayed)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._on_blur_mode_changed", e)
            except Exception: pass

    def _build_fields(self):
        try:
            # ── Initialiser les dictionnaires de toggles ──
            self._toggles = {}
            self._toggle_widgets = {}

            # ── Vidéo ──
            self._add_section_label("📹 Vidéo")
            self.i_source = QLineEdit()
            self.i_source.setPlaceholderText("URL ou fichier local")
            self._form.addRow("Source :", self._make_browse_row(self.i_source, self._browse_video))

            self.i_cover = QLineEdit()
            self.i_cover.setPlaceholderText("Couverture (optionnel)")
            self._add_toggle_field("cover", "Couverture", self._make_browse_row(self.i_cover, self._browse_cover))

            # ── Carousel d'images (optionnel) ──
            self._add_section_label("🖼️ Carousel d'images")
            self._carousel_images = []       # list of image paths
            self._carousel_blur = []         # list of dicts: {"blur": bool, "reason": str}
            self._carousel_thumbs = []
            car_container = QWidget()
            car_layout = QVBoxLayout(car_container)
            car_layout.setContentsMargins(0, 0, 0, 0)
            car_layout.setSpacing(6)
            # Carousel list widget with native drag-drop reordering (InternalMove)
            self._carousel_list = CarouselListWidget(self)
            car_layout.addWidget(self._carousel_list)
            # Button row
            car_btn_row = QHBoxLayout()
            car_btn_row.setSpacing(6)
            self.btn_add_carousel = BounceButton("➕ Ajouter image")
            self.btn_add_carousel.setFixedHeight(32)
            self.btn_add_carousel.clicked.connect(self._add_carousel_image)
            car_btn_row.addWidget(self.btn_add_carousel)
            self.btn_clear_carousel = BounceButton("🗑️ Tout effacer")
            self.btn_clear_carousel.setFixedHeight(32)
            self.btn_clear_carousel.clicked.connect(self._clear_carousel)
            car_btn_row.addWidget(self.btn_clear_carousel)
            car_btn_row.addStretch()
            car_btn_w = QWidget(); car_btn_w.setLayout(car_btn_row)
            car_layout.addWidget(car_btn_w)
            # Hidden field for data storage
            self.i_carousel = QLineEdit()
            self.i_carousel.setVisible(False)
            car_layout.addWidget(self.i_carousel)
            self._form.addRow("Images :", car_container)

            # ── Flou ──
            self._add_section_label("🌫️ Flou")
            self.chk_blur = QCheckBox("Floutter la vidéo")
            self.chk_blur.setToolTip("Active un flou sur la vidéo dans le feed.\nLa victime verra la raison + un bouton « Se connecter pour voir ».")
            self._form.addRow("", self.chk_blur)

            self.i_blur_reason = QLineEdit()
            self.i_blur_reason.setPlaceholderText("Raison affichée à la victime (ex: Contenu sensible)")
            self.i_blur_reason.setEnabled(False)
            self.chk_blur.toggled.connect(self.i_blur_reason.setEnabled)
            self._form.addRow("Raison :", self.i_blur_reason)

            # Mode de flou : immédiat ou après lecture
            self.cmb_blur_mode = QComboBox()
            self.cmb_blur_mode.addItem("Immédiat (flou direct)", "instant")
            self.cmb_blur_mode.addItem("Après lecture (son d'abord, puis flou)", "delayed")
            self.cmb_blur_mode.setEnabled(False)
            self.chk_blur.toggled.connect(self.cmb_blur_mode.setEnabled)
            self._form.addRow("Mode :", self.cmb_blur_mode)

            # Délai avant flou (visible seulement en mode "delayed")
            self.i_blur_delay = QLineEdit()
            self.i_blur_delay.setPlaceholderText("Délai en secondes (ex: 3)")
            self.i_blur_delay.setText("3")
            self.i_blur_delay.setMaximumWidth(80)
            self.i_blur_delay.setEnabled(False)
            self.chk_blur.toggled.connect(self.i_blur_delay.setEnabled)
            self.cmb_blur_mode.currentIndexChanged.connect(self._on_blur_mode_changed)
            self._form.addRow("Délai :", self.i_blur_delay)

            # ── Contenu ──
            self._add_section_label("✍️ Contenu")
            self.i_caption = QLineEdit()
            self.i_caption.setPlaceholderText("Légende")
            caption_row = QHBoxLayout()
            caption_row.setSpacing(6)
            caption_row.addWidget(self.i_caption, stretch=1)
            self.btn_edit_caption = BounceButton("✏️ Éditer")
            self.btn_edit_caption.setFixedWidth(100)
            self.btn_edit_caption.setToolTip("Ouvrir l'éditeur de texte avancé")
            self.btn_edit_caption.clicked.connect(self._open_caption_editor)
            caption_row.addWidget(self.btn_edit_caption)
            caption_w = QWidget()
            caption_w.setLayout(caption_row)
            self._add_toggle_field("caption", "Légende", caption_w)

            self.i_tags = QLineEdit()
            self.i_tags.setPlaceholderText("#fyp #viral #pourtoi")
            self._add_toggle_field("tags", "Hashtags", self.i_tags)

            # ── Son ──
            self._add_section_label("🎵 Son")
            self.i_sound = QLineEdit()
            self.i_sound.setPlaceholderText("Son original - @username")
            self._add_toggle_field("sound", "Titre", self.i_sound)

            self.i_sound_file = QLineEdit()
            self.i_sound_file.setPlaceholderText("Fichier audio (optionnel)")
            self._add_toggle_field("sound_file", "Audio", self._make_browse_row(self.i_sound_file, self._browse_sound))

            self.i_disc_image = QLineEdit()
            self.i_disc_image.setPlaceholderText("Image du disque (optionnel)")
            self._add_toggle_field("disc", "Disque", self._make_browse_row(self.i_disc_image, self._browse_disc))

            # ── Profil ──
            self._add_section_label("👤 Profil")
            self.i_prof_name = QLineEdit()
            self.i_prof_name.setPlaceholderText("Nom (vide = cible)")
            self._add_toggle_field("prof_name", "Nom", self.i_prof_name)

            self.i_prof_pic = QLineEdit()
            self.i_prof_pic.setPlaceholderText("Photo de profil (optionnel)")
            self._add_toggle_field("prof_pic", "Photo", self._make_browse_row(self.i_prof_pic, self._browse_pic))

            self.chk_verified = QCheckBox("✓ Compte vérifié")
            self._form.addRow("", self.chk_verified)

            # ── Engagement ──
            self._add_section_label("📊 Engagement")
            eng_row = QHBoxLayout()
            eng_row.setSpacing(6)
            self.i_likes = QLineEdit(); self.i_likes.setPlaceholderText("👍")
            self.i_comments = QLineEdit(); self.i_comments.setPlaceholderText("💬")
            self.i_shares = QLineEdit(); self.i_shares.setPlaceholderText("➤")
            self.i_favorites = QLineEdit(); self.i_favorites.setPlaceholderText("🔖")
            eng_row.addWidget(self.i_likes)
            eng_row.addWidget(self.i_comments)
            eng_row.addWidget(self.i_shares)
            eng_row.addWidget(self.i_favorites)
            eng_w = QWidget(); eng_w.setLayout(eng_row)
            self._add_toggle_field("stats", "Stats", eng_w)

            self.chk_visible = QCheckBox("Visible dans le feed")
            self.chk_visible.setChecked(True)
            self._form.addRow("", self.chk_visible)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._build_fields", e)
            except Exception: pass

    def _make_browse_row(self, line_edit, callback):
        try:
            row = QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(line_edit, stretch=1)
            btn = BounceButton("📂 Parcourir")
            btn.setFixedHeight(32)
            btn.setMinimumWidth(90)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._t['bg_alt']};
                    color: {self._t['text']};
                    border: 1px solid {self._t['border_hover']};
                    border-radius: 8px; padding: 5px 12px;
                    font-size: 11px; font-weight: 600;
                    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial;
                }}
                QPushButton:hover {{ border-color: #fe2c55; background-color: {self._t['border']}; }}
                QPushButton:pressed {{ background-color: {self._t['border_hover']}; }}
            """)
            btn.clicked.connect(callback)
            row.addWidget(btn)
            w = QWidget(); w.setLayout(row)
            return w
        except Exception:
            return line_edit

    def _browse_video(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Vidéo", "Vidéos (*.mp4 *.webm *.mov *.avi *.mkv *.flv *.m4v)", "vid")
            if m: self.i_source.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._browse_video", e)
            except Exception: pass

    def _browse_cover(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Couverture", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "cov")
            if m: self.i_cover.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._browse_cover", e)
            except Exception: pass

    def _add_carousel_image(self):
        """Ajoute une image au carousel via le sélecteur de médias."""
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Carousel", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "car")
            if m:
                if m not in self._carousel_images:
                    self._carousel_images.append(m)
                    self._carousel_blur.append({"blur": False, "reason": ""})
                    self._refresh_carousel_gallery()
                    self._sync_carousel_field()
                    self._update_media_visibility()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._add_carousel_image", e)
            except Exception: pass

    def _clear_carousel(self):
        """Efface toutes les images du carousel."""
        try:
            self._carousel_images = []
            self._carousel_blur = []
            self._refresh_carousel_gallery()
            self._sync_carousel_field()
            self._update_media_visibility()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._clear_carousel", e)
            except Exception: pass

    def _remove_carousel_image(self, idx):
        """Supprime une image du carousel par son index."""
        try:
            if 0 <= idx < len(self._carousel_images):
                self._carousel_images.pop(idx)
                if idx < len(self._carousel_blur):
                    self._carousel_blur.pop(idx)
                self._refresh_carousel_gallery()
                self._sync_carousel_field()
                self._update_media_visibility()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._remove_carousel_image", e)
            except Exception: pass

    def _toggle_carousel_blur(self, idx):
        """Bascule le flou sur une image du carousel et demande une raison."""
        try:
            if 0 <= idx < len(self._carousel_blur):
                current = self._carousel_blur[idx]
                if not current["blur"]:
                    # Activer le flou → demander une raison
                    from PyQt6.QtWidgets import QInputDialog
                    reason, ok = QInputDialog.getText(self, "Raison du flou",
                        f"Raison affichée à la victime pour l'image {idx + 1}:",
                        text=current["reason"] or "Contenu sensible")
                    if ok:
                        current["blur"] = True
                        current["reason"] = reason.strip() or "Contenu sensible"
                    else:
                        return  # Annulé
                else:
                    # Désactiver le flou
                    current["blur"] = False
                    current["reason"] = ""
                self._refresh_carousel_gallery()
                self._sync_carousel_field()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._toggle_carousel_blur", e)
            except Exception: pass

    def _update_media_visibility(self):
        """Masque les champs vidéo quand le carousel a des images, et vice-versa."""
        try:
            has_carousel = len(self._carousel_images) > 0
            # Masquer/afficher les champs vidéo
            _video_label = self._form.labelForField(self._media_widget) if hasattr(self, '_media_widget') else None
            if _video_label:
                _video_label.setVisible(not has_carousel)
            if hasattr(self, '_media_widget') and self._media_widget:
                self._media_widget.setVisible(not has_carousel)
            # Masquer/afficher la couverture
            _cover_label = self._form.labelForField(self.i_cover.parent()) if hasattr(self, 'i_cover') else None
            # La couverture reste visible même avec carousel (pour la cover de la vidéo fallback)
            # Masquer/afficher les champs de flou vidéo (pas pertinent si carousel)
            if hasattr(self, 'chk_blur') and self.chk_blur:
                _blur_chk_label = self._form.labelForField(self.chk_blur)
                if _blur_chk_label:
                    _blur_chk_label.setVisible(not has_carousel)
                self.chk_blur.setVisible(not has_carousel)
            for attr in ('i_blur_reason', 'cmb_blur_mode', 'i_blur_delay'):
                w = getattr(self, attr, None)
                if w:
                    _lbl = self._form.labelForField(w)
                    if _lbl:
                        _lbl.setVisible(not has_carousel)
                    w.setVisible(not has_carousel)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._update_media_visibility", e)
            except Exception: pass

    def _sync_carousel_field(self):
        """Synchronise le champ caché avec la liste interne (format JSON robuste).
        Utilise JSON pour éviter les problèmes avec les URLs contenant des | ou ||."""
        try:
            import json
            data = []
            for i, img in enumerate(self._carousel_images):
                blur_info = self._carousel_blur[i] if i < len(self._carousel_blur) else {"blur": False, "reason": ""}
                data.append({
                    "img": img,
                    "blur": blur_info.get("blur", False),
                    "reason": blur_info.get("reason", "")
                })
            self.i_carousel.setText(json.dumps(data))
        except Exception as e:
            try: from helpers import log_error; log_error("TT._sync_carousel_field", e)
            except Exception: pass
            try:
                self.i_carousel.setText('')
            except Exception:
                pass

    def _move_carousel_image(self, from_idx, to_idx):
        """Déplace une image du carousel de from_idx vers to_idx."""
        try:
            if 0 <= from_idx < len(self._carousel_images) and 0 <= to_idx < len(self._carousel_images) and from_idx != to_idx:
                # Move image
                img = self._carousel_images.pop(from_idx)
                self._carousel_images.insert(to_idx, img)
                # Move blur info
                if from_idx < len(self._carousel_blur):
                    blur = self._carousel_blur.pop(from_idx)
                    self._carousel_blur.insert(to_idx, blur)
                # Refresh gallery + sync
                self._refresh_carousel_gallery()
                self._sync_carousel_field()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._move_carousel_image", e)
            except Exception: pass

    def _refresh_carousel_gallery(self):
        """Reconstruit la liste des miniatures dans le QListWidget."""
        try:
            # Block signals to avoid triggering itemSelectionChanged during rebuild
            self._carousel_list.blockSignals(True)
            # Clear all existing items
            self._carousel_list.clear()
            self._carousel_thumbs = []
            # Add each image as a QListWidgetItem with a CarouselThumbnail widget
            for idx, img_path in enumerate(self._carousel_images):
                blur_info = self._carousel_blur[idx] if idx < len(self._carousel_blur) else {"blur": False, "reason": ""}
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 96))  # height for the thumbnail row
                thumb = CarouselThumbnail(idx, img_path, blur_info, self, self._carousel_list)
                self._carousel_list.addItem(item)
                self._carousel_list.setItemWidget(item, thumb)
                self._carousel_thumbs.append(thumb)
            self._carousel_list.blockSignals(False)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._refresh_carousel_gallery", e)
            except Exception: pass
            try:
                self._carousel_list.blockSignals(False)
            except Exception:
                pass

    def _on_carousel_reordered(self):
        """Appelé après un drag-drop dans le QListWidget pour resynchroniser
        les listes internes _carousel_images et _carousel_blur."""
        try:
            # Read new order from the list widgets
            new_images = []
            new_blur = []
            for i in range(self._carousel_list.count()):
                item = self._carousel_list.item(i)
                thumb = self._carousel_list.itemWidget(item)
                if thumb is not None:
                    new_images.append(thumb._img_path)
                    new_blur.append(thumb._blur_info)
            self._carousel_images = new_images
            self._carousel_blur = new_blur
            # Update the index labels and stored _index on each thumbnail
            for i in range(self._carousel_list.count()):
                item = self._carousel_list.item(i)
                thumb = self._carousel_list.itemWidget(item)
                if thumb is not None:
                    thumb._index = i
                    is_blurred = thumb._blur_info.get("blur", False)
                    idx_text = f"#{i + 1}"
                    if is_blurred:
                        reason = thumb._blur_info.get('reason', '')
                        idx_text += f"  •  🌫️ {reason}" if reason else "  •  🌫️ Flou"
                    thumb._index_lbl.setText(idx_text)
            # Sync the hidden field
            self._sync_carousel_field()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._on_carousel_reordered", e)
            except Exception: pass

    def _browse_sound(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Audio", "Audio (*.mp3 *.wav *.ogg *.m4a *.aac *.flac)", "snd")
            if m: self.i_sound_file.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._browse_sound", e)
            except Exception: pass

    def _browse_disc(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Disque", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "dsc")
            if m: self.i_disc_image.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._browse_disc", e)
            except Exception: pass

    def _browse_pic(self):
        try:
            m = MediaSelectorDialog.get_media(self, self.tid, "Profil", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)", "prf")
            if m: self.i_prof_pic.setText(m)
        except Exception as e:
            try: from helpers import log_error; log_error("TT._browse_pic", e)
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
            try: from helpers import log_error; log_error("TT._open_caption_editor", e)
            except Exception: pass

    def _validate(self):
        try:
            has_video = bool(self.i_source.text().strip())
            has_carousel = len(self._carousel_images) > 0
            if not has_video and not has_carousel:
                QMessageBox.warning(self, "Média manquant", "Sélectionnez une vidéo ou au moins une image pour le carousel.")
                return
            # Security: if music file/URL is provided (and sound_file toggle is on),
            # music name is required (and sound toggle must be on)
            if self._is_toggle_on("sound_file"):
                has_music_file = bool(self.i_sound_file.text().strip())
                if has_music_file and self._is_toggle_on("sound"):
                    has_music_name = bool(self.i_sound.text().strip())
                    if not has_music_name:
                        QMessageBox.warning(self, "Musique incomplète", "Vous avez sélectionné un fichier/lien musique mais vous n'avez pas mis le nom.\nVeuillez saisir le nom de la musique.")
                        return
            self.accept()
        except Exception as e:
            try: from helpers import log_error; log_error("TT._validate", e)
            except Exception: pass
            self.accept()

    def _populate(self, d):
        try:
            self.i_source.setText(d.get("image", "") or "")
            self.i_cover.setText(d.get("video_cover", "") or "")
            self.i_carousel.setText(d.get("carousel_images", "") or "")
            # Rebuild gallery from stored carousel_images
            _car_text = d.get("carousel_images", "") or ""
            self._carousel_images = []
            self._carousel_blur = []
            if _car_text:
                import json
                _parsed = False
                # Format JSON (nouveau, robuste)
                try:
                    data = json.loads(_car_text)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "img" in item:
                                self._carousel_images.append(item["img"])
                                self._carousel_blur.append({
                                    "blur": item.get("blur", False),
                                    "reason": item.get("reason", "")
                                })
                        _parsed = True
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass

                # Fallback: ancien format "img1||img2|blur:reason||img3"
                if not _parsed and "||" in _car_text:
                    for part in _car_text.split("||"):
                        part = part.strip()
                        if not part:
                            continue
                        if "|blur:" in part:
                            img, reason = part.split("|blur:", 1)
                            self._carousel_images.append(img.strip())
                            self._carousel_blur.append({"blur": True, "reason": reason.strip()})
                        else:
                            self._carousel_images.append(part)
                            self._carousel_blur.append({"blur": False, "reason": ""})
                    _parsed = True

                # Fallback: très ancien format "img1, img2, img3" (comma-separated)
                if not _parsed:
                    for p in _car_text.split(','):
                        p = p.strip()
                        if p:
                            self._carousel_images.append(p)
                            self._carousel_blur.append({"blur": False, "reason": ""})

            self._refresh_carousel_gallery()
            self._sync_carousel_field()
            self._update_media_visibility()
            self.chk_blur.setChecked(bool(d.get("blur_enabled", False)))
            self.i_blur_reason.setText(d.get("blur_reason", "") or "")
            self.i_blur_reason.setEnabled(self.chk_blur.isChecked())
            # Mode de flou
            _blur_mode = d.get("blur_mode", "instant") or "instant"
            for i in range(self.cmb_blur_mode.count()):
                if self.cmb_blur_mode.itemData(i) == _blur_mode:
                    self.cmb_blur_mode.setCurrentIndex(i)
                    break
            self.cmb_blur_mode.setEnabled(self.chk_blur.isChecked())
            # Délai
            self.i_blur_delay.setText(str(d.get("blur_delay", 3)))
            self._on_blur_mode_changed()
            self.i_caption.setText(d.get("caption", "") or d.get("text", "") or "")
            self.i_tags.setText(d.get("tags", "") or "")
            self.i_sound.setText(d.get("sound_name") or d.get("music_name", "") or "")
            self.i_sound_file.setText(d.get("music_url") or d.get("sound_url", "") or "")
            self.i_disc_image.setText(d.get("sound_image") or d.get("music_image", "") or "")
            self.i_prof_name.setText(d.get("profile_name", "") or "")
            self.i_prof_pic.setText(d.get("profile_pic", "") or "")
            self.chk_verified.setChecked(bool(d.get("verified", False)))
            self.i_likes.setText(str(d.get("likes", "") or ""))
            self.i_comments.setText(str(d.get("comments_count", d.get("comments", "")) or ""))
            self.i_shares.setText(str(d.get("shares_count", d.get("shares", "")) or ""))
            self.i_favorites.setText(str(d.get("favorites_count", d.get("favorites", "")) or ""))
            self.chk_visible.setChecked(bool(d.get("visible", True)))
            # ── Restaurer les états des cases à cocher ──
            _saved_toggles = d.get("toggle_states", {}) or {}
            if hasattr(self, '_toggles') and _saved_toggles:
                for k, chk in self._toggles.items():
                    if k in _saved_toggles:
                        chk.setChecked(bool(_saved_toggles[k]))
        except Exception as e:
            try: from helpers import log_error; log_error("TT._populate", e)
            except Exception: pass

    def get_data(self):
        try:
            # ── Lire les valeurs selon l'état des cases à cocher ──
            # Si une case est décochée, la valeur du champ est vide
            caption = self.i_caption.text().strip() if self._is_toggle_on("caption") else ""
            tags = self.i_tags.text().strip() if self._is_toggle_on("tags") else ""
            sound = self.i_sound.text().strip() if self._is_toggle_on("sound") else ""
            src = self.i_source.text().strip()
            cover = self.i_cover.text().strip() if self._is_toggle_on("cover") else ""
            sound_file = self.i_sound_file.text().strip() if self._is_toggle_on("sound_file") else ""
            disc = self.i_disc_image.text().strip() if self._is_toggle_on("disc") else ""
            prof_name = self.i_prof_name.text().strip() if self._is_toggle_on("prof_name") else ""
            prof_pic = self.i_prof_pic.text().strip() if self._is_toggle_on("prof_pic") else ""

            # Stats: si décoché, tout à "0"
            if self._is_toggle_on("stats"):
                likes = self.i_likes.text().strip() or "0"
                comments = self.i_comments.text().strip() or "0"
                shares = self.i_shares.text().strip() or "0"
                favorites = self.i_favorites.text().strip() or "0"
            else:
                likes = comments = shares = favorites = "0"

            full = (caption + "\n" + tags).strip() if tags else caption

            # Construire le dictionnaire des toggles pour sauvegarde
            toggle_states = {}
            if hasattr(self, '_toggles'):
                for k, chk in self._toggles.items():
                    toggle_states[k] = chk.isChecked()

            return {
                "type": "video", "platform": "tiktok",
                "video_mode": "tiktok_fullscreen",
                "image": src, "video_cover": cover,
                "carousel_images": self.i_carousel.text().strip(),
                "blur_enabled": self.chk_blur.isChecked(),
                "blur_reason": self.i_blur_reason.text().strip() if self.chk_blur.isChecked() else "",
                "blur_mode": self.cmb_blur_mode.currentData() if self.chk_blur.isChecked() else "instant",
                "blur_delay": int(self.i_blur_delay.text().strip()) if self.i_blur_delay.text().strip().isdigit() and self.chk_blur.isChecked() else 3,
                "profile_name": prof_name,
                "profile_pic": prof_pic,
                "verified": self.chk_verified.isChecked(),
                "text": full, "caption": caption, "tags": tags,
                "music_name": sound, "sound_name": sound, "has_music": bool(sound),
                "sound_image": disc,
                "music_image": disc,
                "music_url": sound_file,
                "sound_url": sound_file,
                "has_sound_file": bool(sound_file),
                "likes": likes,
                "comments_count": comments,
                "shares_count": shares,
                "favorites_count": favorites,
                "favorites": favorites,
                "comments": comments,
                "shares": shares,
                "visible": self.chk_visible.isChecked(),
                "audience": "Public", "time_ago": "À l'instant",
                "fake_video": False, "sound_enabled": True,
                "video_resolutions": [],
                "toggle_states": toggle_states,
            }
        except Exception as e:
            try: from helpers import log_error; log_error("TT.get_data", e)
            except Exception: pass
            return {}
