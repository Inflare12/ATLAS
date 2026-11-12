from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "atlas-api"}


@router.get("/ready")
def ready() -> dict[str, str]:
    # Readiness will include database/provider checks once those integrations exist.
    return {"status": "ready", "checks": "not-configured"}
