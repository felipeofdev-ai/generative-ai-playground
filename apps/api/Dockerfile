FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Merge-safe startup behavior:
# - run migration only when explicitly requested
# - only attempt migration when alembic.ini exists
# - start API as PID 1 process via exec
CMD ["sh", "-c", "if [ \"${MIGRATE_ON_START:-0}\" = \"1\" ] && [ -f alembic.ini ]; then alembic upgrade head; fi; exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
