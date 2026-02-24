"""Simple in-memory rate limiter for authentication endpoints.

Protects against brute-force login/register attempts.
Uses a sliding-window counter per IP address.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import HTTPException, Request


@dataclass
class _Bucket:
    """Tracks request timestamps for a single key."""
    timestamps: list[float] = field(default_factory=list)

    def clean(self, window: float) -> None:
        cutoff = time.monotonic() - window
        self.timestamps = [t for t in self.timestamps if t > cutoff]

    def count(self, window: float) -> int:
        self.clean(window)
        return len(self.timestamps)

    def add(self) -> None:
        self.timestamps.append(time.monotonic())


class RateLimiter:
    """In-memory sliding-window rate limiter.

    Args:
        max_requests: Maximum allowed requests within the window.
        window_seconds: Time window in seconds.
    """

    _EVICT_INTERVAL = 300.0  # evict stale buckets every 5 min

    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[str, _Bucket] = defaultdict(_Bucket)
        self._last_evict: float = time.monotonic()

    def _evict_stale(self) -> None:
        """Remove buckets with no recent timestamps to prevent memory growth."""
        now = time.monotonic()
        if now - self._last_evict < self._EVICT_INTERVAL:
            return
        self._last_evict = now
        stale = [k for k, b in self._buckets.items() if b.count(self.window) == 0]
        for k in stale:
            del self._buckets[k]

    def check(self, key: str) -> None:
        """Raise HTTPException(429) if the key has exceeded the limit."""
        self._evict_stale()
        bucket = self._buckets[key]
        if bucket.count(self.window) >= self.max_requests:
            raise HTTPException(
                429,
                "Слишком много попыток. Повторите через минуту.",
            )
        bucket.add()


def _client_ip(request: Request) -> str:
    """Extract client IP from request.

    In production Nginx sets X-Real-IP from the actual client address.
    X-Forwarded-For is used as fallback but can be spoofed without
    trusted proxy validation — Nginx config should strip/override it.
    """
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Pre-configured limiters
auth_limiter = RateLimiter(max_requests=10, window_seconds=60)      # 10 req/min
register_limiter = RateLimiter(max_requests=5, window_seconds=300)   # 5 reg / 5 min
global_limiter = RateLimiter(max_requests=60, window_seconds=60)    # 60 req/min per IP


def check_auth_rate_limit(request: Request) -> None:
    """Check login rate limit for the requesting IP."""
    auth_limiter.check(_client_ip(request))


def check_register_rate_limit(request: Request) -> None:
    """Check registration rate limit for the requesting IP."""
    register_limiter.check(_client_ip(request))


def check_global_rate_limit(request: Request) -> None:
    """Check global API rate limit for the requesting IP."""
    global_limiter.check(_client_ip(request))
