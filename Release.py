"""
Release.py — thin shim that re-exports every symbol from the
`release_parts` sub-package. Existing code that does:
    from Release import HTML_MOBILE
    import Release
continues to work unchanged. The actual content now lives in
release_parts/ as one file per logical element.
"""

from release_parts import (  # noqa: F401  (re-exports)
    ButtonStateManager,
    ReorderableListWidget,
    button_manager,
    log_error_to_file,
    TargetConfigWindow,
    ConfigWindow,
    ActiveTargetWindow,
    SandboxWindow,
    CredentialsWindow,
    CorbeilleWindow,
    PanneauAdmin,
)

__all__ = [
    "ButtonStateManager",
    "ReorderableListWidget",
    "button_manager",
    "log_error_to_file",
    "TargetConfigWindow",
    "ConfigWindow",
    "ActiveTargetWindow",
    "SandboxWindow",
    "CredentialsWindow",
    "CorbeilleWindow",
    "PanneauAdmin",
]


# ── Entry point preserved from original ──
# Direct imports needed only by the entry-point block below.
from release_parts import PanneauAdmin  # noqa: F401
import sys  # noqa: F401
from datetime import datetime  # noqa: F401
from PyQt6.QtWidgets import QApplication  # noqa: F401

if __name__ == "__main__":
    # ── Nettoyer le cache Python au démarrage ──
    # Supprime tous les dossiers __pycache__ et fichiers .pyc pour forcer
    # Python à recompiler les fichiers .py modifiés. Sans ça, les changements
    # de templates ne sont pas pris en compte si l'ancien cache est présent.
    try:
        import os as _os
        import shutil as _shutil
        _root_dir = _os.path.dirname(_os.path.abspath(__file__))
        for _dirpath, _dirnames, _filenames in _os.walk(_root_dir):
            for _dirname in _dirnames:
                if _dirname == "__pycache__":
                    _cache_path = _os.path.join(_dirpath, _dirname)
                    try:
                        _shutil.rmtree(_cache_path)
                    except Exception:
                        pass
            for _filename in _filenames:
                if _filename.endswith(".pyc"):
                    _pyc_path = _os.path.join(_dirpath, _filename)
                    try:
                        _os.remove(_pyc_path)
                    except Exception:
                        pass
    except Exception:
        pass

    import traceback as _tb_mod
    def _global_excepthook(exc_type, exc_value, tb):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Canonical error log file (consolidated with helpers.log_error)
            with open("errors_logs.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{timestamp}] UNHANDLED EXCEPTION\n")
                f.write(f"Type: {exc_type.__name__}\n")
                f.write(f"Value: {exc_value}\n")
                f.write("Traceback:\n")
                for line in "".join(_tb_mod.format_tb(tb)).strip().split("\n"):
                    f.write(f"  {line}\n")
                f.write(f"{'='*60}\n\n")
        except Exception as e:
            try:
                import sys as _sys
                _sys.stderr.write(f"[Release._global_excepthook] log failed: {e}\n")
            except Exception:
                pass
        import traceback as _tb2
        _tb2.print_exception(exc_type, exc_value, tb)
    sys.excepthook = _global_excepthook

    try:
        import faulthandler
        # Send segfault / deadlock dumps to the same canonical error log file
        _fh = open("errors_logs.txt", "a", encoding="utf-8")
        try:
            faulthandler.enable(_fh)
        except Exception:
            _fh.close()
            raise
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release.faulthandler] {e}\n")
        except Exception:
            pass

    try:
        from PyQt6.QtCore import qInstallMessageHandler
        def _qt_msg(msg_type, ctx, message):
            try:
                # Filtrer les messages Wayland non critiques
                if "Wayland" in message or "wayland" in message:
                    return
                if "opacity" in message and "plugin" in message:
                    return
                with open("errors_logs.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [Qt] {message}\n")
            except Exception as e:
                try:
                    import sys as _sys
                    _sys.stderr.write(f"[Release._qt_msg] {e}\n")
                except Exception:
                    pass
        qInstallMessageHandler(_qt_msg)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release.qInstallMessageHandler] {e}\n")
        except Exception:
            pass

    app_qt = QApplication(sys.argv)

    # ── Définir l'icône de l'application ──
    # Affichée dans la barre des tâches, le titre de fenêtre, alt-tab, etc.
    # L'icône est recherchée dans assets/app_icon.png (mode source)
    # ou dans le bundle PyInstaller (sys._MEIPASS).
    try:
        from widgets_parts.app_icon import set_application_icon
        set_application_icon(app_qt)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release] set app icon failed: {e}\n")
        except Exception:
            pass

    # Apply the saved theme color globally (blue / green / red / purple).
    try:
        from theme import apply_theme
        apply_theme(app_qt)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release] theme apply failed: {e}\n")
        except Exception:
            pass

    # ── Migrate existing credential files to encrypted if enabled ──
    # Only credentials JSON files are encrypted. Error logs stay plaintext (performance).
    try:
        import config as _cfg_startup
        if _cfg_startup.is_encrypt_files():
            import os, glob
            from crypto import is_encrypted, encrypt_text

            # Encrypt credential JSON files
            try:
                import credentials_manager as cm
                for _tid, cred_dir in cm._iter_all_cred_dirs():
                    if not os.path.isdir(cred_dir):
                        continue
                    for fpath in glob.glob(os.path.join(cred_dir, "*.json")):
                        try:
                            with open(fpath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            if content and not is_encrypted(content):
                                encrypted = encrypt_text(content)
                                with open(fpath, 'w', encoding='utf-8') as f:
                                    f.write(encrypted)
                        except Exception:
                            pass
            except Exception:
                pass
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release] encryption migration failed: {e}\n")
        except Exception:
            pass

    # ── Migration automatique des identifiants depuis credentials.txt ──
    # Parse le fichier legacy credentials.txt et range chaque bloc de capture
    # dans le dossier credentials/ de la cible correspondante. Idempotent par cible.
    try:
        import credentials_manager as _cm_startup
        _mig_result = _cm_startup.migrate_from_txt(force=False)
        _mig_count = _mig_result.get("migrated", 0) if isinstance(_mig_result, dict) else 0
        if _mig_count > 0:
            try:
                import sys as _sys
                _sys.stderr.write(
                    f"[Release] Migration credentials.txt → {int(_mig_count)} session(s) créée(s).\n"
                )
            except Exception:
                pass
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release] credentials.txt migration failed: {e}\n")
        except Exception:
            pass

    win = PanneauAdmin()

    # ── Appliquer l'icône à la fenêtre principale ──
    # (en plus de l'icône application, certaines plateformes Linux/Wayland
    # nécessitent que l'icône soit aussi définie sur la fenêtre elle-même)
    try:
        from widgets_parts.app_icon import set_app_icon
        set_app_icon(win)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[Release] set window icon failed: {e}\n")
        except Exception:
            pass

    win.show()
    sys.exit(app_qt.exec())
