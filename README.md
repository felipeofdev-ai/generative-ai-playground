# NexusAI — Enterprise GenAI Platform

This repository contains practical experiments and projects involving Generative AI and LLM-based platform components.

## Topics Covered

- Prompt engineering
- LLM API integrations
- Text generation and summarization
- AI-powered automation
- Multi-model orchestration patterns
- Governance, cost control, and operational safety

## Technologies

- Python 3
- FastAPI / Celery / SQLAlchemy
- OpenAI-compatible provider integrations
- Redis / PostgreSQL
- Docker / Terraform / Helm

## Project Structure

```text
generative-ai-playground/
├── apps/
│   ├── api/
│   ├── worker/
│   ├── web/
│   └── pipeline-kotlin/
├── gateway-rust/
├── mesh-go/
├── security/
├── policy-engine/
├── runtime-control/
├── governance/
├── feature-flags/
├── infra/
├── docs/
├── tests/
└── README.md
```

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up -d --build
```

Endpoints:

- Web UI: http://localhost:3000
- API docs: http://localhost:8000/docs
- Gateway health: http://localhost:8080/health
- Mesh health: http://localhost:9000/health

## Migration Behavior

- `MIGRATE_ON_START=1` runs migration **only if** `alembic.ini` exists.
- `MIGRATE_ON_START=0` starts API directly with `uvicorn`.

## Documentation

- `docs/nexusai-documentacao.md`
- `docs/nexusai-implementation-blueprint.md`
- `docs/nexusai-enterprise-architecture.md`
- `docs/nexusai-adk-integration-plan.md`
- `docs/nexusai-production-hardening-plan.md`
