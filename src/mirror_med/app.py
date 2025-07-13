import asyncio
import warnings
from contextlib import asynccontextmanager
from typing import Any

import weave
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mirror_med.a2a.agent_config import create_a2a_app
from mirror_med.crews import run_patient_health_assessment
from mirror_med.logging import get_logger
from mirror_med.settings import get_settings

# Suppress deprecation warnings from third-party packages
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="weave")

weave.init("stepandel-none/hack-jul12")


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
    status: str = Field(..., json_schema_extra={"example": "ok"})


class VisitInput(BaseModel):
    # Use Any to accept flexible structure for stub
    social_history: Any
    medical_history: Any
    allergies: Any
    surgical_history: Any
    hospitalizations: Any
    family_history: Any
    medications: Any
    pcp: Any
    forecast: Any
    measurements: Any


class RecommendationItem(BaseModel):
    description: str
    rating: int


class Recommendations(BaseModel):
    alcohol: RecommendationItem
    sleep: RecommendationItem
    exercise: RecommendationItem
    supplements: list[RecommendationItem]


class VisitOutput(VisitInput):
    recommendations: Recommendations


def _get_stub_recommendations() -> dict:
    """Return stub recommendations as fallback."""
    return {
        "alcohol": {"description": "Limit to 1 drink per day", "rating": 8},
        "sleep": {"description": "Aim for 7-8 hours nightly", "rating": 9},
        "exercise": {
            "description": "30 minutes of moderate activity, 5 days/week",
            "rating": 8,
        },
        "supplements": [
            {"description": "Take 2000 IU Vitamin D3 daily", "rating": 9},
            {"description": "Consider 1000 mg Omega-3 daily", "rating": 7},
        ],
    }


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

# Add CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    include_in_schema=False,
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/visit", response_model=VisitOutput)
async def create_visit(visit_data: VisitInput) -> VisitOutput:
    # Convert input to dict
    visit_dict = visit_data.model_dump()

    try:
        # Run the crew in a thread with timeout
        logger.info("Running patient health assessment crew")
        crew_result = await asyncio.wait_for(
            asyncio.to_thread(run_patient_health_assessment, visit_dict), timeout=3
        )

        # If crew returned valid recommendations
        if isinstance(crew_result, dict) and "raw_output" not in crew_result:
            visit_dict["recommendations"] = crew_result
            logger.info("Successfully generated crew recommendations")
        else:
            # Fallback to stub if crew output is invalid
            logger.warning("Crew returned invalid format, using stub data")
            raise ValueError("Invalid crew output format")

    except asyncio.TimeoutError:
        logger.error("Crew execution timed out after 45 seconds")
        # Use stub data
        visit_dict["recommendations"] = _get_stub_recommendations()

    except Exception as e:
        logger.error(f"Error running crew: {str(e)}")
        # Use stub data on any error
        visit_dict["recommendations"] = _get_stub_recommendations()

    # Return complete output
    return VisitOutput(**visit_dict)


# Mount A2A handler if base URL is configured
# if settings.a2a_base_url:
#     a2a_app = create_a2a_app(settings.a2a_base_url)
#     app.mount("/", a2a_app)


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
