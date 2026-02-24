"""Configuration for Aibolit web backend."""
import os
import secrets
import warnings

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_PORT = 8007

# ── Database ──────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aibolit:aibolit@localhost:5432/aibolit",
)

# ── JWT Secret ────────────────────────────────────────────────
_secret = os.getenv("AIBOLIT_SECRET_KEY", "")
if not _secret:
    # Try to load from persistent file
    _secret_file = os.path.join(PROJECT_ROOT, "data", ".secret_key")
    if os.path.isfile(_secret_file):
        with open(_secret_file, "r") as f:
            _secret = f.read().strip()
    if not _secret:
        _secret = secrets.token_hex(32)
        # Persist so tokens survive restarts
        os.makedirs(os.path.dirname(_secret_file), exist_ok=True)
        with open(_secret_file, "w") as f:
            f.write(_secret)
        warnings.warn(
            "AIBOLIT_SECRET_KEY не задан! Сгенерирован и сохранён в data/.secret_key. "
            "Задайте переменную окружения AIBOLIT_SECRET_KEY для production.",
            RuntimeWarning,
            stacklevel=1,
        )

SECRET_KEY = _secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

# ── Encryption ────────────────────────────────────────────────
ENCRYPTION_KEY = os.getenv("AIBOLIT_ENCRYPTION_KEY", "")

# ── CORS ──────────────────────────────────────────────────────
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://127.0.0.1",
    "https://aibolit-ai.ru",
    "https://api.aibolit-ai.ru",
    "http://aibolit-ai.ru",
    "http://api.aibolit-ai.ru",
]
