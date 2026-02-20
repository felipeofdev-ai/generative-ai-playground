FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Safe startup for merge compatibility:
# - migrations are opt-in (MIGRATE_ON_START=1)
# - migrations only run when alembic.ini exists
# - API process always replaces shell via exec
CMD ["sh", "-c", "if [ \"${MIGRATE_ON_START:-0}\" = \"1\" ] && [ -f alembic.ini ]; then alembic upgrade head; fi; exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
