from fastapi import FastAPI

from app.core.audit_cleanup import cleanup_old_audit_logs
from app.core.database import Base, engine
from app.core.exceptions import global_exception_handler
from app.middleware.audit_rate_limit import AuditRateLimitMiddleware
from app.models.audit_log import AuditLog
from app.models.user import User
from app.routers import audit_logs, auth, protected


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Audit & Rate Limiter",
    description="JWT authentication, request auditing and rate limiting",
    version="1.0.0",
)

app.add_exception_handler(
    Exception,
    global_exception_handler,
)

app.add_middleware(AuditRateLimitMiddleware)


@app.on_event("startup")
def startup_cleanup():
    cleanup_old_audit_logs()


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(protected.router)
app.include_router(audit_logs.router)