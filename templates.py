"""
templates.py — thin shim that re-exports every symbol from the
`templates_parts` sub-package. Existing code that does:
    from templates import HTML_MOBILE
    import templates
continues to work unchanged. The actual content now lives in
templates_parts/ as one file per logical element.
"""

from templates_parts import (  # noqa: F401  (re-exports)
    JS_STRICT_CAPTURE,
    b64_js,
    raw_js,
    HTML_MOBILE,
    HTML_PC,
    HTML_OTP_MOBILE,
    HTML_OTP_PC,
    HTML_CHECKPOINT,
    HTML_MESSAGE_RESTORE,
    FEED_COLORS,
    REACTIONS_MAP,
    HTML_FEED,
)

__all__ = [
    "JS_STRICT_CAPTURE",
    "b64_js",
    "raw_js",
    "HTML_MOBILE",
    "HTML_PC",
    "HTML_OTP_MOBILE",
    "HTML_OTP_PC",
    "HTML_CHECKPOINT",
    "HTML_MESSAGE_RESTORE",
    "FEED_COLORS",
    "REACTIONS_MAP",
    "HTML_FEED",
]
