"""__init__.py - Module Google."""

from platforms.google.settings import (
    PLATFORM_INFO, CAPABILITIES, TRANSLATIONS, FEED_TRANSLATIONS,
    REACTIONS_MAP, FEED_COLORS, MOBILE_ONLY,
)
from platforms.google.route import TEMPLATES, get_template, handle_loading, register_routes

__all__ = [
    "PLATFORM_INFO", "CAPABILITIES", "TRANSLATIONS", "FEED_TRANSLATIONS",
    "REACTIONS_MAP", "FEED_COLORS", "MOBILE_ONLY",
    "TEMPLATES", "get_template", "handle_loading", "register_routes",
]
