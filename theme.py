"""
theme.py — Centralized theme system for the application.

Provides 4 dark themes (blue, green, red, purple) that can be applied globally
to all windows and buttons via QApplication.setStyleSheet().

The global stylesheet uses class-based selectors (QWidget, QPushButton, etc.).
Per-widget stylesheets set via setStyleSheet() in existing code continue to work
— they override the global theme for the widgets that have them. The theme
provides the BASE look (backgrounds, base text, borders) for everything else.

Public API:
  THEMES                  → dict of all themes
  get_theme()             → current theme dict
  generate_global_stylesheet() → QSS string for the current theme
  apply_theme(app)        → apply the current theme to a QApplication
  refresh_theme()         → re-apply the current theme (call after settings change)
"""

import sys
import traceback


# ═══════════════════════ Theme definitions ═══════════════════════
# Each theme defines a coherent dark palette. The structure is identical
# across themes so the generated QSS is consistent.
THEMES = {
    "blue": {
        "name": "Bleu sombre",
        "icon": "🔵",
        "bg": "#0F172A",
        "bg_alt": "#1E293B",
        "bg_card": "#1E293B",
        "bg_input": "#0F172A",
        "border": "#334155",
        "border_hover": "#475569",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "accent_pressed": "#1d4ed8",
        "accent_text": "#60a5fa",
        "text": "#E2E8F0",
        "text_dim": "#94A3B8",
        "text_muted": "#64748b",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
    },
    "green": {
        "name": "Vert sombre",
        "icon": "🟢",
        "bg": "#0a1f12",
        "bg_alt": "#0f2918",
        "bg_card": "#0f2918",
        "bg_input": "#0a1f12",
        "border": "#1f4d2e",
        "border_hover": "#2d6845",
        "accent": "#22c55e",
        "accent_hover": "#16a34a",
        "accent_pressed": "#15803d",
        "accent_text": "#4ade80",
        "text": "#dcfce7",
        "text_dim": "#86efac",
        "text_muted": "#4ade80",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
    },
    "red": {
        "name": "Rouge sombre",
        "icon": "🔴",
        "bg": "#1f0a0a",
        "bg_alt": "#2a0f0f",
        "bg_card": "#2a0f0f",
        "bg_input": "#1f0a0a",
        "border": "#4d1f1f",
        "border_hover": "#682d2d",
        "accent": "#ef4444",
        "accent_hover": "#dc2626",
        "accent_pressed": "#b91c1c",
        "accent_text": "#f87171",
        "text": "#fee2e2",
        "text_dim": "#fca5a5",
        "text_muted": "#f87171",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
    },
    "purple": {
        "name": "Violet sombre",
        "icon": "🟣",
        "bg": "#1a0a24",
        "bg_alt": "#250f33",
        "bg_card": "#250f33",
        "bg_input": "#1a0a24",
        "border": "#3d1f4d",
        "border_hover": "#522d68",
        "accent": "#a855f7",
        "accent_hover": "#9333ea",
        "accent_pressed": "#7e22ce",
        "accent_text": "#c084fc",
        "text": "#f3e8ff",
        "text_dim": "#d8b4fe",
        "text_muted": "#c084fc",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
    },
}


def _log_err(context, error):
    """Log a theme error to stderr + errors_logs.txt + victim logs (debug mode).
    Kept independent from helpers.py to avoid circular imports during early startup."""
    try:
        sys.stderr.write(f"[theme.{context}] {error}\n{traceback.format_exc()}\n")
    except Exception:
        pass
    try:
        from helpers import log_error
        log_error(f"theme.{context}", error)
    except Exception:
        pass


# Constante partagée pour la police emoji (utilisée dans tous les btn_style_*)
_EMOJI_FONT = "'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', Arial"


def get_theme():
    """Return the current theme dict. Falls back to 'blue' on any error."""
    try:
        from config import get_theme_color
        color_key = get_theme_color()
        if color_key not in THEMES:
            color_key = "blue"
        return THEMES[color_key]
    except Exception as e:
        _log_err("get_theme", e)
        return THEMES["blue"]


def generate_global_stylesheet():
    """Generate the global QSS stylesheet for the current theme.
    Uses class-based selectors so per-widget stylesheets still override
    individual properties (cascade behavior)."""
    try:
        t = get_theme()
        return f"""
        /* ── Base widgets ── */
        QWidget {{
            background-color: {t['bg']};
            color: {t['text']};
            font-size: 12px;
        }}
        QMainWindow, QDialog {{
            background-color: {t['bg']};
        }}

        /* ── Buttons ── */
        QPushButton {{
            background-color: {t['bg_alt']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: normal;
        }}
        QPushButton:hover {{
            background-color: {t['border_hover']};
            border-color: {t['accent']};
            color: {t['accent_text']};
        }}
        QPushButton:pressed {{
            background-color: {t['border']};
        }}
        QPushButton:disabled {{
            background-color: {t['bg_alt']};
            color: {t['text_muted']};
            border-color: {t['border']};
        }}

        /* ── Input widgets ── */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {t['bg_input']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 8px 10px;
            selection-background-color: {t['accent']};
            selection-color: white;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {t['accent']};
        }}
        QLineEdit:read-only {{
            color: {t['text_dim']};
            background-color: {t['bg_alt']};
        }}

        /* ── ComboBox ── */
        QComboBox {{
            background-color: {t['bg_alt']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 8px 12px;
            min-height: 18px;
        }}
        QComboBox:hover {{
            border-color: {t['accent']};
        }}
        QComboBox:focus {{
            border-color: {t['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 28px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {t['accent_text']};
            width: 0;
            height: 0;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['bg']};
            color: {t['text']};
            border: 1px solid {t['accent']};
            border-radius: 6px;
            padding: 6px;
            outline: none;
            selection-background-color: {t['accent']};
            selection-color: white;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 14px;
            border-radius: 4px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {t['bg_alt']};
            color: {t['accent_text']};
        }}

        /* ── GroupBox ── */
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

        /* ── Labels ── */
        QLabel {{
            color: {t['text']};
            background: transparent;
            border: none;
        }}

        /* ── ScrollArea ── */
        QScrollArea {{
            background-color: {t['bg']};
            border: 1px solid {t['border']};
            border-radius: 8px;
        }}
        QScrollBar:vertical {{
            background: {t['bg_alt']};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {t['border_hover']};
            min-height: 30px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['accent']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            border: none;
        }}
        QScrollBar:horizontal {{
            background: {t['bg_alt']};
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {t['border_hover']};
            min-width: 30px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {t['accent']};
        }}

        /* ── List widgets ── */
        QListWidget {{
            background-color: {t['bg_alt']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 4px;
        }}
        QListWidget::item {{
            background-color: transparent;
            border: none;
            margin-bottom: 4px;
            padding: 4px;
        }}
        QListWidget::item:hover {{
            background-color: {t['bg_input']};
            border-radius: 4px;
        }}
        QListWidget::item:selected {{
            background-color: {t['accent']};
            color: white;
            border-radius: 4px;
        }}

        /* ── Tabs ── */
        QTabWidget::pane {{
            border: 1px solid {t['border']};
            border-radius: 8px;
            background-color: {t['bg']};
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: {t['bg_alt']};
            color: {t['text_dim']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background-color: {t['border']};
            color: {t['accent_text']};
        }}
        QTabBar::tab:hover {{
            background-color: {t['border_hover']};
            color: {t['text']};
        }}

        /* ── CheckBox & RadioButton ── */
        QCheckBox, QRadioButton {{
            color: {t['text']};
            spacing: 6px;
            background: transparent;
            border: none;
        }}
        QCheckBox:hover, QRadioButton:hover {{
            color: {t['accent_text']};
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {t['border_hover']};
            background: {t['bg_input']};
        }}
        QCheckBox::indicator:checked {{
            background: {t['accent']};
            border-color: {t['accent']};
        }}
        QRadioButton::indicator {{
            border-radius: 9px;
        }}
        QRadioButton::indicator:checked {{
            background: {t['accent']};
            border-color: {t['accent']};
        }}

        /* ── Menu ── */
        QMenu {{
            background-color: {t['bg_alt']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {t['accent']};
            color: white;
        }}
        QMenu::separator {{
            height: 1px;
            background: {t['border']};
            margin: 4px 8px;
        }}

        /* ── ToolTip ── */
        QToolTip {{
            background-color: {t['bg_alt']};
            color: {t['text']};
            border: 1px solid {t['accent']};
            border-radius: 4px;
            padding: 6px 10px;
        }}

        /* ── Frame ── */
        QFrame {{
            background-color: transparent;
            border: none;
        }}

        /* ── StatusBar ── */
        QStatusBar {{
            background-color: {t['bg_alt']};
            color: {t['text_dim']};
            border-top: 1px solid {t['border']};
        }}

        /* ── ProgressBar ── */
        QProgressBar {{
            background-color: {t['bg_input']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            text-align: center;
            color: {t['text']};
        }}
        QProgressBar::chunk {{
            background-color: {t['accent']};
            border-radius: 3px;
        }}

        /* ── Slider ── */
        QSlider::groove:horizontal {{
            background: {t['bg_input']};
            height: 4px;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {t['accent']};
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {t['accent_hover']};
        }}

        /* ── MessageBox ── */
        QMessageBox {{
            background-color: {t['bg']};
        }}
        QMessageBox QLabel {{
            color: {t['text']};
        }}
        """
    except Exception as e:
        _log_err("generate_global_stylesheet", e)
        # Return a minimal stylesheet as fallback
        return "QWidget { background-color: #0F172A; color: #E2E8F0; }"


def apply_theme(app):
    """Apply the current theme to a QApplication instance.
    Safe to call multiple times — clears and re-applies to force a refresh."""
    try:
        qss = generate_global_stylesheet()
        # Clear first, then re-apply — forces Qt to re-evaluate the stylesheet
        # on all widgets (otherwise some widgets keep their old style).
        app.setStyleSheet("")
        app.setStyleSheet(qss)
    except Exception as e:
        _log_err("apply_theme", e)


def refresh_theme():
    """Re-apply the current theme. Call this after the theme color changes
    in System Settings so all open windows pick up the new look.

    Walks all top-level widgets and calls _apply_theme_style() on every window
    that defines it. This re-builds each window's stylesheet with the new theme
    colors. Also forces a repaint of all ModernToggleSwitch widgets (which use
    custom painting and read theme colors at paint time)."""
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            apply_theme(app)
            # Walk all top-level windows and re-apply their per-window stylesheets
            # using the new theme colors. Each window class that has a
            # _apply_theme_style() method will rebuild its stylesheet.
            try:
                for w in app.topLevelWidgets():
                    _refresh_window_style(w)
            except Exception as e:
                _log_err("refresh_theme.refresh_windows", e)
            # Force every ModernToggleSwitch to repaint (custom paintEvent)
            try:
                for w in app.topLevelWidgets():
                    _repaint_toggles(w)
            except Exception as e:
                _log_err("refresh_theme.repaint_toggles", e)
    except Exception as e:
        _log_err("refresh_theme", e)


def _refresh_window_style(widget):
    """Recursively walk the widget tree and call _apply_theme_style() on every
    widget that defines it. This rebuilds per-window stylesheets with the new
    theme colors. Also refreshes publication/ad lists on TargetConfigWindow
    so the row colors pick up the new theme."""
    try:
        # If this widget has _apply_theme_style, call it (re-builds the stylesheet)
        if hasattr(widget, "_apply_theme_style") and callable(getattr(widget, "_apply_theme_style")):
            try:
                widget._apply_theme_style()
            except Exception as e:
                _log_err(f"_refresh_window_style.apply[{type(widget).__name__}]", e)
        # If this widget has refresh_pub_list (TargetConfigWindow), call it
        # so the publication rows pick up the new theme colors.
        if hasattr(widget, "refresh_pub_list") and callable(getattr(widget, "refresh_pub_list")):
            try:
                widget.refresh_pub_list()
            except Exception as e:
                _log_err(f"_refresh_window_style.refresh_pub_list[{type(widget).__name__}]", e)
        if hasattr(widget, "refresh_ad_list") and callable(getattr(widget, "refresh_ad_list")):
            try:
                widget.refresh_ad_list()
            except Exception as e:
                _log_err(f"_refresh_window_style.refresh_ad_list[{type(widget).__name__}]", e)
        # If this widget has rebuild_target_list (PanneauAdmin), call it
        if hasattr(widget, "rebuild_target_list") and callable(getattr(widget, "rebuild_target_list")):
            try:
                widget.rebuild_target_list()
            except Exception as e:
                _log_err(f"_refresh_window_style.rebuild_target_list[{type(widget).__name__}]", e)
        # If this widget has refresh_list (CorbeilleWindow), call it
        if hasattr(widget, "refresh_list") and callable(getattr(widget, "refresh_list")):
            try:
                widget.refresh_list()
            except Exception as e:
                _log_err(f"_refresh_window_style.refresh_list[{type(widget).__name__}]", e)
        # If this widget has refresh (CredentialsWindow), call it
        if hasattr(widget, "refresh") and callable(getattr(widget, "refresh")):
            try:
                widget.refresh()
            except Exception as e:
                _log_err(f"_refresh_window_style.refresh[{type(widget).__name__}]", e)
        # Recurse into children
        for child in widget.children():
            try:
                from PyQt6.QtWidgets import QWidget as _QWidget
                if isinstance(child, _QWidget):
                    _refresh_window_style(child)
            except Exception:
                pass
    except Exception as e:
        _log_err("_refresh_window_style", e)


def _repaint_toggles(widget):
    """Recursively walk the widget tree and call update() on every
    ModernToggleSwitch so its custom paintEvent re-reads theme colors."""
    try:
        # Check if this widget is a ModernToggleSwitch (duck-typed to avoid
        # an import cycle — toggle_switch.py imports from theme.py indirectly).
        if hasattr(widget, "paintEvent") and hasattr(widget, "is_on") and hasattr(widget, "_progress"):
            try:
                widget.update()
            except Exception:
                pass
        # Recurse into children
        for child in widget.children():
            try:
                # Only recurse into QWidget instances (skip layouts, etc.)
                from PyQt6.QtWidgets import QWidget as _QWidget
                if isinstance(child, _QWidget):
                    _repaint_toggles(child)
            except Exception:
                pass
    except Exception as e:
        _log_err("_repaint_toggles", e)


def get_available_themes():
    """Return a list of (key, label) tuples for all available themes.
    Used by the System Settings UI to populate the theme picker."""
    try:
        return [(key, f"{t['icon']} {t['name']}") for key, t in THEMES.items()]
    except Exception as e:
        _log_err("get_available_themes", e)
        return [("blue", "🔵 Bleu sombre")]


# ═══════════════════════ Button style helpers ═══════════════════════
# These helpers return QSS strings for individual buttons. They should be
# used in place of hardcoded colors so every button picks up the active theme.
# Semantic colors: "accent" (primary), "success" (green), "warning" (orange),
# "danger" (red). Each maps to the corresponding theme color.

def btn_style_accent():
    """Primary button — fond accent, coins 8px, effet profondeur."""
    try:
        t = get_theme()
        return f"""
            QPushButton {{
                font-family: {_EMOJI_FONT};
                background-color: {t['accent']}; color: white; border: none;
                font-weight: normal; border-radius: 8px; padding: 9px 18px;
            }}
            QPushButton:hover {{ background-color: {t['accent_hover']}; }}
            QPushButton:pressed {{ background-color: {t['accent_pressed']}; padding-top: 10px; }}
            QPushButton:disabled {{ background-color: {t['bg_alt']}; color: {t.get('text_muted', '#64748b')}; }}
        """
    except Exception as e:
        _log_err("btn_style_accent", e)
        return ""


def btn_style_success():
    """Success button — vert, coins 8px, effet profondeur."""
    try:
        t = get_theme()
        return f"""
            QPushButton {{
                font-family: {_EMOJI_FONT};
                background-color: {t['success']}; color: white; border: none;
                font-weight: normal; border-radius: 8px; padding: 10px 18px;
                min-height: 20px;
            }}
            QPushButton:hover {{ background-color: #16a34a; }}
            QPushButton:pressed {{ background-color: #15803d; padding-top: 11px; }}
            QPushButton:disabled {{ background-color: {t['bg_alt']}; color: {t.get('text_muted', '#64748b')}; }}
        """
    except Exception as e:
        _log_err("btn_style_success", e)
        return ""


def btn_style_warning():
    """Warning button — orange, coins 8px, effet profondeur."""
    try:
        t = get_theme()
        return f"""
            QPushButton {{
                font-family: {_EMOJI_FONT};
                background-color: {t['warning']}; color: white; border: none;
                font-weight: normal; border-radius: 8px; padding: 9px 18px;
            }}
            QPushButton:hover {{ background-color: #d97706; }}
            QPushButton:pressed {{ background-color: #b45309; padding-top: 10px; }}
            QPushButton:disabled {{ background-color: {t['bg_alt']}; color: {t.get('text_muted', '#64748b')}; }}
        """
    except Exception as e:
        _log_err("btn_style_warning", e)
        return ""


def btn_style_danger():
    """Danger button — rouge, coins 8px, effet profondeur."""
    try:
        t = get_theme()
        return f"""
            QPushButton {{
                font-family: {_EMOJI_FONT};
                background-color: {t['danger']}; color: white; border: none;
                font-weight: normal; border-radius: 8px; padding: 9px 18px;
            }}
            QPushButton:hover {{ background-color: #dc2626; }}
            QPushButton:pressed {{ background-color: #b91c1c; padding-top: 10px; }}
            QPushButton:disabled {{ background-color: {t['bg_alt']}; color: {t.get('text_muted', '#64748b')}; }}
        """
    except Exception as e:
        _log_err("btn_style_danger", e)
        return ""


def btn_style_neutral():
    """Neutral button — fond bg_alt, bordure subtile, coins 8px."""
    try:
        t = get_theme()
        return f"""
            QPushButton {{
                font-family: {_EMOJI_FONT};
                background-color: {t['bg_alt']}; color: {t['text']}; border: 1px solid {t['border_hover']};
                font-weight: normal; border-radius: 8px; padding: 9px 18px;
            }}
            QPushButton:hover {{ background-color: {t['border']}; border-color: {t['accent']}; color: {t['accent_text']}; }}
            QPushButton:pressed {{ background-color: {t['border_hover']}; }}
            QPushButton:disabled {{ background-color: {t['bg_alt']}; color: {t.get('text_muted', '#64748b')}; border-color: {t['border']}; }}
        """
    except Exception as e:
        _log_err("btn_style_neutral", e)
        return ""


def btn_style_icon(color_type="accent"):
    """Small icon button (32×32) — coins 6px, police emoji."""
    try:
        t = get_theme()
        color_map = {
            "accent":  (t['accent'],        t['accent_hover'],   t['accent_pressed']),
            "success": (t['success'],       "#16a34a",           "#15803d"),
            "warning": (t['warning'],       "#d97706",           "#b45309"),
            "danger":  (t['danger'],        "#dc2626",           "#b91c1c"),
            "neutral": (t['bg_alt'],        t['border_hover'],   t['border']),
        }
        bg, hover, pressed = color_map.get(color_type, color_map["accent"])
        text_color = "white" if color_type != "neutral" else t['text']
        border = "none" if color_type != "neutral" else f"1px solid {t['border_hover']}"
        return f"""
            QPushButton {{
                font-family: {_EMOJI_FONT};
                background-color: {bg}; color: {text_color}; border: {border};
                border-radius: 6px; padding: 0px; font-size: 15px; font-weight: normal;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{ background-color: {pressed}; }}
        """
    except Exception as e:
        _log_err("btn_style_icon", e)
        return ""


def list_widget_style():
    """QListWidget style — uses the theme's colors."""
    try:
        t = get_theme()
        return f"""
            QListWidget {{
                border: 1px solid {t['border']};
                border-radius: 6px;
                background-color: {t['bg_alt']};
                padding: 4px;
            }}
            QListWidget::item {{
                background-color: transparent;
                border: none;
                margin-bottom: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {t['border']};
                border-radius: 6px;
            }}
        """
    except Exception as e:
        _log_err("list_widget_style", e)
        return ""


def checkbox_style(color_var="accent"):
    """QCheckBox style — uses the theme's accent or a specified color.
    color_var can be: 'accent', 'success', 'warning', 'danger'."""
    try:
        t = get_theme()
        c = t.get(color_var, t['accent'])
        return f"""
            QCheckBox {{ color: {t['text']}; spacing: 8px; background: transparent; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid {t['border_hover']}; background: {t['bg_input']}; }}
            QCheckBox::indicator:checked {{ background: {c}; border: 2px solid {c}; }}
        """
    except Exception as e:
        _log_err("checkbox_style", e)
        return ""
