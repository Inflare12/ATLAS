-- Initial PostgreSQL domain schema. Apply through reviewed migrations in production.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE organization_memberships (
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'analyst', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (organization_id, user_id)
);

CREATE TABLE investor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    investment_horizon TEXT,
    risk_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, user_id)
);

CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    owner_user_id UUID NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    base_currency CHAR(3) NOT NULL DEFAULT 'INR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_symbol TEXT NOT NULL,
    exchange TEXT,
    asset_type TEXT NOT NULL,
    currency CHAR(3),
    identifiers JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (canonical_symbol, exchange)
);

CREATE TABLE holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id),
    quantity NUMERIC(28, 10) NOT NULL CHECK (quantity >= 0),
    average_cost NUMERIC(28, 10) CHECK (average_cost >= 0),
    as_of TIMESTAMPTZ NOT NULL,
    UNIQUE (portfolio_id, asset_id, as_of)
);

CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    license_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    permitted_uses TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evidence_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES data_sources(id),
    source_uri TEXT,
    title TEXT,
    published_at TIMESTAMPTZ,
    retrieved_at TIMESTAMPTZ NOT NULL,
    event_at TIMESTAMPTZ,
    content_hash TEXT,
    extracted_text_location TEXT,
    extraction_version TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE research_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    requested_by UUID REFERENCES users(id),
    query JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued','running','completed','failed','insufficient_evidence')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    model_versions JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE research_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    claim TEXT NOT NULL,
    stance TEXT NOT NULL CHECK (stance IN ('support','counter_evidence','context','hypothesis')),
    confidence NUMERIC(5,4) CHECK (confidence BETWEEN 0 AND 1),
    evidence_ids UUID[] NOT NULL DEFAULT '{}',
    caveats TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    actor_user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id UUID,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_portfolios_org ON portfolios(organization_id);
CREATE INDEX idx_holdings_portfolio_asof ON holdings(portfolio_id, as_of DESC);
CREATE INDEX idx_evidence_published ON evidence_records(published_at DESC);
CREATE INDEX idx_research_org_created ON research_runs(organization_id, started_at DESC);
CREATE INDEX idx_audit_org_time ON audit_events(organization_id, occurred_at DESC);
