from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from atlas_api.config import get_settings
from atlas_api.routers import health, portfolio, research

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description=(
        "Evidence-first financial research and portfolio intelligence. "
        "This API does not execute trades or provide guaranteed predictions."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(research.router, prefix=settings.api_prefix)
app.include_router(portfolio.router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "foundation", "docs": "/docs"}
