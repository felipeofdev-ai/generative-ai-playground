-- NexusAI — PostgreSQL Initialization
-- Runs once on first container start

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tenants') THEN
    INSERT INTO tenants (id, name, slug, plan, status, nexus_enabled, daily_budget_usd, created_at, updated_at)
    VALUES (
      'ten_default_dev',
      'NexusAI Dev Tenant',
      'nexusai-dev',
      'enterprise',
      'active',
      true,
      10000.00,
      NOW(),
      NOW()
    ) ON CONFLICT DO NOTHING;
  END IF;
END $$;
