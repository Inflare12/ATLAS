-- Apply after database/schema.sql. The API must set these transaction-local values
-- only after authenticating the user:
--   SET LOCAL atlas.user_id = '<authenticated-user-uuid>';
--   SET LOCAL atlas.organization_id = '<requested-organization-uuid>';
-- Every tenant policy ALSO checks actual membership, so a forged organization
-- setting alone cannot grant access. Use a restricted application DB role.
-- A separate privileged control-plane role is required for provisioning/migrations.
CREATE OR REPLACE FUNCTION atlas_current_org_id()
RETURNS UUID LANGUAGE SQL STABLE
AS $$ SELECT NULLIF(current_setting('atlas.organization_id', true), '')::UUID $$;

CREATE OR REPLACE FUNCTION atlas_current_user_id()
RETURNS UUID LANGUAGE SQL STABLE
AS $$ SELECT NULLIF(current_setting('atlas.user_id', true), '')::UUID $$;

-- Membership rows are visible only to the authenticated user. This avoids an
-- RLS policy that accidentally grants visibility merely because an org ID is set.
ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_memberships FORCE ROW LEVEL SECURITY;
CREATE POLICY memberships_self_read ON organization_memberships
    FOR SELECT USING (user_id = atlas_current_user_id());

CREATE OR REPLACE FUNCTION atlas_is_org_member(target_org UUID)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT target_org IS NOT NULL AND EXISTS (
        SELECT 1
        FROM organization_memberships m
        WHERE m.organization_id = target_org
          AND m.user_id = atlas_current_user_id()
    )
$$;

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations FORCE ROW LEVEL SECURITY;
CREATE POLICY organizations_member_read ON organizations
    FOR SELECT USING (atlas_is_org_member(id));

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;
CREATE POLICY users_self_read ON users FOR SELECT
    USING (id = atlas_current_user_id());

ALTER TABLE investor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE investor_profiles FORCE ROW LEVEL SECURITY;
CREATE POLICY investor_profiles_org_isolation ON investor_profiles
    USING (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    )
    WITH CHECK (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    );

ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios FORCE ROW LEVEL SECURITY;
CREATE POLICY portfolios_org_isolation ON portfolios
    USING (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    )
    WITH CHECK (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    );

ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE holdings FORCE ROW LEVEL SECURITY;
CREATE POLICY holdings_portfolio_org_isolation ON holdings
    USING (
        EXISTS (
            SELECT 1 FROM portfolios p
            WHERE p.id = holdings.portfolio_id
              AND p.organization_id = atlas_current_org_id()
              AND atlas_is_org_member(p.organization_id)
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM portfolios p
            WHERE p.id = holdings.portfolio_id
              AND p.organization_id = atlas_current_org_id()
              AND atlas_is_org_member(p.organization_id)
        )
    );

ALTER TABLE evidence_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_records FORCE ROW LEVEL SECURITY;
CREATE POLICY evidence_global_or_org_read ON evidence_records FOR SELECT
    USING (
        organization_id IS NULL
        OR (
            organization_id = atlas_current_org_id()
            AND atlas_is_org_member(organization_id)
        )
    );
CREATE POLICY evidence_org_insert ON evidence_records FOR INSERT
    WITH CHECK (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    );

ALTER TABLE research_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY research_runs_org_isolation ON research_runs
    USING (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    )
    WITH CHECK (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    );

ALTER TABLE research_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_claims FORCE ROW LEVEL SECURITY;
CREATE POLICY research_claims_via_run ON research_claims
    USING (
        EXISTS (
            SELECT 1 FROM research_runs r
            WHERE r.id = research_claims.research_run_id
              AND r.organization_id = atlas_current_org_id()
              AND atlas_is_org_member(r.organization_id)
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM research_runs r
            WHERE r.id = research_claims.research_run_id
              AND r.organization_id = atlas_current_org_id()
              AND atlas_is_org_member(r.organization_id)
        )
    );

ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;
CREATE POLICY audit_events_org_read ON audit_events FOR SELECT
    USING (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    );
CREATE POLICY audit_events_org_insert ON audit_events FOR INSERT
    WITH CHECK (
        organization_id = atlas_current_org_id()
        AND atlas_is_org_member(organization_id)
    );

-- assets and data_sources remain shared reference/catalogue tables. Do not store
-- tenant-private notes, holdings, or customer-specific metadata in these tables.
