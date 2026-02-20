# NexusAI / Generative AI Playground

Monorepo com playgrounds de IA generativa e uma stack local do NexusAI (API FastAPI, worker Celery, gateway Rust, mesh Go e web Next.js).

## Status desta branch

- Conflitos de merge resolvidos em:
  - `README.md`
  - `apps/api/Dockerfile`
  - `docker-compose.yml`
- Compose consolidado com serviços existentes no repositório.
- Startup da API seguro para cenários com/sem Alembic (`MIGRATE_ON_START`).

## Serviços da stack local

- `postgres` (pgvector)
- `redis`
- `api` (`apps/api`)
- `worker` (`apps/worker`)
- `gateway` (`gateway-rust`)
- `mesh` (`mesh-go`)
- `web` (`apps/web`)

## Setup rápido

```bash
cp .env.example .env
docker compose up -d --build
```

Endpoints esperados:

- API: `http://localhost:8000/health`
- Gateway: `http://localhost:8080/health`
- Mesh: `http://localhost:9000/health`
- Web: `http://localhost:3000`

## Variáveis importantes

Veja `.env.example`:

- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`
- `MIGRATE_ON_START` (default `0`)
- `NEXT_PUBLIC_API_URL`

## Comandos úteis

```bash
make test
make lint
make api-up
make down
```

## Observação sobre migração

O container da API só tenta rodar `alembic upgrade head` quando:

1. `MIGRATE_ON_START=1`
2. `alembic.ini` existe no diretório da API

Se não, sobe diretamente o `uvicorn`.

## Documentação

- `docs/nexusai-documentacao.md`
- `docs/nexusai-implementation-blueprint.md`
- `docs/nexusai-enterprise-architecture.md`
- `docs/nexusai-production-hardening-plan.md`
