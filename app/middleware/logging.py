import logging,time,uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.requests")

class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request:Request, call_next):
        request_id = str(uuid.uuid4())[:8]

        start = time.perf_counter()

        logger.info("REQUEST -> %s %s [%s]",request.method, request.url.path, request_id)

        response = await call_next(request)

        duration = (time.perf_counter() - start) * 1000

        logger.info("RESPONSE -> %s %s %d %.1fms [%s]", request.method,request.url.path,response.status_code,duration,request_id)

        response.headers["X-Request-ID"] = request_id

        response.headers["X-Response-Time"] = (f"{duration:.1f}ms")

        return response