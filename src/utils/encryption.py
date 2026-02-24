"""Field-level encryption for medical data at rest.

Uses Fernet (AES-128-CBC + HMAC-SHA256) for authenticated encryption.
Encrypted values are stored as base64 strings prefixed with 'enc:'.
"""
import logging
import os
import warnings

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("aibolit.encryption")

_fernet: Fernet | None = None
_ENC_PREFIX = "enc:"


def _init_fernet() -> Fernet | None:
    """Initialize Fernet cipher from AIBOLIT_ENCRYPTION_KEY env var."""
    global _fernet
    if _fernet is not None:
        return _fernet

    key = os.getenv("AIBOLIT_ENCRYPTION_KEY", "")
    if not key:
        # Try loading from config (circular import safe — config is pure env reads)
        try:
            from web.backend.config import ENCRYPTION_KEY
            key = ENCRYPTION_KEY
        except ImportError:
            pass

    if not key:
        warnings.warn(
            "AIBOLIT_ENCRYPTION_KEY not set — medical data will NOT be encrypted at rest. "
            "Generate a key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    try:
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
        return _fernet
    except Exception:
        logger.error("Invalid AIBOLIT_ENCRYPTION_KEY — cannot initialize encryption")
        return None


def encrypt_field(value: str | None) -> str | None:
    """Encrypt a string field value. Returns 'enc:<base64>' or original if no key."""
    if value is None or value == "":
        return value

    f = _init_fernet()
    if f is None:
        return value  # No key — store unencrypted (dev mode)

    try:
        encrypted = f.encrypt(value.encode("utf-8"))
        return _ENC_PREFIX + encrypted.decode("ascii")
    except Exception:
        logger.exception("Failed to encrypt field value")
        return value  # Fallback to unencrypted


def decrypt_field(value: str | None) -> str | None:
    """Decrypt a field value. Handles both encrypted ('enc:...') and plaintext values."""
    if value is None or value == "":
        return value

    if not value.startswith(_ENC_PREFIX):
        return value  # Not encrypted — return as-is (backward compat)

    f = _init_fernet()
    if f is None:
        logger.warning("Cannot decrypt field — AIBOLIT_ENCRYPTION_KEY not set")
        return "[ENCRYPTED — key not available]"

    try:
        token = value[len(_ENC_PREFIX):].encode("ascii")
        return f.decrypt(token).decode("utf-8")
    except InvalidToken:
        logger.error("Failed to decrypt field — invalid token or wrong key")
        return "[DECRYPTION FAILED]"
    except Exception:
        logger.exception("Unexpected error decrypting field")
        return "[DECRYPTION ERROR]"


def is_encryption_enabled() -> bool:
    """Check if encryption is configured and active."""
    return _init_fernet() is not None
