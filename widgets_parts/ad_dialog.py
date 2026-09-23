"""ad_dialog.py — auto-generated from widgets.py."""

import os
import base64
from PyQt6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QRadioButton, QComboBox, QScrollArea, QFileDialog, QMenu, QInputDialog, QStyle, QStyleOptionButton, QGridLayout, QWidget, QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QFrame, QFormLayout, QStackedWidget
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation, pyqtSignal
from PyQt6.QtGui import QPainter, QCursor, QColor
from templates import FEED_COLORS, REACTIONS_MAP
from config import BASE_CONFIG as default_config

from ._header import QDialog, QFileDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QVBoxLayout, QWidget, os
from .bounce_button import BounceButton

class AdDialog(QDialog):
    def __init__(self, parent=None, ad_data=None, tid=None):
        super().__init__(parent)
        self.tid = tid
        self.setWindowTitle("Configuration de la Publicité")
        self.setMinimumSize(500, 650)
        self.setStyleSheet("""
            QDialog { background-color: #0F172A; color: #E2E8F0; }
            QGroupBox { border: 1px solid #334155; border-radius: 10px; margin-top: 15px; font-weight: bold; color: #38bdf8; padding-top: 15px; font-size: 13px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QLineEdit { background-color: #1E293B; border: 1px solid #475569; padding: 10px; border-radius: 6px; color: #FFFFFF; font-size: 13px; }
            QLabel { color: #94A3B8; font-weight: bold; font-size: 12px; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)

        # ====== GROUPE 1: VISUEL & CONTENU ======
        group_visuel = QGroupBox("🖼️ Visuel & Contenu Principal")
        lay_visuel = QVBoxLayout(group_visuel)
        lay_visuel.setSpacing(15)
        
        # Image
        lay_visuel.addWidget(QLabel("Image de la publicité :"))
        img_lay = QHBoxLayout()
        self.i_image = QLineEdit()
        self.i_image.setPlaceholderText("URL de l'image ou parcourir...")
        self.i_image.setMinimumHeight(40)
        btn_img = BounceButton("📂")
        btn_img.setFixedSize(40, 40)
        from theme import btn_style_accent as _bsa
        btn_img.setStyleSheet(_bsa())
        btn_img.clicked.connect(self.select_image)
        img_lay.addWidget(self.i_image)
        img_lay.addWidget(btn_img)
        lay_visuel.addLayout(img_lay)

        # Titre
        lay_visuel.addWidget(QLabel("Titre principal :"))
        self.i_title = QLineEdit()
        self.i_title.setPlaceholderText("Ex: Produit révolutionnaire")
        self.i_title.setMinimumHeight(40)
        lay_visuel.addWidget(self.i_title)

        # Description
        lay_visuel.addWidget(QLabel("Texte descriptif :"))
        self.i_desc = QLineEdit()
        self.i_desc.setPlaceholderText("Ex: Profitez de -50% aujourd'hui seulement")
        self.i_desc.setMinimumHeight(40)
        lay_visuel.addWidget(self.i_desc)

        layout.addWidget(group_visuel)

        # ====== GROUPE 2: ACTION & REDIRECTION ======
        group_action = QGroupBox("🔗 Action & Redirection")
        lay_action = QVBoxLayout(group_action)
        lay_action.setSpacing(15)

        # Label
        lay_action.addWidget(QLabel("Étiquette :"))
        self.i_label = QLineEdit()
        self.i_label.setText("Sponsorisé")
        self.i_label.setMinimumHeight(40)
        lay_action.addWidget(self.i_label)

        # CTA Text
        lay_action.addWidget(QLabel("Texte du Bouton :"))
        self.i_cta_text = QLineEdit()
        self.i_cta_text.setPlaceholderText("En savoir plus")
        self.i_cta_text.setMinimumHeight(40)
        lay_action.addWidget(self.i_cta_text)

        # URL Bouton
        lay_action.addWidget(QLabel("URL du Bouton (Lien affiché) :"))
        self.i_cta_url = QLineEdit()
        self.i_cta_url.setPlaceholderText("Ex: https://mon-site.com")
        self.i_cta_url.setMinimumHeight(40)
        lay_action.addWidget(self.i_cta_url)

        # Tracking URL
        lay_action.addWidget(QLabel("URL de redirection réelle / Tracking (Optionnel) :"))
        self.i_click_url = QLineEdit()
        self.i_click_url.setPlaceholderText("Lien final caché vers lequel envoyer la victime")
        self.i_click_url.setMinimumHeight(40)
        lay_action.addWidget(self.i_click_url)

        layout.addWidget(group_action)

        layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Boutons Valid/Annuler
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(15)
        btn_lay.setContentsMargins(20, 10, 20, 20)
        
        btn_ok = BounceButton("✓ Enregistrer")
        btn_ok.setMinimumHeight(45)
        from theme import btn_style_success as _bss
        btn_ok.setStyleSheet(_bss())
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = BounceButton("✕ Annuler")
        btn_cancel.setMinimumHeight(45)
        from theme import btn_style_danger as _bsd
        btn_cancel.setStyleSheet(_bsd())
        btn_cancel.clicked.connect(self.reject)
        
        btn_lay.addWidget(btn_ok)
        btn_lay.addWidget(btn_cancel)
        main_layout.addLayout(btn_lay)

        if ad_data:
            self.i_image.setText(ad_data.get("image_url", ""))
            self.i_title.setText(ad_data.get("title", ""))
            self.i_desc.setText(ad_data.get("description", ""))
            self.i_label.setText(ad_data.get("label", "Sponsorisé"))
            self.i_cta_text.setText(ad_data.get("cta_text", "En savoir plus"))
            self.i_cta_url.setText(ad_data.get("cta_url", ""))
            self.i_click_url.setText(ad_data.get("click_url", ""))

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng *.exr *.psd);;Tous les fichiers (*)")
        if file_path:
            try:
                import shutil, os, time
                from config import get_video_dir
                
                if self.tid:
                    video_dir = get_video_dir(self.tid)
                    os.makedirs(video_dir, exist_ok=True)
                    
                    filename = os.path.basename(file_path)
                    # Préfixe pour éviter conflits
                    safe_filename = f"ad_{int(time.time())}_{filename.replace(' ', '_')}"
                    
                    dest_path = os.path.join(video_dir, safe_filename)
                    shutil.copy2(file_path, dest_path)
                    
                    self.i_image.setText(safe_filename)
            except Exception as e:
                from helpers import log_error
                log_error('widgets', e)

    def get_data(self):
        try:
            return {
                "image_url": self.i_image.text(),
                "title": self.i_title.text(),
                "description": self.i_desc.text(),
                "label": self.i_label.text(),
                "cta_text": self.i_cta_text.text(),
                "cta_url": self.i_cta_url.text(),
                "click_url": self.i_click_url.text()
            }
        except Exception as e:
            from helpers import log_error
            log_error('widgets.get_data', e)
