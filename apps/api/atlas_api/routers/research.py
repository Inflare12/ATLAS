"""Evidence packet contracts; validates provenance structure, not truth."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

router = APIRouter(prefix="/research", tags=["research"])


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class EvidenceSource(StrictModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_.:-]+$")
    source_name: str = Field(min_length=2, max_length=160)
    source_type: Literal["company_filing", "exchange_disclosure", "government", "company_website", "licensed_news", "licensed_market_data", "user_supplied", "other"]
    source_url: HttpUrl
    published_at: datetime | None = None
    retrieved_at: datetime
    excerpt: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def timestamps_are_aware(self):
        for field in ("published_at", "retrieved_at"):
            value = getattr(self, field)
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{field} must include a timezone")
        return self


class EvidenceClaim(StrictModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_.:-]+$")
    statement: str = Field(min_length=3, max_length=1000)
    evidence_ids: list[str] = Field(min_length=1, max_length=20)
    stance: Literal["supports", "contradicts", "context"]
    as_of: datetime

    @model_validator(mode="after")
    def validate_claim(self):
        if self.as_of.tzinfo is None:
            raise ValueError("claim as_of must include a timezone")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("claim evidence_ids must be unique")
        return self


class EvidencePacketRequest(StrictModel):
    company_identifier: str = Field(min_length=1, max_length=100)
    market: str = Field(default="IN", min_length=2, max_length=8)
    as_of: datetime
    evidence: list[EvidenceSource] = Field(min_length=1, max_length=100)
    claims: list[EvidenceClaim] = Field(default_factory=list, max_length=200)
    limitations: list[str] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def validate_packet(self):
        if self.as_of.tzinfo is None:
            raise ValueError("packet as_of must include a timezone")
        evidence_ids = [item.id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence IDs must be unique")
        claim_ids = [item.id for item in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("claim IDs must be unique")
        known = set(evidence_ids)
        for claim in self.claims:
            missing = set(claim.evidence_ids) - known
            if missing:
                raise ValueError(f"claim '{claim.id}' references unknown evidence IDs: {', '.join(sorted(missing))}")
        return self


@router.post("/evidence-packets/validate")
def validate_evidence_packet(request: EvidencePacketRequest) -> dict[str, object]:
    """Validate caller-supplied source references; do not imply independent verification."""
    referenced = {eid for claim in request.claims for eid in claim.evidence_ids}
    return {
        "status": "validated",
        "company_identifier": request.company_identifier,
        "market": request.market,
        "as_of": request.as_of.isoformat(),
        "evidence_count": len(request.evidence),
        "claim_count": len(request.claims),
        "unreferenced_evidence_ids": sorted({item.id for item in request.evidence} - referenced),
        "stance_counts": {stance: sum(claim.stance == stance for claim in request.claims) for stance in ("supports", "contradicts", "context")},
        "limitations": [
            *request.limitations,
            "Validation confirms packet structure and references, not source authenticity or claim truth.",
            "Sources and excerpts were supplied by the caller and have not been independently verified.",
            "This endpoint does not produce investment recommendations or forecasts.",
        ],
        "next_step": "Connect authorized source ingestion before treating this packet as verified research.",
    }


class ResearchRequest(StrictModel):
    query: str = Field(min_length=2, max_length=240, examples=["Analyse ABC Ltd"])
    market: str = Field(default="IN", min_length=2, max_length=8)
    include_risks: bool = True


@router.post("/reports")
def create_research_report(request: ResearchRequest) -> dict[str, object]:
    """Keep report generation disabled until verified connectors are configured."""
    raise HTTPException(
        status_code=501,
        detail={
            "code": "RESEARCH_ENGINE_NOT_CONFIGURED",
            "message": "A verified data connector, provenance store, and research pipeline are required.",
        },
    )
