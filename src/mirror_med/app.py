from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mirror_med.logging import get_logger
from mirror_med.settings import get_settings

logger = get_logger(__name__)

# Uvicorn logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "filters": {
        "health_check_filter": {
            "()": "mirror_med.logging_filters.HealthCheckFilter",
            "paths": ["/health", "/"],
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["health_check_filter"],
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting MirrorMed API")

    yield

    # Shutdown
    logger.info("Shutting down MirrorMed API")


app = FastAPI(
    title="MirrorMed API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware for WebSocket support
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Origin"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    include_in_schema=False,
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


def main():
    """Entry point for the mirror_med CLI command."""
    import uvicorn

    uvicorn.run(
        "mirror_med.app:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING_CONFIG,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
