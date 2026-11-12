# ATLAS architecture

## System boundaries
ATLAS is a research and decision-support system, not a broker. The first release is a modular monolith with independently testable domain modules. Split workers/services only when measured scale or isolation requirements justify it.

## Request flow
1. API authenticates the user and resolves tenant scope.
2. Orchestrator creates a research run with a reproducible request snapshot.
3. Connectors retrieve licensed, timestamped source material.
4. Normalizers validate identifiers, units, currencies, and periods.
5. Evidence records preserve source, publication time, retrieval time, and extraction version.
6. Specialist engines calculate metrics and assess claims.
7. Suitability and portfolio-risk checks run separately from company research.
8. A report presents findings, counter-evidence, confidence, caveats, and source links.
9. Monitoring compares new material events with active user rules and emits material alerts only.

## Domain modules
- Identity and tenant access
- Investor context and portfolios
- Data connectors and provenance
- Company and sector research
- Quantitative analytics and risk
- Suitability and decision policy
- Recommendation lifecycle
- Monitoring and notifications
- Audit, evaluation, and observability

## Non-negotiable invariants
- No claim without evidence or an explicit label that it is a hypothesis.
- No fabricated prices, filings, citations, or freshness labels.
- Distinguish event time, publication time, ingestion time, and effective time.
- Preserve source and model versions for reproducibility.
- Research quality, forecast quality, suitability, and portfolio impact are different evaluations.
- Platform recommendation concentration is not the same as actual market crowding.
- Never expose one customer's positions or behaviour to another customer.
- A recommendation may be rejected, suspended, invalidated, expired, or superseded; retain its history.

## Initial technology choices
FastAPI + Pydantic for the API; PostgreSQL for relational records; object storage for immutable source documents; background workers for ingestion; a web client added after API/domain contracts stabilize. External providers must be selected only after licensing, coverage, cost, and redistribution review.
