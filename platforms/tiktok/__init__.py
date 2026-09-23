"""__init__.py - Module TikTok."""

from platforms.tiktok.settings import (
    PLATFORM_INFO, CAPABILITIES, TRANSLATIONS, FEED_TRANSLATIONS,
    REACTIONS_MAP, FEED_COLORS, MOBILE_ONLY,
)
from platforms.tiktok.route import TEMPLATES, get_template, handle_loading, register_routes
from platforms.tiktok.dialog import TikTokPublicationDialog

__all__ = [
    "PLATFORM_INFO", "CAPABILITIES", "TRANSLATIONS", "FEED_TRANSLATIONS",
    "REACTIONS_MAP", "FEED_COLORS", "MOBILE_ONLY",
    "TEMPLATES", "get_template", "handle_loading", "register_routes",
    "TikTokPublicationDialog",
]
