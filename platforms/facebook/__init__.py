"""__init__.py - Module Facebook."""

from platforms.facebook.settings import (
    PLATFORM_INFO, CAPABILITIES, TRANSLATIONS, FEED_TRANSLATIONS,
    REACTIONS_MAP, FEED_COLORS, MOBILE_ONLY,
)
from platforms.facebook.route import TEMPLATES, get_template, register_routes
from platforms.facebook.dialog import FacebookPublicationDialog, AdDialog
# PublicationDialog est dans widgets_parts/publication_dialog.py
from widgets_parts.publication_dialog import PublicationDialog

__all__ = [
    "PLATFORM_INFO", "CAPABILITIES", "TRANSLATIONS", "FEED_TRANSLATIONS",
    "REACTIONS_MAP", "FEED_COLORS", "MOBILE_ONLY",
    "TEMPLATES", "get_template", "register_routes",
    "FacebookPublicationDialog", "PublicationDialog", "AdDialog",
]
