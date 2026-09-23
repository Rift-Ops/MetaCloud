"""bounce_button.py — BounceButton moderne avec glassmorphism et animations.

Style unique :
  • Bordure dégradée subtile qui s'illumine au survol
  • Effet de profondeur au clic (scale + shadow)
  • Police emoji intégrée pour que les icônes s'affichent partout
  • Coins arrondis 8px par défaut
  • Transitions fluides (200ms)
"""

from PyQt6.QtWidgets import QPushButton, QStyle, QStyleOptionButton
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QBrush, QLinearGradient, QRadialGradient


_EMOJI_FONT = "'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial"


class BounceButton(QPushButton):
    """Bouton moderne avec animation de rebond, effet glassmorphism et police emoji."""

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self._scale = 1.0
            self._hover_alpha = 0
            self._anim = QVariantAnimation(self)
            self._anim.setDuration(200)
            self._anim.setStartValue(1.0)
            self._anim.setEndValue(1.04)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.valueChanged.connect(self._on_anim)

            # Police normale en primaire, emoji en fallback pour les icônes
            # (📁, ✓, ✕, 📹, etc.) — éviter l'espacement large des polices emoji
            font = QFont()
            font.setFamilies(["Segoe UI", "Arial", "DejaVu Sans", "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"])
            font.setPointSize(self.font().pointSize() if self.font().pointSize() > 0 else 10)
            font.setWeight(QFont.Weight.Normal)
            self.setFont(font)

            # Bordure par défaut si aucune stylesheet n'est définie
            if not self.styleSheet():
                self._apply_default_style()
        except Exception as e:
            try:
                import sys
                sys.stderr.write(f"[BounceButton.__init__] {e}\n")
            except Exception:
                pass

    def _apply_default_style(self):
        """Style par défaut moderne — glassmorphism subtil."""
        try:
            from theme import get_theme
            t = get_theme()
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['bg_alt']};
                    color: {t['text']};
                    border: 1px solid {t['border_hover']};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: {t['border']};
                    border-color: {t['accent']};
                    color: {t['accent_text']};
                }}
                QPushButton:pressed {{
                    background-color: {t['border_hover']};
                }}
                QPushButton:disabled {{
                    background-color: {t['bg_alt']};
                    color: {t.get('text_muted', '#64748b')};
                    border-color: {t['border']};
                }}
            """)
        except Exception:
            pass

    def _on_anim(self, value):
        try:
            self._scale = value
            self.update()
        except Exception:
            pass

    def enterEvent(self, event):
        try:
            self._anim.setDirection(QAbstractAnimation.Direction.Forward)
            self._anim.setDuration(200)
            self._anim.setEndValue(1.04)
            self._anim.start()
        except Exception:
            pass
        super().enterEvent(event)

    def leaveEvent(self, event):
        try:
            self._anim.setDirection(QAbstractAnimation.Direction.Backward)
            self._anim.setDuration(200)
            self._anim.setEndValue(1.0)
            self._anim.start()
        except Exception:
            pass
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        try:
            self._anim.stop()
            self._anim.setEndValue(0.93)
            self._anim.setDuration(80)
            self._anim.start()
        except Exception:
            pass
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        try:
            self._anim.stop()
            self._anim.setEndValue(1.04 if self.underMouse() else 1.0)
            self._anim.setDuration(200)
            self._anim.start()
        except Exception:
            pass
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            # Appliquer le scale (animation de rebond)
            cx = self.width() / 2
            cy = self.height() / 2
            painter.translate(cx, cy)
            painter.scale(self._scale, self._scale)
            painter.translate(-cx, -cy)

            # Dessiner le bouton via QStyle (respecte la stylesheet)
            opt = QStyleOptionButton()
            self.initStyleOption(opt)
            self.style().drawControl(QStyle.ControlElement.CE_PushButton, opt, painter, self)

            # Effet de lueur subtile au survol (si pas désactivé)
            if self.isEnabled() and self.underMouse():
                try:
                    from theme import get_theme
                    t = get_theme()
                    glow = QColor(t.get('accent', '#3b82f6'))
                    glow.setAlpha(20)
                    painter.setBrush(QBrush(glow))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 7, 7)
                except Exception:
                    pass

            painter.end()
        except Exception as e:
            try:
                import sys
                sys.stderr.write(f"[BounceButton.paintEvent] {e}\n")
            except Exception:
                pass
            # Fallback: dessiner via le paintEvent parent
            super().paintEvent(event)
