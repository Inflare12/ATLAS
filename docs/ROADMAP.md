# Delivery roadmap

## Phase 0 — Foundation (current)
- [x] Repository and product boundaries
- [x] FastAPI scaffold and health endpoints
- [x] Safe research request contract
- [ ] CI, linting, and test baseline
- [ ] Database migrations and tenant model

## Phase 1 — Trustworthy research MVP
- [ ] Instrument/security master and identifier mapping
- [ ] Source registry and licensing metadata
- [ ] Filing/news ingestion with publication and retrieval timestamps
- [ ] Evidence extraction and source-linked claims
- [ ] Company profile, fundamentals, and comparison report
- [ ] Counter-evidence and uncertainty presentation

## Phase 2 — Portfolio intelligence
- [ ] Manual CSV portfolio import with validation
- [ ] Holdings, cash, currency, and exposure model
- [ ] Risk snapshots: concentration, volatility, drawdown, correlation, liquidity caveats
- [ ] Portfolio-wide impact analysis
- [ ] User-defined monitoring rules and alert history

## Phase 3 — Validation and controlled expansion
- [ ] Point-in-time datasets and walk-forward evaluation
- [ ] Benchmark and transaction-cost-aware backtests
- [ ] Model registry, drift monitoring, and reproducibility
- [ ] Geospatial and advanced prediction only after data rights and validation
- [ ] Security, privacy, and regulatory review before public launch

## Definition of done
A feature is not complete merely because an endpoint returns data. It needs input validation, authorization, tests, observability, failure behaviour, provenance where applicable, and documentation. No simulated data may be presented as live data.
