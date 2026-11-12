# ATLAS — Adaptive Global Financial Intelligence

ATLAS is an evidence-first financial research and portfolio intelligence platform. It helps users investigate companies and markets, understand portfolio risk, and monitor material changes. It does **not** execute trades.

> **Status:** Foundation / early development. Not investment advice. Outputs are research support, not guaranteed predictions or personalized regulated advice.

## Product principles
- Evidence before conclusions: every material claim should be traceable to a source and timestamp.
- Separate research, quantitative analysis, suitability, and portfolio decisions.
- Explicit uncertainty: support **insufficient evidence**, **wait**, and **no action**.
- Point-in-time correctness: retain event, publication, ingestion, and effective timestamps.
- Privacy by design: tenant isolation, least privilege, and no cross-customer position disclosure.
- India-first, globally extensible; regulatory and data-licensing review before commercial launch.

## Initial MVP
1. Company search and evidence-backed research reports.
2. Company fundamentals, filings, news, and counter-evidence.
3. Manual portfolio import and holdings overview.
4. Portfolio exposure and risk snapshots.
5. Material-event monitoring, alerts, and audit history.

Advanced prediction, geospatial intelligence, broker integrations, and automated trading are explicitly out of initial scope.

## Repository layout
- `apps/api` — FastAPI application
- `apps/web` — planned web client
- `packages/atlas_core` — shared domain contracts and calculations
- `database` — migrations and database design
- `docs` — architecture, security, compliance, roadmap
- `tests` — automated tests

## Local development
Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn atlas_api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API.

## Configuration
Copy `.env.example` to `.env`. The API can start without external financial data credentials. Never commit secrets.

## Development status
This repository is being built in small, testable stages. Live market data, investment recommendations, and production deployment are not yet implemented. Do not use sample data as current market information.

## License
No license has been granted yet. All rights reserved until a license is added by the project owner.
