# NexusAI — Comprehensive System Documentation

## 1. Purpose and Scope

This document consolidates the technical view of the NexusAI platform and is intended for:

- platform engineers;
- backend/frontend developers;
- SRE/DevOps teams;
- security and governance stakeholders.

It complements the existing deep-dive documents under `docs/` and `docs/reference/` with a single operational map of the system.

---

## 2. System Overview

NexusAI is a multi-model Generative AI platform that orchestrates multiple LLM providers behind a unified API and governance layer.

Core capabilities:

- multi-provider inference routing;
- policy and safety enforcement;
- cost and quota controls;
- observability and auditing;
- retrieval-augmented generation (RAG);
- async workloads for indexing/evaluation/reporting.

At runtime, the platform combines synchronous API serving (`apps/api/`) with asynchronous worker execution (`apps/worker/`) and complementary runtime modules (security, policy, rollout, governance).

---

## 3. High-Level Architecture

```text
Clients (Web / SDK / API Consumers)
                |
                v
          API Layer (FastAPI)
                |
                +--> Auth / Tenant / Cost middleware
                |
                +--> Routers (Inference, Nexus, Governance, Metrics, etc.)
                |
                +--> Services (Orchestrator, Routing, Cost, PII, Audit)
                |
                +--> Data Layer (PostgreSQL / Redis / Vector Store)
                |
                +--> Async Tasks (Celery Worker)

Cross-cutting: policy engine, feature flags, runtime backpressure, immutable audit.
```

---

## 4. Main Components

### 4.1 API Application (`apps/api/app`)

Key responsibilities:

- Exposes HTTP endpoints by bounded domains (`routers/`).
- Applies request middleware for authentication, tenancy, and budget/circuit-breaker logic.
- Coordinates business workflows through services.
- Records structured logs and audit events.

Important modules:

- `main.py`: FastAPI bootstrap and router registration.
- `middleware/`: auth, tenant context, and cost safeguards.
- `routers/`: domain endpoints (inference, pipelines, governance, costs, knowledge base, etc.).
- `services/`: orchestrator, model routing, cost tracking, audit, and PII detection.
- `models/`: ORM entities for tenant/user/audit/cost/API key/knowledge base domains.

### 4.2 Worker Application (`apps/worker`)

Celery-based async execution for background operations:

- indexing pipelines;
- evaluation routines;
- cost reporting tasks.

### 4.3 Security & Governance Modules

Top-level modules provide enforcement primitives:

- `security/`: prompt injection detection, jailbreak classification, output validation.
- `governance/immutable_audit.py`: tamper-evident audit chain behavior.
- `policy-engine/`: rules and policy evaluation.
- `runtime-control/backpressure.py`: system protection during load spikes.

### 4.4 Feature and Rollout Controls

- `feature-flags/rollout_manager.py` and `feature-flags/model_rollout.yaml` define controlled rollout mechanics and gradual model exposure.

---

## 5. Request Lifecycle

1. Client sends request to API endpoint.
2. Middleware resolves identity, tenant scope, and budget guardrails.
3. Router delegates to service layer.
4. Service layer may:
   - route model/provider;
   - run safety checks;
   - execute orchestration;
   - persist inference/cost/audit metadata.
5. Response is returned to client.
6. Optional async tasks are queued for post-processing and analytics.

---

## 6. Data and State

Primary persistence concerns:

- relational data (tenants, users, API keys, logs, costs, KB metadata) in SQL models under `apps/api/app/models/`;
- cache/session/rate state in Redis (`apps/api/app/cache.py` and runtime modules);
- vector retrieval primitives in `data/vector_store.py`;
- migration bootstrap in `data/migrations/001_init.sql`.

---

## 7. Observability and Operations

Infrastructure observability assets are under `infra/observability/`:

- OpenTelemetry collector config;
- Prometheus and Loki configuration;
- Jaeger tracing support;
- Grafana dashboard definitions;
- region/fallback operational policies.

Load and resilience artifacts:

- `load-testing/locustfile.py`
- `load-testing/stress_test.yaml`

---

## 8. Deployment Topology

Deployment-related assets are split by concern:

- `docker-compose.yml` for local composition;
- `infra/helm/` for Kubernetes packaging;
- `infra/terraform/` for infrastructure provisioning.

Recommended environments:

- local dev (single-node, mock/real providers as needed);
- staging (production-like policies and observability enabled);
- production (strict governance, HA data stores, full telemetry).

---

## 9. Security Posture

Security controls are designed as layered defenses:

- API-level auth and key management;
- tenant isolation middleware;
- prompt and output safety validators;
- immutable audit chain for forensic integrity;
- governance endpoints for policy visibility and operations.

For regulated environments, combine policy engine rules with documented data-sovereignty and audit workflows from the existing architecture documents.

---

## 10. Testing Strategy

Current test suite includes policy/budget and runtime/audit paths:

- `tests/test_policy_and_budget.py`
- `tests/test_backpressure_and_audit.py`

Recommended CI validation baseline:

1. static checks/linters;
2. unit tests;
3. contract tests for critical routers;
4. smoke tests for orchestration and worker queue health.

---

## 11. Documentation Map

Use this sequence for onboarding:

1. `README.md` — project entrypoint.
2. `docs/nexusai-documentacao.md` — complete PT-BR narrative.
3. `docs/nexusai-implementation-blueprint.md` — implementation blueprint.
4. `docs/nexusai-enterprise-architecture.md` — enterprise architecture deep dive.
5. `docs/nexusai-production-hardening-plan.md` — hardening roadmap.
6. `docs/reference/` — language- and stack-specific reference artifacts.

---

## 12. Known Gaps and Next Improvements

Suggested follow-up improvements:

- define architecture decision records (ADRs) for orchestrator and policy engine evolution;
- document SLO/SLI targets and alert routing ownership;
- formalize incident response and rollback runbooks;
- add end-to-end trace examples from request to audit record;
- version the external API contract and SDK compatibility matrix.

