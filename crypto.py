"""
crypto.py — Chiffrement/déchiffrement simple des fichiers sensibles.

Utilise un chiffrement XOR avec une clé dérivée d'un sel fixe via SHA-256,
puis encode en base64. Ajoute un en-tête magique pour détecter les fichiers
déjà chiffrés vs les fichiers en clair (pour la rétrocompatibilité).

Ce n'est pas un chiffrement cryptographiquement inviolable, mais ça empêche
la lecture en clair des fichiers sur disque (identifiants, logs d'erreurs).

Fonctions publiques:
  encrypt_text(plaintext: str) -> str   → chiffre du texte, retourne base64
  decrypt_text(ciphertext: str) -> str  → déchiffre du texte base64
  is_encrypted(data: str) -> bool       → détecte si le contenu est chiffré
  encrypt_file(filepath: str) -> bool   → chiffre un fichier sur disque
  decrypt_file_content(filepath: str) -> str → lit + déchiffre un fichier
  write_encrypted(filepath: str, content: str) -> None → écrit du contenu chiffré
"""

import base64
import hashlib
import os
import sys
import traceback

# ─── Constants ───────────────────────────────────────────────────────────────
# Magic header to identify encrypted files (prevents double-encryption and
# allows reading old plaintext files for backward compatibility)
_MAGIC = "ENCv1:"

# Fixed application salt — used to derive the XOR key.
# This is not meant to be a secret (it's in the source code), but it ensures
# that the files can't be read by simply opening them in a text editor.
_APP_SALT = b"MetaCloud_SVD_2024_SecureStorage_Salt_Key"


def _derive_key(length: int) -> bytes:
    """Derive a key of the given length from the application salt using SHA-256."""
    try:
        # Use repeated SHA-256 to generate enough bytes for the key
        key = b""
        counter = 0
        while len(key) < length:
            chunk = hashlib.sha256(_APP_SALT + counter.to_bytes(4, 'big')).digest()
            key += chunk
            counter += 1
        return key[:length]
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto._derive_key] {e}\n")
        except Exception:
            pass
        return _APP_SALT[:length]


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR data with a repeating key."""
    try:
        if not key:
            return data
        result = bytearray(len(data))
        key_len = len(key)
        for i in range(len(data)):
            result[i] = data[i] ^ key[i % key_len]
        return bytes(result)
    except Exception:
        return data


def encrypt_text(plaintext: str) -> str:
    """Encrypt a plaintext string and return a base64-encoded string with magic header.
    Returns the plaintext unchanged if encryption fails (never raises)."""
    try:
        if not plaintext:
            return plaintext
        data = plaintext.encode('utf-8')
        key = _derive_key(len(data))
        encrypted = _xor_bytes(data, key)
        encoded = base64.b64encode(encrypted).decode('ascii')
        return _MAGIC + encoded
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.encrypt_text] {e}\n")
        except Exception:
            pass
        return plaintext  # Fallback: return plaintext (better than losing data)


def decrypt_text(ciphertext: str) -> str:
    """Decrypt a base64-encoded string (with magic header) back to plaintext.
    If the input is not encrypted (no magic header), returns it unchanged (backward compat).
    Never raises — returns the input on any error."""
    try:
        if not ciphertext:
            return ciphertext
        # Check if the data is encrypted (has the magic header)
        if not ciphertext.startswith(_MAGIC):
            return ciphertext  # Not encrypted — return as-is (backward compatibility)
        # Remove magic header and decode
        encoded = ciphertext[len(_MAGIC):]
        encrypted = base64.b64decode(encoded)
        key = _derive_key(len(encrypted))
        decrypted = _xor_bytes(encrypted, key)
        return decrypted.decode('utf-8')
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.decrypt_text] {e}\n")
        except Exception:
            pass
        return ciphertext  # Fallback: return the raw input (better than crashing)


def is_encrypted(data: str) -> bool:
    """Check if a string is encrypted (starts with the magic header)."""
    try:
        return data is not None and data.startswith(_MAGIC)
    except Exception:
        return False


def write_encrypted(filepath: str, content: str) -> None:
    """Write content to a file, encrypted if encrypt_files is enabled, plaintext otherwise.
    Never raises — logs errors to stderr."""
    try:
        # Check if encryption is enabled in config
        try:
            import config as _cfg
            should_encrypt = _cfg.is_encrypt_files()
        except Exception:
            should_encrypt = True  # Default: encrypt

        if should_encrypt:
            encrypted = encrypt_text(content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(encrypted)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.write_encrypted] {filepath}: {e}\n")
        except Exception:
            pass


def read_encrypted(filepath: str) -> str:
    """Read a file and decrypt it if needed.
    If the file doesn't exist, returns empty string.
    If the file is not encrypted (old plaintext), returns it as-is.
    Never raises — returns empty string on error."""
    try:
        if not os.path.exists(filepath):
            return ""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return decrypt_text(content)
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.read_encrypted] {filepath}: {e}\n")
        except Exception:
            pass
        return ""


def encrypt_file(filepath: str) -> bool:
    """Encrypt an existing file in-place (read, encrypt, overwrite).
    Skips files that are already encrypted.
    Returns True if the file was encrypted, False if skipped or failed."""
    try:
        if not os.path.exists(filepath):
            return False
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if is_encrypted(content):
            return False  # Already encrypted — skip
        write_encrypted(filepath, content)
        return True
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.encrypt_file] {filepath}: {e}\n")
        except Exception:
            pass
        return False


def read_json_encrypted(filepath: str):
    """Read a JSON file that may be encrypted or plaintext.
    Returns the parsed JSON object, or None on error.
    Never raises."""
    try:
        content = read_encrypted(filepath)
        if not content:
            return None
        import json
        return json.loads(content)
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.read_json_encrypted] {filepath}: {e}\n")
        except Exception:
            pass
        return None


def write_json_encrypted(filepath: str, data) -> None:
    """Write a Python object as encrypted JSON to a file.
    Never raises — logs errors to stderr."""
    try:
        import json
        content = json.dumps(data, indent=4, ensure_ascii=False)
        write_encrypted(filepath, content)
    except Exception as e:
        try:
            sys.stderr.write(f"[crypto.write_json_encrypted] {filepath}: {e}\n")
        except Exception:
            pass
