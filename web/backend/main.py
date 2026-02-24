"""Aibolit Patient Portal — FastAPI backend.

Run from project root:
    python -m web.backend.main
"""
import logging
import sys
import os
import time
import uuid
from contextlib import asynccontextmanager

# Ensure project root is in path so `src.*` imports work
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.utils.database import init_db, close_db, cleanup_expired_tokens
from .config import CORS_ORIGINS
from .rate_limit import check_global_rate_limit
from .routers import auth, patients, consultations, diagnostics, drugs, documents, reference, knowledge, chat, audit
from .services.audit_service import request_id_var, request_ip_var, request_ua_var

# ── Logging setup ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("aibolit")


async def _token_cleanup_loop() -> None:
    """Periodically remove expired revoked tokens (every 6 hours)."""
    import asyncio
    while True:
        await asyncio.sleep(6 * 3600)
        try:
            removed = cleanup_expired_tokens()
            if removed:
                logger.info("[CLEANUP] Removed %d expired revoked tokens", removed)
        except Exception:
            logger.exception("[CLEANUP] Failed to clean expired tokens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    init_db()
    logger.info("Aibolit backend started (PostgreSQL)")
    cleanup_task = asyncio.create_task(_token_cleanup_loop())
    yield
    cleanup_task.cancel()
    close_db()
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


# ── Global rate limit middleware ──────────────────────────
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Enforce global rate limit (60 req/min per IP) on all /api/ endpoints."""
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        try:
            check_global_rate_limit(request)
        except HTTPException as exc:
            client_ip = request.client.host if request.client else "?"
            logger.warning(
                "[RATE_LIMIT] 429 %s %s from=%s",
                request.method, request.url.path, client_ip,
            )
            return JSONResponse(status_code=429, content={"detail": exc.detail})
    return await call_next(request)


# ── Request ID + audit context middleware ─────────────────
@app.middleware("http")
async def audit_context_middleware(request: Request, call_next):
    """Генерирует request_id (UUID) для каждого запроса и сохраняет
    метаданные в contextvars для доступа из AuditLogService."""
    req_id = str(uuid.uuid4())
    request.state.request_id = req_id

    # Сохраняем в contextvars для доступа из любого места без передачи request
    token_rid = request_id_var.set(req_id)
    token_ip = request_ip_var.set(request.client.host if request.client else None)
    token_ua = request_ua_var.set(request.headers.get("user-agent"))

    client_ip = request.client.host if request.client else "?"
    user_agent = request.headers.get("user-agent", "?")[:100]
    path = request.url.path
    method = request.method

    # Логируем входящие запросы (кроме health check)
    if path != "/api/health":
        logger.info(
            "[REQ] %s %s from=%s ua=%.60s rid=%s",
            method, path, client_ip, user_agent, req_id[:8],
        )

    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    # Добавляем request_id в заголовок ответа для трейсинга
    response.headers["X-Request-ID"] = req_id

    # Логируем все ответы (кроме health check)
    if path != "/api/health":
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "[RES] %s %s → %s (%.2fs) rid=%s",
            method, path, response.status_code, duration, req_id[:8],
        )

    # Сбрасываем contextvars
    request_id_var.reset(token_rid)
    request_ip_var.reset(token_ip)
    request_ua_var.reset(token_ua)

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
app.include_router(audit.router, prefix="/api/v1")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "aibolit-portal"}


if __name__ == "__main__":
    import uvicorn
    from .config import BACKEND_PORT
    uvicorn.run("web.backend.main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
