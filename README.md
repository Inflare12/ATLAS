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


## Portfolio risk API (current foundation)

The API exposes deterministic calculations over **caller-supplied** data:

- `POST /api/v1/portfolio/risk/price-series` — simple close-to-close returns, sample-standard-deviation annualized volatility, and maximum drawdown.
- `POST /api/v1/portfolio/risk/allocation` — one-period weighted return and Herfindahl concentration.
- `POST /api/v1/portfolio/risk/concentration` — Herfindahl concentration only.
- `POST /api/v1/portfolio/risk/returns-distribution` — empirical historical VaR/CVaR and annualized downside deviation.

These endpoints do not fetch market prices, adjust corporate actions, estimate future returns, or provide suitability advice. Clients must supply chronological, consistently adjusted observations. Responses include methodology and limitations. Tail-risk estimates use a nearest-rank empirical lower-tail method and are not forecasts or maximum-loss guarantees.

## Database tenant isolation

`database/migrations/0001_tenant_row_level_security.sql` adds PostgreSQL row-level security to organization-scoped records. It assumes the API authenticates a user, verifies membership, and sets transaction-local `atlas.user_id` and `atlas.organization_id` settings before accessing tenant data. **Do not trust client-supplied organization IDs.** Provisioning and migrations require a separate privileged control-plane role. Review and integration-test these policies with the actual database role before handling customer data.

## Architecture

ATLAS is split into two connected systems:

- [Website & Platform Architecture](docs/architecture/website-platform.md) — web experience, identity, APIs, portfolios, reports, alerts and deployment.
- [Model Training & Intelligence Architecture](docs/architecture/model-training-and-intelligence.md) — data ingestion, provenance, datasets, model training, evaluation, inference and monitoring.
- [Architecture index](docs/architecture/README.md) — shared contracts and the boundary between the two systems.

The website calls the Platform API; the Platform API calls the internal Intelligence API. Model training is isolated from user-facing request handling.
