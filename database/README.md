# Database setup and tenant security

## Apply the initial schema

The SQL in this directory is an initial foundation, not a production migration framework yet.

1. Create a PostgreSQL database.
2. Apply `database/schema.sql` using a migration/administration role.
3. Apply `database/migrations/0001_tenant_row_level_security.sql`.
4. Create a restricted application role. Do not connect the public web client directly to PostgreSQL.
5. Test access with at least two organizations and two users before importing any customer data.

Example using `psql` from the repository root:

```sql
\i database/schema.sql
\i database/migrations/0001_tenant_row_level_security.sql
```

## Transaction context

After authenticating a user, the API must verify that the user belongs to the requested organization. It then sets both values on the same database transaction:

```sql
SELECT set_config('atlas.user_id', :authenticated_user_uuid, true);
SELECT set_config('atlas.organization_id', :verified_organization_uuid, true);
```

The third argument to `set_config` makes the setting transaction-local. Never accept the user ID or organization membership as trusted values from an unverified client request. The RLS policies independently check that the configured user is a member of the configured organization.

## Current boundaries

- Organization and membership provisioning is reserved for a privileged control-plane role.
- The application role should not own the tables and should not have `BYPASSRLS`.
- Shared `assets` and `data_sources` are catalogue tables, not places for tenant-private data.
- This migration does not replace application authentication, authorization, audit review, backup policy, or penetration testing.
- The SQL has not yet been integration-tested against a live PostgreSQL instance. Do that before using real personal or financial information.
