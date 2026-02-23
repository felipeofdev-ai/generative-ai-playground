# NexusAI — Developer Makefile

.PHONY: help dev docker-up docker-down test lint clean

help:
	@echo "NexusAI Platform v3.0 — Available commands:"
	@echo "  make docker-up    Start full stack with Docker Compose"
	@echo "  make docker-down  Stop all containers"
	@echo "  make test         Run Python tests"
	@echo "  make lint         Compile-check Python modules"


docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

test:
	pytest -q

lint:
	python -m compileall apps/api/app
	python -m compileall apps/worker

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
