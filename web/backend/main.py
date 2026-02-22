"""Aibolit Patient Portal — FastAPI backend.

Run from project root:
    python -m web.backend.main
"""
import sys
import os
from contextlib import asynccontextmanager

# Ensure project root is in path so `src.*` imports work
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.utils.database import init_db
from .config import CORS_ORIGINS
from .routers import auth, patients, consultations, diagnostics, drugs, documents, reference, knowledge


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(consultations.router, prefix="/api/v1")
app.include_router(diagnostics.router, prefix="/api/v1")
app.include_router(drugs.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(reference.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "aibolit-portal"}


if __name__ == "__main__":
    import uvicorn
    from .config import BACKEND_PORT
    uvicorn.run("web.backend.main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
