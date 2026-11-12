# Security, privacy, and regulatory guardrails

This document is an engineering checklist, not legal advice.

## Security baseline
- Enforce tenant scope on every customer-owned query and mutation.
- Use managed identity, short-lived sessions, least-privilege service credentials, and secret storage.
- Encrypt traffic and sensitive stored data; define retention and deletion workflows.
- Record security-relevant actions in append-only audit events.
- Validate uploads, limit size/type, scan files, and isolate document parsing.
- Treat filings, webpages, PDFs, and user-provided text as untrusted input. Retrieved text must never override system policy or trigger arbitrary tools.
- Do not send private portfolio data to model providers without explicit, informed authorization and contractual safeguards.

## Financial integrity
- Separate general research from investor-specific suitability.
- Record the assumptions, evidence, timestamps, model versions, and limitations behind every assessment.
- Never promise returns or certainty. Display uncertainty and material counter-evidence.
- Do not enable order placement or broker write permissions in the MVP.
- Do not imply a dataset is real-time unless its actual update latency supports that claim.

## India launch gate
Before offering paid, actionable securities research or personalized recommendations, obtain qualified Indian regulatory counsel to assess applicable SEBI Research Analyst / Investment Adviser requirements, distribution rules, disclosures, and operating controls. Confirm current requirements rather than relying on this checklist.

## Data rights
Publicly accessible data is not automatically licensed for commercial use or redistribution. Track provider, permitted purpose, geography, retention, display, derived-data, and redistribution rights for every connector.
