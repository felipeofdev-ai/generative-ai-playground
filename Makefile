.PHONY: test lint api-up down

test:
	pytest -q

lint:
	python -m compileall apps/api/app

api-up:
	docker compose up -d postgres redis api gateway mesh web

down:
	docker compose down
