from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=240, examples=["Analyse ABC Ltd"])
    market: str = Field(default="IN", min_length=2, max_length=8)
    include_risks: bool = True


@router.post("/reports")
def create_research_report(request: ResearchRequest) -> dict[str, object]:
    """Placeholder contract; intentionally does not fabricate financial research."""
    raise HTTPException(
        status_code=501,
        detail={
            "code": "RESEARCH_ENGINE_NOT_CONFIGURED",
            "message": (
                "Research generation is not available yet. A verified data connector, "
                "source provenance, and research pipeline must be configured first."
            ),
            "request": request.model_dump(),
        },
    )
