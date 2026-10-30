from fastapi import FastAPI, Depends

from app.database import Base, engine
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.routers import auth,users,permissions, uploads
from app.routers.v1 import products as products_v1
from app.routers.v2 import products as products_v2

# Middleware, CROS 
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware


# Rate Limiting
from fastapi import Request
from fastapi.responses import JSONResponse

try:
    from importlib import import_module

    _slowapi = import_module("slowapi")
    _slowapi_errors = import_module("slowapi.errors")
    _rate_limit_exceeded_handler = _slowapi._rate_limit_exceeded_handler
    RateLimitExceeded = _slowapi_errors.RateLimitExceeded
    from app.limiter import limiter
except ImportError:
    class RateLimitExceeded(Exception):
        pass

    def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        _ = request, exc
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    class _LimiterFallback:
        def limit(self, value: str):
            _ = value

            def decorator(endpoint):
                return endpoint

            return decorator

    limiter = _LimiterFallback()


# create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Authentication API", description="Authentication system using postgreSQL, JWT and OAuth2", version="1.0.0")

# Allowed origins for CROS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000"
]

# store limiter
app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

# Middleware, CROS 
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization","Content-Type","X-Request-ID"],
)

# Root path
@app.get("/")
def root():
    return {"message": "FastAPI Authentication API is running"}

@app.get("/me", response_model=UserResponse)
@limiter.limit("30/minute")
def get_me(request:Request, current_user: User = Depends(get_current_user)):
    _ = request
    return current_user

# Authentication, RBAC, PBAC, API Versioning routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(uploads.router)
app.include_router(products_v1.router, prefix="/api/v1")
app.include_router(products_v2.router, prefix="/api/v2")