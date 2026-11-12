# ATLAS Model Training & Intelligence Architecture

**Status:** Proposed implementation blueprint

## 1. Purpose and non-negotiable principles

This system ingests approved financial and alternative data, builds reproducible datasets, trains and evaluates specialist models, serves validated inference, and monitors outcomes.

1. Point-in-time correctness: features may only use information available at the prediction timestamp.
2. Provenance: every feature, label, prediction and report claim traces to source records and transformations.
3. Separation of concerns: retrieval, calculations, forecasting, suitability and language generation are different tasks.
4. Deterministic code performs portfolio arithmetic, risk and validation; an LLM is not the calculator.
5. Synthetic fixtures are always labelled and never presented as live market observations.
6. Models are promoted only after robust out-of-sample evaluation.
7. Data licensing, user consent and applicable regulatory boundaries are enforced before use.

## 2. End-to-end architecture

~~~mermaid
flowchart TB
  subgraph SRC[Approved Data Sources]
    M[Licensed Market Data]
    F[Filings & Fundamentals]
    N[Licensed News & Disclosures]
    G[Government & Macro Data]
    S[Licensed Satellite / Geospatial]
    P[Authorized User Portfolio Data]
  end
  subgraph ING[Ingestion Trust Boundary]
    C[Source Connectors]
    R[Immutable Raw Store]
    L[Source & License Registry]
    V[Parsing / Validation / Deduplication]
  end
  subgraph DATA[Canonical Data Platform]
    E[Evidence & Provenance]
    I[Instrument / Entity Resolution]
    T[(PostgreSQL Time-series Data)]
    FE[Point-in-time Feature Builder]
    LA[Outcome / Label Builder]
    DS[Versioned Dataset Manifests]
  end
  subgraph DEV[Model Development]
    SP[Temporal Splits]
    TR[Training Pipelines]
    EV[Walk-forward / Robustness Evaluation]
    MR[Model Registry & Approval]
  end
  subgraph RUN[Production Intelligence]
    OR[Research Orchestrator]
    RET[Evidence Retrieval]
    Q[Deterministic Quant & Risk]
    TS[Time-series / Ranking Models]
    NLP[Document NLP / Extraction]
    CV[Vision / Geospatial Models]
    LLM[Grounded Language Synthesis]
    PG[Policy / Suitability / Confidence Gates]
    API[Versioned Intelligence API]
  end
  subgraph OPS[Governance]
    DM[Data & Model Drift]
    FB[Outcome Capture]
    HR[Human Review / Revalidation]
  end
  M --> C
  F --> C
  N --> C
  G --> C
  S --> C
  P --> C
  L --> C
  C --> R --> V
  V --> E
  V --> I --> T
  T --> FE
  FE --> DS
  LA --> DS
  DS --> SP --> TR --> EV --> MR
  E --> RET
  OR --> RET
  OR --> Q
  OR --> TS
  OR --> NLP
  OR --> CV
  RET --> LLM
  NLP --> LLM
  CV --> LLM
  Q --> PG
  TS --> PG
  LLM --> PG --> API
  API --> DM
  DM --> HR
  FB --> HR
  HR --> DS
~~~

## 3. Ingestion and data trust

Each connector must declare source identity, provider, license, permitted use, identifiers, observation/publication/retrieval/effective timestamps, currency, units, timezone, frequency, raw payload checksum, parser version and validation status.

Pipeline:
1. Fetch only from an authorized API/feed or permitted user upload.
2. Store the raw response immutably with checksum and retrieval metadata.
3. Parse into typed records while retaining source fields.
4. Normalize identifiers, units, currencies and timezones.
5. Validate gaps, duplicates, outliers, corporate actions and timestamp order.
6. Persist canonical records linked to raw evidence.
7. Publish a versioned event for downstream processing.

Public availability does not automatically grant commercial redistribution rights. Keep a source/license registry and enforce its scope. Satellite imagery must retain acquisition time and revisit limitations; do not call delayed imagery real-time.

## 4. Dataset engineering

Maintain separate layers:
- Raw: immutable payloads and uploads.
- Normalized: canonical observations and events.
- Evidence: claims, source spans and extracted facts.
- Features: versioned numerical/categorical inputs.
- Labels: outcomes with explicit horizon and availability time.
- Training snapshots: immutable reproducible manifests.

Each dataset manifest records source snapshots and rights, date range, point-in-time cutoff, universe membership history, feature and label definitions, code version, missing-data policy, adjustment policy, temporal split boundaries, exclusions, hash and creation time.

### Leakage prevention

- Use historical universe membership to prevent survivorship bias.
- Use only filings/news actually published by the feature cutoff.
- Apply corporate-action adjustments consistently and point-in-time.
- Fit scalers and imputers on training data only.
- Avoid random shuffling for temporal forecasting.
- Handle overlapping outcome horizons correctly.
- Keep a final untouched test period.
- Include transaction costs, spread, slippage, liquidity and taxes where relevant.

## 5. Specialist model portfolio

Do not begin with one giant model.

| Component | Responsibility | Initial implementation |
|---|---|---|
| Document extraction | Parse filings and disclosures | Rules + NLP; schema-validated LLM extraction |
| Evidence retrieval | Find support and counter-evidence | Hybrid lexical + vector search |
| Fundamentals | Ratios, trends and accounting checks | Deterministic Python/SQL |
| Risk | Volatility, drawdown, VaR/CVaR, exposure, stress | Tested deterministic library |
| Forecasting | Estimate distributions/ranges, not certainty | Naive baselines, regularized models, then advanced models |
| Ranking/anomaly | Surface unusual changes and research priorities | Statistical baselines, gradient boosting |
| Geospatial/vision | Extract licensed imagery observations | Separate vision pipeline, later phase |
| Graph analytics | Company, supplier and event relationships | Graph features after entity resolution |
| Language synthesis | Explain evidence and uncertainty | LLM grounded in validated evidence |

A useful first release does not require a custom deep neural network. Source quality, deterministic metrics, retrieval and calibrated baselines come first.

## 6. Training lifecycle

~~~mermaid
flowchart TD
  A[Approved Source Snapshots] --> B[Build Point-in-time Dataset]
  B --> C[Schema / Leakage / Coverage Tests]
  C --> D[Temporal Train-Validation-Test Split]
  D --> E[Train Baseline]
  E --> F[Train Candidate]
  F --> G[Walk-forward Evaluation]
  G --> H{Pass Baselines and Risk Gates?}
  H -- No --> I[Reject and Diagnose]
  I --> B
  H -- Yes --> J[Robustness / Regime / Cost Tests]
  J --> K{Independent Approval?}
  K -- No --> I
  K -- Yes --> L[Register Immutable Artifact]
  L --> M[Shadow Deployment]
  M --> N[Monitor Drift / Quality / Latency]
  N --> O{Within Guardrails?}
  O -- No --> P[Disable / Roll Back]
  O -- Yes --> Q[Controlled Production]
~~~

Reproducibility requires code commit, dependency lock, dataset manifest, configuration, random seed where relevant, environment metadata and artifact checksum.

## 7. Evaluation

**Forecasting:** MAE/RMSE where appropriate, calibration, interval coverage, horizon/regime/subgroup performance and naive baselines.

**Ranking:** precision/recall at K, ranking stability, turnover, subgroup analysis, concentration and capacity.

**Portfolio simulation:** point-in-time walk-forward tests, realistic costs, drawdown, volatility, downside deviation, VaR/CVaR, turnover, liquidity, exposure, stress scenarios and benchmark comparisons.

**Document extraction/RAG:** field-level precision/recall, citation correctness, source-span verification, contradiction detection, abstention and prompt-injection tests.

**LLM synthesis:** evidence factuality, citation coverage, unsupported-claim rate, uncertainty handling, policy compliance and human review.

Never promote on in-sample accuracy, training loss or one attractive backtest alone.

## 8. Production inference path

1. Platform API submits an authorized research request.
2. Orchestrator resolves company, investor context and permitted data scope.
3. Retrieval returns versioned evidence and timestamps.
4. Deterministic services calculate fundamentals, portfolio impact and risk.
5. Specialist models return typed outputs with model version and confidence.
6. Policy gates check data freshness, completeness and permitted use.
7. LLM writes an explanation from the validated evidence bundle.
8. Citation validation checks claims and removes unsupported statements.
9. A versioned report is stored and returned through the Intelligence API.

LLMs may summarize, compare and explain. They may not invent data, bypass authorization, execute trades or turn uncertain forecasts into guarantees.

## 9. Model operations and monitoring

Monitor data freshness, source outages, schema changes, missingness, feature drift, prediction drift, realized forecast calibration, latency, failures, compute cost, human overrides, abstentions and report corrections.

Use shadow mode before a model affects user-facing analysis. Retrain only after documented triggers and evaluation; do not blindly retrain on a timer. Keep rollback artifacts and a kill switch.

## 10. Initial technology choices

| Need | Start with |
|---|---|
| Data processing | Python, Polars, PyArrow |
| Storage | PostgreSQL + object storage |
| Geospatial | PostGIS |
| ML | scikit-learn first; PyTorch when justified |
| Dataset versioning | Immutable manifests + object storage |
| Experiment tracking | MLflow or equivalent |
| Workflow | Queue + workers; consider Temporal later |
| Retrieval | pgvector plus lexical search |
| Serving | Internal FastAPI inference endpoints |
| Monitoring | OpenTelemetry + data/model quality metrics |

Keep training isolated from latency-sensitive API services. Start with CPU-friendly baselines and small datasets; use cloud compute when needed rather than making a modest personal laptop a production dependency.

## 11. Suggested repository structure

~~~text
services/
  intelligence_api/
  ingestion/
  research_orchestrator/
  inference/
  training/
  monitoring/
  document_processing/
  geospatial/
ml/
  components/
    document_nlp/
    retrieval/
    fundamentals/
    risk/
    time_series/
    ranking/
    anomaly_detection/
    geospatial/
  datasets/manifests/
  features/
  labels/
  experiments/
  evaluation/
  model_registry/
  serving/
data/
  connectors/
  contracts/
  normalization/
  validation/
  provenance/
  licensing/
evaluation/
  backtesting/
  walk_forward/
  leakage_tests/
  robustness/
  baselines/
~~~

## 12. Build order

**Phase 1 — trustworthy foundation:** connector contract, source/license registry, entity mapping, raw evidence storage, deterministic fundamentals/risk, evidence-grounded reports.

**Phase 2 — reproducible model development:** dataset manifests, point-in-time features, leakage tests, temporal splits, baseline models, walk-forward evaluation and experiment tracking.

**Phase 3 — controlled production:** Intelligence API, shadow deployments, drift monitoring, citation validation, abstention and outcome capture.

**Phase 4 — advanced modalities:** licensed geospatial data, document vision, graph analytics and advanced time-series models.

## 13. Definition of done

A model is not production-ready until data rights are clear, its dataset is reproducible, leakage tests pass, baselines are documented, out-of-sample and cost-aware evaluation passes, its artifact is versioned, inference is monitored, rollback is tested and user-facing limitations are explicit.
