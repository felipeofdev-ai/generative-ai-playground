# NexusAI — Enterprise GenAI Platform

Stack local com API FastAPI, worker Celery, gateway Rust, mesh Go e frontend Next.js.

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up -d --build
```

Acessos:

- Web UI: http://localhost:3000
- API docs: http://localhost:8000/docs
- Gateway health: http://localhost:8080/health
- Mesh health: http://localhost:9000/health

## Observações importantes

- `MIGRATE_ON_START=1` só roda migração se `alembic.ini` existir.
- Com `MIGRATE_ON_START=0`, sobe direto `uvicorn`.

## Desenvolvimento

```bash
make test
make lint
```

## Arquitetura

- `apps/api` — FastAPI + Nexus router/services
- `apps/worker` — Celery workers
- `gateway-rust` — gateway/rate limiting
- `mesh-go` — event mesh service
- `apps/web` — Next.js
