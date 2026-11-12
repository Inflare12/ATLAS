# ATLAS Website & Platform Architecture

**Status:** Proposed implementation blueprint

## 1. Purpose and boundaries

The website is the product interface: identity, dashboards, company research workspaces, portfolios, reports, alerts, administration and API access. It must not train models, hold vendor secrets, or perform authoritative financial calculations in browser code.

Start with a modular backend and separately deployed web/API/worker processes. Do not split into many microservices before scale and team boundaries justify it. The platform is research and decision-support software, not a trading execution system.

## 2. High-level architecture

~~~mermaid
flowchart TB
  U[Investor / Analyst / Admin] --> EDGE[CDN + WAF]
  EDGE --> WEB[Next.js Web App]
  WEB --> API[Platform API / BFF]
  API --> AUTH[Identity + Authorization]
  API --> ORG[Organization & Investor Context]
  API --> RES[Research Workspaces]
  API --> PORT[Portfolio & Risk]
  API --> REPORT[Reports & Exports]
  API --> MON[Monitoring & Alerts]
  API --> AUDIT[Audit & Consent]
  RES --> INTEL[Internal Intelligence API]
  PORT --> INTEL
  MON --> INTEL
  API --> DB[(PostgreSQL + PostGIS)]
  API --> CACHE[(Redis)]
  API --> STORE[(Private Object Storage)]
  API --> QUEUE[Job Queue]
  QUEUE --> WORK[Background Workers]
  WORK --> INTEL
  WORK --> DB
  WORK --> STORE
  API --> OBS[Logs / Metrics / Traces]
  WORK --> OBS
~~~

## 3. Technology choices

| Layer | Initial technology | Role |
|---|---|---|
| Website | Next.js + TypeScript | Responsive product UI and routing |
| UI system | Tailwind + reusable accessible components | Consistent design system |
| API | Python + FastAPI | Validation, authorization and product workflows |
| Contracts | OpenAPI + generated TypeScript client | Versioned frontend/backend boundary |
| Primary database | PostgreSQL | Users, tenants, portfolios, jobs, reports, audit |
| Geospatial | PostGIS | Spatial metadata when geospatial features arrive |
| Cache / queue | Redis | Caching, rate limits and lightweight job dispatch |
| Files | S3-compatible private object storage | Uploads, source documents and report artifacts |
| Workers | Python processes | Imports, report generation and scheduled monitoring |
| Observability | OpenTelemetry-compatible stack | Traces, logs, metrics and error tracking |

## 4. Web application structure

~~~text
apps/web/
  app/
    (public)/
    (auth)/
    dashboard/
    research/
    companies/[identifier]/
    portfolios/
    portfolios/[id]/risk/
    reports/[id]/
    alerts/
    settings/
apps/api/atlas_api/
  auth/
  organizations/
  investor_profiles/
  research/
  portfolios/
  reports/
  monitoring/
  notifications/
  audit/
  integrations/
services/workers/
  imports/
  report_generation/
  monitoring/
packages/
  contracts/
  ui/
  api_client/
~~~

Core screens:
- Dashboard: portfolio health, watchlist and material updates.
- Research: company search, comparisons and research-run status.
- Company workspace: business profile, fundamentals, events, evidence and risks.
- Portfolio: manual import, holdings and allocation.
- Risk: exposures, concentration, drawdown and stress scenarios.
- Reports: versioned research reports with citations and as-of time.
- Alerts: material events, preferences and alert history.
- Settings: profile, consent, exports and account controls.

## 5. Three main user journeys

### Company research
1. User submits an instrument/company and research question.
2. API authenticates the user, resolves tenant membership and checks permissions.
3. API creates a research run and returns a job identifier.
4. Worker calls the internal Intelligence API.
5. Evidence, calculations, model versions and limitations are stored.
6. Web app shows progress and renders the completed report with citations.

### Portfolio risk
1. User uploads a supported CSV or enters holdings manually.
2. API validates identifiers, units, currency, dates and duplicates.
3. User reviews and confirms the parsed positions.
4. Portfolio snapshot is stored with an audit event.
5. Risk engine calculates metrics from timestamped inputs.
6. UI displays assumptions, missing data and calculation timestamp.

### Monitoring
1. User chooses monitoring scope and alert categories.
2. Scheduler dispatches monitoring jobs.
3. Workers check for new observations and material changes.
4. Impact assessment suppresses duplicates and low-value noise.
5. API stores an auditable event and delivers the configured alert.

## 6. API boundary

The browser communicates only with the Platform API. The Platform API calls internal domain modules and the Intelligence API using authenticated service-to-service contracts.

Suggested routes:
- /api/v1/me
- /api/v1/organizations
- /api/v1/research-runs
- /api/v1/companies
- /api/v1/portfolios
- /api/v1/reports
- /api/v1/alerts
- /api/v1/data-exports

Use request IDs, pagination, idempotency keys for retryable writes, explicit API versions and a consistent error format. Never expose unrestricted database queries or model/vendor credentials.

## 7. Security and tenancy

- Use a maintained identity provider or reviewed authentication implementation.
- Resolve user and organization membership on the server. A browser-supplied organization ID is not proof of membership.
- Set transaction-local database identity only after server-side membership verification.
- Use PostgreSQL Row-Level Security as defense in depth. The app role must not own protected tables or have BYPASSRLS.
- Keep tenant data separate from shared reference catalogs.
- Encrypt transport and sensitive stored data; keep secrets server-side.
- Validate file type, size and content; scan uploads where appropriate.
- Audit imports, exports, sensitive reads, permission changes and administrative actions.
- Do not train on customer portfolios without explicit documented authorization.
- Treat uploaded documents and external content as untrusted; defend model workflows against prompt injection.

## 8. Report trust requirements

Every report and metric must show data-as-of time, retrieval time where different, source and publication time where available, methodology/model version, confidence, limitations and missing/stale inputs. Supporting and contradictory evidence should both be visible. Valid outcomes include insufficient evidence, wait, no material change and no action. Do not force a buy/sell conclusion.

## 9. Deployment topology

Deploy CDN/WAF, web app, API, workers, managed PostgreSQL, managed Redis/queue and private object storage as distinct runtime components. Use separate development, staging and production environments. Apply database migrations as a controlled release step. Maintain backups and test restoration, secrets management, TLS, monitoring and rollback procedures.

## 10. Delivery order

1. Stable API contracts, configuration, health checks and CI.
2. Authentication, organization membership and tenant isolation.
3. Company lookup and research job lifecycle.
4. Evidence-backed report pages.
5. Manual portfolio import and risk dashboard.
6. Material event monitoring and alert history.
7. Exports, administration and enterprise controls.
8. Accessibility, load tests, security review and production hardening.

## 11. Acceptance criteria

- Tenant boundaries cannot be bypassed by changing request parameters.
- Browser bundles contain no vendor or database secrets.
- Reports trace to input data, evidence, run and model versions.
- Long-running tasks are asynchronous, retry-safe and observable.
- Portfolio metrics disclose methodology and stale/missing inputs.
- Monitoring events are deduplicated and auditable.
- Core flows have unit, API, authorization and database integration tests.
