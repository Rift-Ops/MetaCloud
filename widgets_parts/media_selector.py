"""media_selector.py — auto-generated from widgets.py."""

import os
import base64
from PyQt6.QtWidgets import QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QRadioButton, QComboBox, QScrollArea, QFileDialog, QMenu, QInputDialog, QStyle, QStyleOptionButton, QGridLayout, QWidget, QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QFrame, QFormLayout, QStackedWidget
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation, pyqtSignal
from PyQt6.QtGui import QPainter, QCursor, QColor
from templates import FEED_COLORS, REACTIONS_MAP
from config import BASE_CONFIG as default_config

from ._header import QColor, QDialog, QFileDialog, QHBoxLayout, QLabel, QListWidget, QMessageBox, QPainter, QVBoxLayout, Qt, os
from .bounce_button import BounceButton

class MediaSelectorDialog(QDialog):
    def __init__(self, parent, tid, title, filter_str, prefix):
        super().__init__(parent)
        self.tid = tid
        self.prefix = prefix
        self.filter_str = filter_str
        self.selected_file = None
        
        self.setWindowTitle(title)
        # Le bouton URL s'affiche UNIQUEMENT pour le carousel d'images (prefix="car")
        # Les autres champs (couverture, profil, disque, etc.) supportent déjà
        # le collage direct d'URL dans le champ texte.
        try:
            _prefix = (prefix or "").strip().lower()
            self._is_carousel_selector = (_prefix == "car")
        except Exception:
            self._is_carousel_selector = False
        self.setFixedSize(500, 510 if self._is_carousel_selector else 450)
        self._apply_theme_style()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title)
        f = lbl_title.font()
        f.setPointSize(14)
        f.setBold(True)
        lbl_title.setFont(f)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        btn_import = BounceButton("📁 Importer un nouveau fichier")
        from theme import btn_style_accent as _bsa
        btn_import.setStyleSheet(_bsa())
        btn_import.setMinimumHeight(45)
        btn_import.clicked.connect(self.import_new_file)
        layout.addWidget(btn_import)
        
        # Bouton URL uniquement pour le carousel d'images du feed
        if self._is_carousel_selector:
            btn_url = BounceButton("🔗 Saisir une URL d'image")
            from theme import btn_style_accent as _bsa2
            btn_url.setStyleSheet(_bsa2())
            btn_url.setMinimumHeight(40)
            btn_url.clicked.connect(self.enter_url)
            layout.addWidget(btn_url)
        
        lbl_or = QLabel("— OU CHOISIR PARMI LES EXISTANTS —")
        lbl_or.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from theme import get_theme as _gt
        _t = _gt()
        lbl_or.setStyleSheet(f"color: {_t['text_muted']}; font-weight: bold; font-size: 12px; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(lbl_or)
        
        content_layout = QHBoxLayout()
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        self.list_widget.currentItemChanged.connect(self.update_preview)
        content_layout.addWidget(self.list_widget, 2)
        
        preview_pane = QVBoxLayout()
        lbl_preview_title = QLabel("Aperçu")
        lbl_preview_title.setStyleSheet(f"color: {_t['text_dim']}; font-weight: bold; font-size: 12px;")
        lbl_preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_pane.addWidget(lbl_preview_title)
        
        self.preview_lbl = QLabel()
        self.preview_lbl.setFixedSize(200, 200)
        self.preview_lbl.setStyleSheet(f"background-color: {_t['bg']}; border: 1px dashed {_t['border_hover']}; border-radius: 8px;")
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_pane.addWidget(self.preview_lbl)
        preview_pane.addStretch()
        content_layout.addLayout(preview_pane, 1)
        
        layout.addLayout(content_layout)
        
        self.populate_list()
        
        btn_layout = QHBoxLayout()
        btn_ok = BounceButton("✓ Valider")
        from theme import btn_style_success as _bss
        btn_ok.setStyleSheet(_bss())
        btn_ok.setMinimumHeight(40)
        btn_ok.clicked.connect(self.accept_selection)
        
        btn_cancel = BounceButton("✕ Annuler")
        from theme import btn_style_danger as _bsd
        btn_cancel.setStyleSheet(_bsd())
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _apply_theme_style(self):
        """Build and apply the dialog stylesheet using the current theme colors."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QDialog {{ background-color: {t['bg']}; border: 2px solid {t['border']}; border-radius: 12px; }}
                QLabel {{ color: {t['text']}; }}
                QListWidget {{ background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; border-radius: 8px; color: {t['text']}; padding: 5px; }}
                QListWidget::item {{ padding: 10px; border-bottom: 1px solid {t['border']}; }}
                QListWidget::item:selected {{ background-color: {t['accent']}; border-radius: 4px; color: white; }}
                QListWidget::item:hover {{ background-color: {t['border_hover']}; }}
            """)
            # Re-apply individual widgets
            from theme import btn_style_accent, btn_style_success, btn_style_danger
            if hasattr(self, 'preview_lbl') and self.preview_lbl:
                self.preview_lbl.setStyleSheet(f"background-color: {t['bg']}; border: 1px dashed {t['border_hover']}; border-radius: 8px;")
        except Exception as e:
            try:
                from helpers import log_error
                log_error("MediaSelectorDialog._apply_theme_style", e)
            except Exception:
                pass

    def populate_list(self):
        try:
            import os
            import re
            from config import get_video_dir
            video_dir = get_video_dir(self.tid)
            if not os.path.exists(video_dir):
                return
                
            files = []
            # Extraire toutes les extensions de tous les groupes du filter_str
            # Format: "Images (*.png *.jpg ...);;Tous les fichiers (*)"
            # On collecte uniquement les extensions réelles (*.ext), pas le wildcard *
            all_extensions = []
            for match in re.finditer(r'\(([^)]*)\)', self.filter_str):
                group_content = match.group(1).strip()
                for ext in group_content.split():
                    ext = ext.strip().lower()
                    if ext.startswith('*.'):
                        all_extensions.append(ext[1:])  # enlever le * → garde .png, .jpg, etc.

            for f in os.listdir(video_dir):
                # Filtrer par les extensions collectées
                if any(f.lower().endswith(ext) for ext in all_extensions):
                    path = os.path.join(video_dir, f)
                    files.append((f, os.path.getmtime(path)))
                    
            files.sort(key=lambda x: x[1], reverse=True)
            for f, _ in files:
                self.list_widget.addItem(f)
        except Exception as e:
            from helpers import log_error
            log_error('widgets.MediaSelectorDialog.populate', e)

    def update_preview(self, current, previous):
        from theme import get_theme as _gt
        _t = _gt()
        if not current:
            self.preview_lbl.clear()
            self.preview_lbl.setStyleSheet(f"background-color: {_t['bg']}; border: 1px dashed {_t['border_hover']}; border-radius: 8px;")
            return
        filename = current.text()
        from config import get_video_dir
        import os
        path = os.path.join(get_video_dir(self.tid), filename)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.tif', '.ico', '.avif', '.heif', '.heic', '.jfif', '.apng', '.mng')):
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.preview_lbl.setStyleSheet("background-color: transparent; border: none;")
                self.preview_lbl.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.preview_lbl.setText("Erreur image")
        elif filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            self.preview_lbl.setStyleSheet(f"background-color: {_t['bg_alt']}; border: 1px solid {_t['border_hover']}; border-radius: 8px;")
            self.preview_lbl.setText("🎵 Audio\n" + filename)
        elif filename.lower().endswith(('.mp4', '.webm', '.ogg', '.mov', '.avi')):
            import subprocess
            import tempfile
            self.preview_lbl.setStyleSheet("background-color: transparent; border: none;")
            
            # Temporary file to store the extracted frame
            tmp_img = os.path.join(tempfile.gettempdir(), f"thumb_{hash(path)}.jpg")
            
            # Extract frame at 00:00:01 if not already extracted
            if not os.path.exists(tmp_img):
                try:
                    subprocess.run([
                        'ffmpeg', '-y', '-i', path, 
                        '-ss', '00:00:01.000', 
                        '-vframes', '1', 
                        tmp_img
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                except subprocess.TimeoutExpired:
                    # ffmpeg trop lent pour cette vidéo — afficher un fallback
                    try:
                        from helpers import log_error
                        log_error("media_selector.ffmpeg_timeout", f"Timeout extracting thumbnail from: {filename}")
                    except Exception:
                        pass
                except Exception as e:
                    try:
                        from helpers import log_error
                        log_error("media_selector.ffmpeg_thumbnail", e)
                    except Exception:
                        pass
            
            if os.path.exists(tmp_img):
                from PyQt6.QtGui import QPixmap, QPainter, QColor
                pixmap = QPixmap(tmp_img)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    
                    # Draw a semi-transparent play overlay on the thumbnail
                    painter = QPainter(scaled)
                    painter.setBrush(QColor(0, 0, 0, 150))
                    painter.setPen(Qt.PenStyle.NoPen)
                    w, h = scaled.width(), scaled.height()
                    painter.drawEllipse(int(w/2 - 20), int(h/2 - 20), 40, 40)
                    painter.setBrush(QColor(255, 255, 255))
                    
                    # Draw play triangle
                    from PyQt6.QtGui import QPolygonF
                    from PyQt6.QtCore import QPointF
                    poly = QPolygonF([
                        QPointF(w/2 - 5, h/2 - 10),
                        QPointF(w/2 + 10, h/2),
                        QPointF(w/2 - 5, h/2 + 10)
                    ])
                    painter.drawPolygon(poly)
                    painter.end()
                    
                    self.preview_lbl.setPixmap(scaled)
                else:
                    self.preview_lbl.setStyleSheet(f"background-color: {_t['bg_alt']}; border: 1px solid {_t['border_hover']}; border-radius: 8px;")
                    self.preview_lbl.setText("🎬 Vidéo\n" + filename)
            else:
                self.preview_lbl.setStyleSheet(f"background-color: {_t['bg_alt']}; border: 1px solid {_t['border_hover']}; border-radius: 8px;")
                self.preview_lbl.setText("🎬 Vidéo\n" + filename)
        else:
            self.preview_lbl.setText("Aperçu non disponible")

    def enter_url(self):
        """Permet à l'utilisateur de saisir une URL d'image directement."""
        try:
            from PyQt6.QtWidgets import QInputDialog, QMessageBox
            url, ok = QInputDialog.getText(self, "URL d'image",
                "Collez l'URL de l'image (http:// ou https://) :",
                text="")
            if ok and url:
                url = url.strip()
                if not url:
                    QMessageBox.warning(self, "URL vide", "Veuillez saisir une URL valide.")
                    return
                # Accepter toute URL commençant par http:// ou https://
                # (même les URLs chiffrées/complexes avec paramètres)
                if not (url.startswith("http://") or url.startswith("https://")):
                    QMessageBox.warning(self, "URL invalide",
                        "L'URL doit commencer par http:// ou https://")
                    return
                self.selected_file = url
                self.accept()
        except Exception as e:
            try:
                from helpers import log_error
                log_error('widgets.MediaSelectorDialog.enter_url', e)
            except Exception:
                pass

    def import_new_file(self):
        try:
            import os, shutil, time, hashlib, re
            from config import get_video_dir
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            file_path, _ = QFileDialog.getOpenFileName(self, "Importer un fichier", "", self.filter_str)
            if file_path:
                video_dir = get_video_dir(self.tid)
                os.makedirs(video_dir, exist_ok=True)
                
                # Calculate hash of the new file
                hasher = hashlib.md5()
                with open(file_path, 'rb') as afile:
                    for chunk in iter(lambda: afile.read(4096), b""):
                        hasher.update(chunk)
                new_file_hash = hasher.hexdigest()
                
                # Extraire les extensions réelles du filter_str (même logique que populate_list)
                all_extensions = []
                for match in re.finditer(r'\(([^)]*)\)', self.filter_str):
                    group_content = match.group(1).strip()
                    for ext in group_content.split():
                        ext = ext.strip().lower()
                        if ext.startswith('*.'):
                            all_extensions.append(ext[1:])
                
                # Check against existing files
                for f in os.listdir(video_dir):
                    if any(f.lower().endswith(ext) for ext in all_extensions):
                        existing_path = os.path.join(video_dir, f)
                        try:
                            ex_hasher = hashlib.md5()
                            with open(existing_path, 'rb') as ex_file:
                                for chunk in iter(lambda: ex_file.read(4096), b""):
                                    ex_hasher.update(chunk)
                            if ex_hasher.hexdigest() == new_file_hash:
                                QMessageBox.information(self, "Fichier Existant", "Ce fichier a déjà été importé précédemment. Il a été sélectionné automatiquement depuis la galerie pour éviter les doublons.")
                                self.selected_file = f
                                self.accept()
                                return
                        except Exception as hash_err:
                            continue
                            
                # File is new, proceed with copying
                filename = os.path.basename(file_path)
                safe_filename = f"{self.prefix}_{int(time.time())}_{filename.replace(' ', '_')}"
                dest_path = os.path.join(video_dir, safe_filename)
                shutil.copy2(file_path, dest_path)
                self.selected_file = safe_filename
                self.accept()
        except Exception as e:
            from helpers import log_error
            log_error('widgets.MediaSelectorDialog.import', e)
            
    def accept_selection(self):
        from PyQt6.QtWidgets import QMessageBox
        item = self.list_widget.currentItem()
        if item:
            self.selected_file = item.text()
            self.accept()
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un média dans la liste ou importer un nouveau fichier.")

    @staticmethod
    def get_media(parent, tid, title, filter_str, prefix):
        dialog = MediaSelectorDialog(parent, tid, title, filter_str, prefix)
        if dialog.exec():
            return dialog.selected_file
        return None
