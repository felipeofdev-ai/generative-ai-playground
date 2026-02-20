# NexusAI / Generative AI Playground

Stack local consolidada para desenvolvimento com:

- FastAPI (`apps/api`)
- Celery worker (`apps/worker`)
- Rust gateway (`gateway-rust`)
- Go mesh (`mesh-go`)
- Next.js web (`apps/web`)
- PostgreSQL + Redis via `docker-compose.yml`

## Como subir

```bash
cp .env.example .env
docker compose up -d --build
```

## Endpoints

- API health: `http://localhost:8000/health`
- Gateway health: `http://localhost:8080/health`
- Mesh health: `http://localhost:9000/health`
- Web: `http://localhost:3000`

## Sobre migração no boot

O container da API roda migração apenas quando:

- `MIGRATE_ON_START=1`
- e `alembic.ini` existir no diretório da API

Caso contrário, sobe direto com `uvicorn`.

## Comandos úteis

```bash
make test
make lint
make api-up
make down
```
