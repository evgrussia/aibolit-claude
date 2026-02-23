"""Aibolit Patient Portal — FastAPI backend.

Run from project root:
    python -m web.backend.main
"""
import logging
import sys
import os
import time
from contextlib import asynccontextmanager

# Ensure project root is in path so `src.*` imports work
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.utils.database import init_db
from .config import CORS_ORIGINS
from .routers import auth, patients, consultations, diagnostics, drugs, documents, reference, knowledge, chat

# ── Logging setup ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("aibolit")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Aibolit backend started")
    yield
    logger.info("Aibolit backend shutting down")


app = FastAPI(
    title="Aibolit Patient Portal",
    version="1.0.0",
    description="Веб-портал пациента клиники Aibolit",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Global exception handler ──────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})


# ── Request logging middleware ─────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    if duration > 1.0 or response.status_code >= 400:
        logger.info(
            "%s %s → %s (%.2fs)",
            request.method, request.url.path, response.status_code, duration,
        )
    return response

app.include_router(auth.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(consultations.router, prefix="/api/v1")
app.include_router(diagnostics.router, prefix="/api/v1")
app.include_router(drugs.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(reference.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "aibolit-portal"}


if __name__ == "__main__":
    import uvicorn
    from .config import BACKEND_PORT
    uvicorn.run("web.backend.main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
