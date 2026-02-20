# Generative AI Playground

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
│   └── worker/
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

## Documentation

- System overview (EN): `docs/SYSTEM_DOCUMENTATION.md`
- Full documentation (PT-BR): `docs/nexusai-documentacao.md`
- Implementation blueprint (EN): `docs/nexusai-implementation-blueprint.md`
- Enterprise architecture (PT-BR): `docs/nexusai-enterprise-architecture.md`
- ADK integration plan (PT-BR): `docs/nexusai-adk-integration-plan.md`
- Production hardening plan (PT-BR): `docs/nexusai-production-hardening-plan.md`
- Reference artifacts: `docs/reference/`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and configure provider credentials.
4. Run local services with your preferred workflow (`docker-compose`, direct FastAPI + worker, etc.).

## Author

Felipe Oliveira
Python Developer | Backend | Automation | Generative AI
