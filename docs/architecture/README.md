# ATLAS Architecture

ATLAS has two connected architecture domains:

1. [Website & Platform Architecture](website-platform.md) — user experience, identity, APIs, portfolio workflows, reports, monitoring and deployment.
2. [Model Training & Intelligence Architecture](model-training-and-intelligence.md) — ingestion, evidence provenance, datasets, specialist models, evaluation, inference and governance.

## System boundary

The website does not train models or perform authoritative financial calculations in the browser. It sends authorized requests to the Platform API. The Platform API calls the internal Intelligence API. The intelligence platform retrieves approved evidence, runs deterministic analytics and specialist models, validates outputs, and returns versioned results.

## Shared contracts

Both architectures must agree on stable company/instrument identifiers; observation, publication, retrieval and effective timestamps; currency and unit conventions; research-run and report identifiers; evidence provenance and source licensing; model, dataset and methodology versions; tenant authorization; and explicit confidence, freshness and limitations.

## Implementation rule

Build the smallest auditable end-to-end workflow first:

Company lookup → authorized source ingestion → evidence-backed research run → validated report → website display.

Expand to portfolio monitoring and custom model training only after this path is reliable.
