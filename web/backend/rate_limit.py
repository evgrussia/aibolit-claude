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

    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[str, _Bucket] = defaultdict(_Bucket)

    def check(self, key: str) -> None:
        """Raise HTTPException(429) if the key has exceeded the limit."""
        bucket = self._buckets[key]
        if bucket.count(self.window) >= self.max_requests:
            raise HTTPException(
                429,
                "Слишком много попыток. Повторите через минуту.",
            )
        bucket.add()


def _client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For behind reverse proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Pre-configured limiters
auth_limiter = RateLimiter(max_requests=10, window_seconds=60)      # 10 req/min
register_limiter = RateLimiter(max_requests=5, window_seconds=300)   # 5 reg / 5 min


def check_auth_rate_limit(request: Request) -> None:
    """Check login rate limit for the requesting IP."""
    auth_limiter.check(_client_ip(request))


def check_register_rate_limit(request: Request) -> None:
    """Check registration rate limit for the requesting IP."""
    register_limiter.check(_client_ip(request))
