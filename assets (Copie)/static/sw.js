// Service Worker - Background Progressive Cache
// Player gets its own network stream immediately (no waiting).
// A completely independent background fetch downloads & caches the full file,
// even while the video is paused. Seeks are served instantly from cache.

const CACHE_NAME = 'video-cache-v7';

// Path prefixes that should be cached progressively.
// IMPORTANT: we match on URL.pathname (not the full URL string), otherwise
// /proxy_video?url=https://cdn.example.com/video/clip.mp4 would falsely match
// the /video/ pattern (because the upstream URL contains /video/ after the
// browser decodes %2F → /).
const CACHEABLE_PATHS = ['/video/', '/video_route/', '/proxy_video'];

// Tracks URLs currently being downloaded to avoid duplicate fetches
const downloading = new Set();

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    let parsedUrl;
    try {
        parsedUrl = new URL(event.request.url);
    } catch (e) {
        return;
    }
    // Match on pathname ONLY — never on the full URL string, because the
    // query string of /proxy_video can contain anything (including "/video/").
    const pathname = parsedUrl.pathname;
    const isCacheable = CACHEABLE_PATHS.some(p => pathname === p || pathname.startsWith(p));
    if (!isCacheable) return;
    event.respondWith(handleCacheableRequest(event.request));
});

async function handleCacheableRequest(request) {
    const cache = await caches.open(CACHE_NAME);
    const cacheKey = new Request(request.url, { method: 'GET' });

    const cached = await cache.match(cacheKey);
    if (cached) {
        // Fully cached — serve sliced bytes instantly (seeking = instant)
        const rangeHeader = request.headers.get('Range');
        if (rangeHeader) return sliceResponse(cached, rangeHeader);
        return cached;
    }

    // Not yet cached:
    // 1. Pass player's request directly to network so playback starts immediately
    // 2. Start a SEPARATE background fetch to download & cache the full file
    //    This continues even when the video is paused (fully independent)
    bgCache(request.url, cache, cacheKey); // fire-and-forget

    return fetch(request); // player gets its own stream, no waiting
}

// Fully independent background download — not tied to the player's stream.
// The player can pause, seek, or close; this fetch keeps going.
async function bgCache(url, cache, cacheKey) {
    if (downloading.has(url)) return;
    downloading.add(url);
    try {
        // Fetch the whole file (no Range header = full content)
        const res = await fetch(new Request(url, { method: 'GET' }));
        if (!res || !res.ok) return;

        const contentType = res.headers.get('Content-Type') || 'video/mp4';
        const reader = res.body.getReader();
        const chunks = [];

        // Read all chunks — continues even if video player is paused/closed
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
        }

        // Assemble into a single ArrayBuffer
        const total = chunks.reduce((n, c) => n + c.byteLength, 0);
        const buf = new Uint8Array(total);
        let off = 0;
        for (const chunk of chunks) { buf.set(chunk, off); off += chunk.byteLength; }

        // Store in cache so future seeks are instant
        await cache.put(cacheKey, new Response(buf.buffer, {
            status: 200,
            headers: {
                'Content-Type': contentType,
                'Content-Length': String(total),
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'public, max-age=2592000',
            }
        }));
    } catch (_) {
        // Silently ignore — player is unaffected
    } finally {
        downloading.delete(url);
    }
}

// Slice a fully-cached file for instant Range/seek responses
async function sliceResponse(response, rangeHeader) {
    const buffer = await response.clone().arrayBuffer();
    const total = buffer.byteLength;
    const match = rangeHeader.match(/bytes=(\d*)-(\d*)/);
    if (!match) return response;
    const start = parseInt(match[1]) || 0;
    const end = match[2] !== '' ? parseInt(match[2]) : total - 1;
    const sliced = buffer.slice(start, end + 1);
    return new Response(sliced, {
        status: 206,
        headers: {
            'Content-Type': response.headers.get('Content-Type') || 'video/mp4',
            'Content-Range': `bytes ${start}-${end}/${total}`,
            'Content-Length': String(sliced.byteLength),
            'Accept-Ranges': 'bytes',
        }
    });
}
