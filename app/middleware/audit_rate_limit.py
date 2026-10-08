import time
from collections import defaultdict, deque
from datetime import datetime

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import verify_access_token
from app.models.audit_log import AuditLog


class AuditRateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        # Stores request timestamps for each IP/user.
        self.request_history = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.client.host if request.client else "unknown"

    def _get_user_id(self, request: Request):
        authorization = request.headers.get("Authorization")

        if not authorization:
            return None

        if not authorization.startswith("Bearer "):
            return None

        token = authorization.split(" ", 1)[1]

        try:
            return verify_access_token(token)
        except Exception:
            return None

    def _get_rate_limit_key(
        self,
        request: Request,
        user_id,
        client_ip: str,
    ) -> str:
        if user_id is not None:
            return f"user:{user_id}"

        return f"ip:{client_ip}"

    def _is_rate_limited(self, key: str) -> bool:
        current_time = time.time()

        history = self.request_history[key]

        # Remove requests outside the current time window.
        while (
            history
            and current_time - history[0]
            >= settings.RATE_LIMIT_WINDOW_SECONDS
        ):
            history.popleft()

        if len(history) >= settings.RATE_LIMIT_REQUESTS:
            return True

        history.append(current_time)

        return False

    async def dispatch(self, request: Request, call_next):

        # Health check is excluded from rate limiting and logging.
        if request.url.path == "/health":
            return await call_next(request)

        start_time = time.perf_counter()

        client_ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)

        rate_limit_key = self._get_rate_limit_key(
            request,
            user_id,
            client_ip,
        )

        # Check rate limit before executing the API.
        if self._is_rate_limited(rate_limit_key):

            response_time = time.perf_counter() - start_time

            self._save_audit_log(
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                ip_address=client_ip,
                status_code=429,
                response_time=response_time,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                },
            )

        try:
            response = await call_next(request)

        except Exception:
            response_time = time.perf_counter() - start_time

            self._save_audit_log(
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                ip_address=client_ip,
                status_code=500,
                response_time=response_time,
            )

            raise

        response_time = time.perf_counter() - start_time

        self._save_audit_log(
            user_id=user_id,
            endpoint=request.url.path,
            method=request.method,
            ip_address=client_ip,
            status_code=response.status_code,
            response_time=response_time,
        )

        return response

    def _save_audit_log(
        self,
        user_id,
        endpoint,
        method,
        ip_address,
        status_code,
        response_time,
    ):
        db = SessionLocal()

        try:
            audit_log = AuditLog(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                ip_address=ip_address,
                status_code=status_code,
                response_time=response_time,
                timestamp=datetime.utcnow(),
            )

            db.add(audit_log)
            db.commit()

        except Exception as exc:
            db.rollback()
            print(f"Audit log failed: {exc}")

        finally:
            db.close()