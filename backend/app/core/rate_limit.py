from __future__ import annotations
import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
class BasicRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 300, window_seconds: int = 60):
        super().__init__(app); self.limit=limit; self.window_seconds=window_seconds; self.requests=defaultdict(deque)
    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now=time.time(); bucket=self.requests[client]
        while bucket and bucket[0] <= now-self.window_seconds: bucket.popleft()
        if len(bucket)>=self.limit: return Response("rate limit exceeded", status_code=429)
        bucket.append(now); return await call_next(request)
