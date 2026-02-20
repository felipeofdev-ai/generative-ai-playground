# NexusAI / Generative AI Playground

Monorepo com playgrounds de IA generativa e um stack funcional de orquestração **NexusAI** (API FastAPI, gateway Rust, worker Celery, mesh Go e web Next.js).

## O que está funcional neste PR

- API FastAPI em `apps/api` com endpoint de saúde e rotas Nexus.
- Gateway Rust em `gateway-rust` para proxy/rate-limit.
- Worker Celery em `apps/worker`.
- Mesh service em Go em `mesh-go`.
- Frontend base Next.js em `apps/web`.
- Stack local de desenvolvimento via `docker-compose.yml`.

## Estrutura principal

- `apps/api/` — API Python/FastAPI
- `apps/worker/` — processamento assíncrono (Celery)
- `gateway-rust/` — API gateway
- `mesh-go/` — serviço de eventos/malha
- `apps/web/` — frontend Next.js
- `infra/docker/postgres-init.sql` — init script do Postgres
- `docker-compose.yml` — orquestração local

## Pré-requisitos

- Python 3.12+
- Docker + Docker Compose
- (opcional) Rust/Go/Node para rodar serviços fora do compose

## Configuração rápida

1. Copie variáveis de ambiente:

```bash
cp .env.example .env
```

2. Ajuste chaves/API keys no `.env`.

3. Suba stack:

```bash
docker compose up -d --build
```

4. Verifique serviços:

- API: `http://localhost:8000/health`
- Gateway: `http://localhost:8080/health`
- Mesh: `http://localhost:9000/health`
- Web: `http://localhost:3000`

## Desenvolvimento local (sem docker)

### API
```bash
pip install -r requirements.txt
uvicorn apps.api.app.main:app --reload --port 8000
```

### Testes
```bash
pytest -q
python -m compileall apps/api/app
```

## Variáveis importantes

Veja `.env.example`. Destaques:

- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`
- `MIGRATE_ON_START`
- `NEXT_PUBLIC_API_URL`

## Observações

- `MIGRATE_ON_START=1` tenta rodar Alembic no container da API **somente se** `alembic.ini` existir.
- Se estiver apenas no modo playground, mantenha `MIGRATE_ON_START=0`.

## Documentação adicional

- `docs/nexusai-documentacao.md`
- `docs/nexusai-implementation-blueprint.md`
- `docs/nexusai-enterprise-architecture.md`
- `docs/nexusai-production-hardening-plan.md`
