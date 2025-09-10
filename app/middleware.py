from __future__ import annotations
import time, hashlib
from typing import Dict, Tuple, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .config import settings
from .logging_util import get_logger

log = get_logger("middleware")

# --- Simple in-memory token bucket per key ---
class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate = int(settings.RATE_LIMIT_PER_MINUTE or 120)  # tokens per minute
        self.burst = int(settings.RATE_LIMIT_BURST or self.rate)
        self.store: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_ts)

    def _key(self, request: Request) -> str:
        strat = (settings.RATE_LIMIT_KEY_STRATEGY or "api_key_or_ip").lower()
        api_key = request.headers.get("x-api-key", "")
        ip = request.client.host if request.client else "unknown"
        if strat == "api_key":
            base = api_key or ip
        elif strat == "ip":
            base = ip
        else:  # api_key_or_ip
            base = api_key or ip
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    async def dispatch(self, request: Request, call_next):
        # no limit for /health
        if request.url.path == "/health":
            return await call_next(request)

        key = self._key(request)
        now = time.time()
        refill_rate = self.rate / 60.0  # tokens per second

        tokens, last_ts = self.store.get(key, (float(self.burst), now))
        # Refill
        elapsed = max(0.0, now - last_ts)
        tokens = min(self.burst, tokens + elapsed * refill_rate)

        if tokens < 1.0:
            # Too many requests
            retry_after = max(1, int((1.0 - tokens) / refill_rate))
            headers = {
                "X-RateLimit-Limit": str(self.rate),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(retry_after),
            }
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429, headers=headers)

        tokens -= 1.0
        self.store[key] = (tokens, now)

        response = await call_next(request)
        # Annotate headers
        remaining = int(tokens)
        response.headers["X-RateLimit-Limit"] = str(self.rate)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = "0"
        return response

class RequestLogger(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # parse header allowlist
        self.header_allow = [h.strip().lower() for h in (settings.REQUEST_LOG_HEADERS or "").split(",") if h.strip()]

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        hdrs = {}
        if self.header_allow:
            for h in self.header_allow:
                if h in request.headers:
                    val = request.headers[h]
                    # mask api key
                    if h == "x-api-key" and val:
                        val = (val[:3] + "***" + val[-2:]) if len(val) > 5 else "***"
                    hdrs[h] = val
        client = request.client.host if request.client else "unknown"
        query = dict(request.query_params) if settings.REQUEST_LOG_QUERY else {}
        body_preview = None
        if settings.REQUEST_LOG_BODY:
            try:
                body_preview = (await request.body())
                body_preview = body_preview[:512].decode("utf-8", errors="ignore")
            except Exception:
                body_preview = None

        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        log.info(f"{client} {request.method} {request.url.path} {response.status_code} {duration_ms}ms "
                 f"headers={hdrs} query={query} body_preview={body_preview}")
        return response
