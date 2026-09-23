"""
pub_manager.py — Gestionnaire de publications séparées par fichiers JSON.

Chaque publication est stockée dans :
  targets/<target_id>/publications/<platform>/<index>.json

Le fichier principal targets/<target_id>.json ne contient plus
la clé "publications" — il contient juste la config générale.

Les publications sont organisées par dossier de plateforme :
  targets/<tid>/publications/facebook/0000.json
  targets/<tid>/publications/tiktok/0000.json
  targets/<tid>/publications/snapchat/0000.json
  targets/<tid>/publications/instagram/0000.json

Fonctions publiques :
  load_publications(target_id, platform=None)  → list[dict]
  save_publications(target_id, publications, platform=None)  → None
  migrate_from_json(target_id)  → bool
  migrate_to_per_platform(target_id)  → bool
  get_pub_dir(target_id, platform=None)  → str
"""

import os
import json
import glob
from datetime import datetime


def _log(ctx: str, error: Exception) -> None:
    """Écrit une ligne d'erreur dans errors_logs.txt (fichier canonique).

    Tente d'abord de déléguer à helpers.log_error() — qui gère aussi l'affichage
    en mode debug dans les logs des victimes + sandbox. Si helpers n'est pas
    importable (import circulaire au démarrage), on retombe sur une écriture
    directe dans errors_logs.txt.

    Error logs are NOT encrypted for performance (fast append)."""
    # 1) Try the high-level logger (handles debug-mode victim forwarding)
    try:
        from helpers import log_error as _hle
        _hle(f"pub_manager.{ctx}", error)
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
        line = f"[{ts}] [ERROR] pub_manager.{ctx}: {error}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as inner:
        try:
            import sys as _sys
            _sys.stderr.write(f"[pub_manager._log] {inner}\n")
        except Exception:
            pass


def get_pub_dir(target_id: str, platform: str = None) -> str:
    """Retourne le chemin absolu du dossier des publications pour une cible.
    Si platform est donné, retourne le sous-dossier de cette plateforme."""
    try:
        from config import TARGETS_DIR
        base = os.path.join(TARGETS_DIR, target_id, "publications")
        if platform:
            return os.path.join(base, platform)
        return base
    except Exception as e:
        _log("get_pub_dir", e)
        return os.path.join("targets", target_id, "publications")


def _ensure_pub_dir(target_id: str, platform: str = None) -> str:
    """Crée le dossier si absent et retourne son chemin."""
    d = get_pub_dir(target_id, platform)
    os.makedirs(d, exist_ok=True)
    return d


def _is_per_platform_layout(target_id: str) -> bool:
    """Vérifie si le dossier publications utilise déjà la structure par plateforme."""
    try:
        base = get_pub_dir(target_id)
        if not os.path.isdir(base):
            return False
        # S'il y a des sous-dossiers, c'est déjà per-platform
        for entry in os.listdir(base):
            if os.path.isdir(os.path.join(base, entry)):
                return True
        return False
    except Exception:
        return False


def load_publications(target_id: str, platform: str = None) -> list:
    """
    Charge les publications depuis les fichiers JSON individuels.

    Si platform est donné : charge uniquement les publications de cette plateforme
    depuis targets/<tid>/publications/<platform>/

    Si platform est None : charge TOUTES les publications de toutes les plateformes
    (utilisé pour la migration et le fallback).

    Retourne une liste vide en cas d'erreur.
    """
    try:
        # ── Si platform est spécifié, charger depuis le sous-dossier ──
        if platform:
            pub_dir = get_pub_dir(target_id, platform)
            if not os.path.isdir(pub_dir):
                return []
            return _load_json_files_from_dir(pub_dir)

        # ── platform=None : charger toutes les plateformes ──
        base = get_pub_dir(target_id)
        if not os.path.isdir(base):
            return []

        # Détecter la structure
        has_subdirs = False
        has_flat_json = False
        for entry in os.listdir(base):
            full = os.path.join(base, entry)
            if os.path.isdir(full):
                has_subdirs = True
            elif entry.endswith(".json"):
                has_flat_json = True

        all_pubs = []

        # Charger depuis les sous-dossiers (nouveau format)
        if has_subdirs:
            for entry in os.listdir(base):
                full = os.path.join(base, entry)
                if os.path.isdir(full):
                    all_pubs.extend(_load_json_files_from_dir(full))

        # Charger depuis les fichiers plats (ancien format — pour migration)
        if has_flat_json and not has_subdirs:
            all_pubs.extend(_load_json_files_from_dir(base))

        return all_pubs

    except Exception as e:
        _log("load_publications", e)
        return []


def _load_json_files_from_dir(dir_path: str) -> list:
    """Charge tous les fichiers JSON triés d'un dossier."""
    try:
        pattern = os.path.join(dir_path, "*.json")
        files = sorted(glob.glob(pattern))
        publications = []
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    pub = json.load(f)
                    publications.append(pub)
            except Exception as e:
                _log(f"_load_json_files[{os.path.basename(fpath)}]", e)
        return publications
    except Exception as e:
        _log("_load_json_files_from_dir", e)
        return []


def _write_pubs_to_dir(pub_dir, publications):
    """Écrit les publications de manière sûre : write-then-rename.

    1. Écrit chaque nouveau fichier avec un suffixe .tmp
    2. Supprime les anciens fichiers .json
    3. Renomme les .tmp en .json

    Cela évite la perte de données si une écriture échoue en cours de route.
    """
    tmp_files = []
    try:
        # Étape 1 : écrire les nouveaux fichiers avec suffixe .tmp
        for idx, pub in enumerate(publications):
            fname = f"{idx:04d}.json.tmp"
            fpath = os.path.join(pub_dir, fname)
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(pub, f, indent=4, ensure_ascii=False)
                tmp_files.append(fpath)
            except Exception as e:
                _log(f"save_publications[write:{fname}]", e)

        # Étape 2 : supprimer les anciens fichiers .json
        for old_file in glob.glob(os.path.join(pub_dir, "*.json")):
            try:
                os.remove(old_file)
            except Exception as e:
                _log(f"save_publications[remove:{os.path.basename(old_file)}]", e)

        # Étape 3 : renommer les .tmp en .json
        for tmp_path in tmp_files:
            final_path = tmp_path[:-4]  # retirer ".tmp"
            try:
                os.rename(tmp_path, final_path)
            except Exception as e:
                _log(f"save_publications[rename:{os.path.basename(tmp_path)}]", e)
    except Exception as e:
        _log("save_publications._write_pubs_to_dir", e)
        # Nettoyer les .tmp restants en cas d'erreur
        for tmp_path in tmp_files:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass


def save_publications(target_id: str, publications: list, platform: str = None) -> None:
    """
    Sauvegarde chaque publication dans son propre fichier JSON.

    Si platform est donné : sauvegarde uniquement dans le sous-dossier de cette
    plateforme, sans toucher aux autres plateformes.

    Si platform est None : sauvegarde dans le dossier plat (legacy).
    """
    try:
        if platform:
            # ── Sauvegarde par plateforme ──
            pub_dir = _ensure_pub_dir(target_id, platform)
            _write_pubs_to_dir(pub_dir, publications)
        else:
            # ── Legacy : sauvegarde dans le dossier plat ──
            pub_dir = _ensure_pub_dir(target_id)
            _write_pubs_to_dir(pub_dir, publications)

    except Exception as e:
        _log("save_publications", e)


def migrate_from_json(target_id: str) -> bool:
    """
    Migration automatique : si le fichier principal contient encore une
    clé "publications", elle est extraite et sauvegardée en fichiers séparés,
    puis supprimée du fichier principal.
    Retourne True si une migration a eu lieu, False sinon.
    """
    try:
        from config import TARGETS_DIR
        main_path = os.path.join(TARGETS_DIR, f"{target_id}.json")
        if not os.path.exists(main_path):
            return False

        with open(main_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "publications" not in data:
            return False  # Déjà migré ou rien à migrer

        publications = data.pop("publications", [])

        # Grouper par plateforme et sauvegarder
        by_platform = {}
        for pub in publications:
            p = pub.get("platform", "facebook")
            by_platform.setdefault(p, []).append(pub)

        for plat, pubs in by_platform.items():
            save_publications(target_id, pubs, plat)

        # Mettre à jour le fichier principal sans la clé publications
        with open(main_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True

    except Exception as e:
        _log("migrate_from_json", e)
        return False


def migrate_to_per_platform(target_id: str) -> bool:
    """
    Migration : si les publications sont encore dans le format plat
    (targets/<tid>/publications/*.json), les migrer vers le format par plateforme
    (targets/<tid>/publications/<platform>/*.json).
    Retourne True si une migration a eu lieu, False sinon.
    """
    try:
        base = get_pub_dir(target_id)
        if not os.path.isdir(base):
            return False

        # Vérifier s'il y a déjà des sous-dossiers (déjà migré)
        has_subdirs = any(os.path.isdir(os.path.join(base, e)) for e in os.listdir(base))
        if has_subdirs:
            return False  # Déjà en format per-platform

        # Charger les publications plates
        flat_pubs = _load_json_files_from_dir(base)
        if not flat_pubs:
            return False

        # Grouper par plateforme
        by_platform = {}
        for pub in flat_pubs:
            p = pub.get("platform", "facebook")
            by_platform.setdefault(p, []).append(pub)

        # Sauvegarder dans les sous-dossiers par plateforme
        for plat, pubs in by_platform.items():
            save_publications(target_id, pubs, plat)

        # Supprimer les anciens fichiers plats
        for old_file in glob.glob(os.path.join(base, "*.json")):
            try:
                os.remove(old_file)
            except Exception as e:
                _log(f"migrate_to_per_platform[remove:{os.path.basename(old_file)}]", e)

        return True

    except Exception as e:
        _log("migrate_to_per_platform", e)
        return False
