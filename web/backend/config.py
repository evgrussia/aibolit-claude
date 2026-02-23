"""Configuration for Aibolit web backend."""
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_PORT = 8007
_secret = os.getenv("AIBOLIT_SECRET_KEY", "")
if not _secret:
    import secrets as _s
    _secret = _s.token_hex(32)
    import warnings
    warnings.warn(
        "AIBOLIT_SECRET_KEY не задан! Сгенерирован временный ключ. "
        "Задайте переменную окружения AIBOLIT_SECRET_KEY для production.",
        RuntimeWarning,
        stacklevel=1,
    )
SECRET_KEY = _secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7
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
