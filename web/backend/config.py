"""Configuration for Aibolit web backend."""
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_PORT = 8007
SECRET_KEY = os.getenv("AIBOLIT_SECRET_KEY", "aibolit-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://127.0.0.1",
]
