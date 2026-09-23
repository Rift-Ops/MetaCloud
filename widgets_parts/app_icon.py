"""app_icon.py — Gestion de l'icône de l'application MetaCloud.

Fournit des fonctions pour définir l'icône de la fenêtre principale et de
l'application, compatibles avec le mode source ET le mode PyInstaller compilé.

L'icône est recherchée dans plusieurs emplacements :
  1. <project_root>/assets/app_icon.png (mode source)
  2. <MEIPASS>/assets/app_icon.png (PyInstaller --onefile, extrait)
  3. <MEIPASS>/app_icon.png (PyInstaller --add-data "assets:.")
  4. <exec_dir>/assets/app_icon.png (PyInstaller --onedir)
  5. <exec_dir>/app_icon.png (fallback)
  6. <cwd>/assets/app_icon.png (dossier courant)

Sur Windows, .ico est utilisé en priorité ( requis par l'API Windows).
Sur Linux/macOS, .png est utilisé (QIcon supporte PNG nativement).
"""

import os
import sys

# Cache pour éviter de reparcourir le système de fichiers à chaque appel
_icon_path_cache = None  # None = pas encore cherché, "" = non trouvé, path = trouvé
_icon_path_checked = False


def _get_app_dir():
    """Retourne le dossier racine de l'application (compatible PyInstaller).

    En mode source : dossier parent du dossier contenant ce fichier
                     (ce fichier est dans widgets_parts/, on remonte d'un niveau)
    En mode PyInstaller : sys._MEIPASS (bundle extrait) ou dossier de l'exécutable
    """
    try:
        # Mode PyInstaller
        if getattr(sys, "frozen", False):
            if hasattr(sys, "_MEIPASS") and sys._MEIPASS:
                return sys._MEIPASS
            return os.path.dirname(os.path.abspath(sys.executable))
    except Exception:
        pass

    # Mode source : remonte d'un niveau depuis widgets_parts/
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(this_dir)
    except Exception:
        return os.getcwd()


def find_app_icon():
    """Cherche l'icône de l'application dans plusieurs emplacements.

    Returns:
        Chemin absolu vers l'icône, ou "" si non trouvée.
    """
    global _icon_path_cache, _icon_path_checked

    if _icon_path_checked:
        return _icon_path_cache

    _icon_path_checked = True
    _icon_path_cache = ""

    try:
        # Déterminer les noms de fichiers prioritaires selon l'OS
        if sys.platform == "win32":
            # Windows : .ico en priorité (requis par l'API Win32),
            # mais .png en fallback (QIcon peut le lire)
            filenames = ["app_icon.ico", "app_icon.png"]
        else:
            # Linux/macOS : .png en priorité (QIcon supporte PNG nativement)
            filenames = ["app_icon.png", "app_icon.ico"]

        app_dir = _get_app_dir()
        exec_dir = os.path.dirname(os.path.abspath(sys.executable)) if sys.executable else os.getcwd()

        # Construire la liste des chemins candidats, dans l'ordre de priorité
        candidates = []
        for fname in filenames:
            candidates.extend([
                # 1. assets/ dans le dossier de l'app (mode source ou PyInstaller)
                os.path.join(app_dir, "assets", fname),
                # 2.直接 à la racine de l'app
                os.path.join(app_dir, fname),
                # 3. assets/ à côté de l'exécutable (PyInstaller --onedir)
                os.path.join(exec_dir, "assets", fname),
                # 4. racine à côté de l'exécutable
                os.path.join(exec_dir, fname),
                # 5. assets/ dans le dossier courant
                os.path.join(os.getcwd(), "assets", fname),
                # 6. dossier courant
                os.path.join(os.getcwd(), fname),
            ])

        # Chemins Linux standards (installation système)
        if sys.platform.startswith("linux"):
            candidates.extend([
                "/usr/share/pixmaps/metacloud.png",
                "/usr/share/icons/hicolor/48x48/apps/metacloud.png",
                "/usr/share/icons/hicolor/128x128/apps/metacloud.png",
                "/usr/share/icons/hicolor/256x256/apps/metacloud.png",
                "/usr/share/icons/hicolor/512x512/apps/metacloud.png",
            ])

        # Chercher le premier fichier qui existe et est lisible
        for path in candidates:
            try:
                if path and os.path.isfile(path) and os.access(path, os.R_OK):
                    _icon_path_cache = path
                    return path
            except Exception:
                continue

        return ""
    except Exception:
        return ""


def set_app_icon(app_or_window):
    """Définit l'icône de l'application sur un QApplication ou un QMainWindow/QWidget.

    Args:
        app_or_window: instance de QApplication, QMainWindow, ou QWidget

    Returns:
        True si l'icône a été définie, False sinon.
    """
    try:
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import QApplication, QWidget

        icon_path = find_app_icon()
        if not icon_path:
            return False

        icon = QIcon(icon_path)
        if icon.isNull():
            return False

        # Si c'est un QApplication → définit l'icône par défaut pour toutes les fenêtres
        if isinstance(app_or_window, QApplication):
            app_or_window.setWindowIcon(icon)
            return True

        # Si c'est un QWidget/QMainWindow → définit l'icône de cette fenêtre
        if isinstance(app_or_window, QWidget):
            app_or_window.setWindowIcon(icon)
            return True

        # Fallback : si l'objet a une méthode setWindowIcon, l'appeler
        if hasattr(app_or_window, 'setWindowIcon'):
            app_or_window.setWindowIcon(icon)
            return True

        return False
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[app_icon.set_app_icon] {e}\n")
        except Exception:
            pass
        return False


def set_application_icon(app):
    """Définit l'icône de l'application (QApplication).

    À appeler après la création du QApplication dans Release.py.

    Args:
        app: instance de QApplication

    Returns:
        True si l'icône a été définie, False sinon.
    """
    return set_app_icon(app)


def apply_icon_to_all_windows():
    """Applique l'icône à toutes les fenêtres top-level actuellement ouvertes.

    Utile pour rafraîchir l'icône après un changement de thème ou après
    l'ouverture de nouvelles fenêtres.
    """
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return False

        icon_path = find_app_icon()
        if not icon_path:
            return False

        from PyQt6.QtGui import QIcon
        icon = QIcon(icon_path)
        if icon.isNull():
            return False

        # Appliquer à toutes les fenêtres top-level
        count = 0
        for widget in app.topLevelWidgets():
            try:
                widget.setWindowIcon(icon)
                count += 1
            except Exception:
                continue
        return count > 0
    except Exception:
        return False
