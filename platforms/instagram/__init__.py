"""__init__.py - Module Instagram."""

from platforms.instagram.settings import (
    PLATFORM_INFO, CAPABILITIES, TRANSLATIONS, FEED_TRANSLATIONS,
    REACTIONS_MAP, FEED_COLORS, MOBILE_ONLY,
)
from platforms.instagram.route import TEMPLATES, get_template, handle_loading, register_routes
from platforms.instagram.dialog import InstagramPublicationDialog

__all__ = [
    "PLATFORM_INFO", "CAPABILITIES", "TRANSLATIONS", "FEED_TRANSLATIONS",
    "REACTIONS_MAP", "FEED_COLORS", "MOBILE_ONLY",
    "TEMPLATES", "get_template", "handle_loading", "register_routes",
    "InstagramPublicationDialog",
]
