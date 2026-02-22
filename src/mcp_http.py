"""
Aibolit AI Medical Clinic — MCP Streamable HTTP Server.

Exposes the same 55 MCP tools over Streamable HTTP transport,
allowing remote Claude clients to connect via:

    https://mcp.aibolit-ai.ru/mcp

Run locally:
    python -m src.mcp_http
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from .mcp_server import app as mcp_app
from .utils.database import init_db

logger = logging.getLogger("aibolit.mcp_http")


session_manager = StreamableHTTPSessionManager(
    app=mcp_app,
    json_response=False,
    stateless=False,
)


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


@asynccontextmanager
async def lifespan(app: Starlette):
    init_db()
    logger.info("Aibolit MCP HTTP server starting on /mcp")
    async with session_manager.run():
        yield


starlette_app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        Mount("/mcp", app=session_manager.handle_request),
    ],
    lifespan=lifespan,
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(starlette_app, host="0.0.0.0", port=8103)
