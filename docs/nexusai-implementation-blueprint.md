# NexusAI — World's Most Advanced GenAI Platform

> Enterprise-grade, multi-model AI orchestration platform built for Fortune 500.

## Architecture Overview

NexusAI is a **polyglot microservices** platform where each language is chosen for what it does best:

| Layer | Language | Framework | Role |
|---|---|---|---|
| Frontend | TypeScript | Next.js 15 | UI, dashboards, chat |
| API Core | Python | FastAPI | AI orchestration, RAG, business logic |
| Gateway | Rust | Axum | High-perf request gateway, rate limiting |
| Mesh | Go | Fiber | AI-to-AI communication, WebSocket hub |
| Pipelines | Kotlin | Ktor | Enterprise workflow engine |
| Workers | Python | Celery | Async indexing, evals, reports |
| CLI | Python | Typer | Developer tooling |

## Services Communication

```text
Browser → Rust Gateway → Python API → NEXUS Orchestrator
                       → Go WebSocket Hub → Browser (realtime)
                       → Kafka → Kotlin Pipeline Engine
                       → Celery → Python Workers
```

## Quick Start (Development)

```bash
# Clone
git clone https://github.com/nexusai/platform.git
cd nexusai

# Start all services
docker compose -f infrastructure/docker/docker-compose.yml up -d

# Web app
cd apps/web && npm install && npm run dev

# API
cd apps/api && pip install -e ".[dev]" && uvicorn app.main:app --reload --port 8001

# Gateway (Rust)
cd apps/gateway-rust && cargo run

# Mesh (Go)
cd apps/mesh-go && go run ./cmd

# Pipeline Engine (Kotlin)
cd apps/pipeline-engine-kotlin && ./gradlew run
```

## Repository Structure

```text
nexusai/
├── apps/
│   ├── web/                    # Next.js 15 frontend (TypeScript)
│   ├── api/                    # FastAPI backend (Python)
│   ├── worker/                 # Celery workers (Python)
│   ├── cli/                    # CLI tool (Python/Typer)
│   ├── gateway-rust/           # High-perf gateway (Rust/Axum)
│   ├── mesh-go/                # AI Mesh & WebSocket hub (Go/Fiber)
│   └── pipeline-engine-kotlin/ # Pipeline engine (Kotlin/Ktor)
├── packages/
│   ├── protos/                 # gRPC Protocol Buffers (shared)
│   ├── nexus-sdk-python/       # Python SDK (public)
│   └── nexus-sdk-typescript/   # TypeScript SDK (public)
├── infrastructure/
│   ├── docker/                 # Docker Compose configs
│   ├── kubernetes/             # K8s manifests
│   └── terraform/              # Infrastructure as Code
├── docs/
└── .github/workflows/
```

## Tech Stack

- **Databases:** PostgreSQL 16 + pgvector + TimescaleDB, Redis 7
- **Messaging:** Apache Kafka (inter-service events)
- **Observability:** OpenTelemetry, Prometheus, Grafana, Sentry
- **Auth:** JWT + OAuth2 + SAML/SSO (Auth0)
- **Infrastructure:** AWS (EKS, RDS, ElastiCache, S3), Terraform, ArgoCD

## Compliance & Certifications

- SOC 2 Type II ✅
- ISO 27001 / 27017 / 27018 ✅
- GDPR / LGPD / CCPA / PDPA ✅
- HIPAA BAA Available ✅
- FedRAMP (In Progress) 🔄

## Additional high-impact improvements (beyond previous lists)

1. **Deterministic replay mode** for incident forensics (replay full inference traces).
2. **Tenant-level model policies** (allow/deny models and jurisdictions).
3. **Inference quality SLOs** (quality budgets alongside uptime budgets).
4. **Synthetic tenant canaries** to detect regressions before customer impact.
5. **Secure prompt vault** with signed prompt bundles and attestation.
6. **Automated vendor risk scoring** for each model provider.
7. **Data lifecycle automation** (retention, legal hold, right-to-be-forgotten workflows).
8. **Regional kill-switches** for provider outages and legal restrictions.
9. **Streaming backpressure controls** and adaptive chunking for UX stability.
10. **Trust scorecard API** for CIO/CISO reporting consumption.

## Blueprint files included in this repository

This repository now includes concrete reference blueprints in `docs/blueprints/`:

- `docker-compose.nexusai.yml`
- `apps-api-pyproject.toml`
- `config.py`
- `main.py`
- `nexus_orchestrator.py`
- `model_router.py`

## ADK Integration

To maximize agent capabilities, NexusAI should adopt Google ADK components as the agent runtime layer integrated with NEXUS orchestration, policy middleware, and evaluation harnesses. See `docs/nexusai-adk-integration-plan.md`.

## License

Proprietary — All rights reserved © 2025 NexusAI Inc.
