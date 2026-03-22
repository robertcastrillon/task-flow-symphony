.PHONY: dev test lint format

dev:
	docker compose up -d

down:
	docker compose down

test:
	cd apps/api && python -m pytest --tb=short -q
	cd apps/web && npm test -- --run

lint:
	cd apps/api && ruff check . && ruff format --check .
	cd apps/web && npx eslint . && npx prettier --check .

format:
	cd apps/api && ruff check --fix . && ruff format .
	cd apps/web && npx eslint --fix . && npx prettier --write .

migrate:
	cd apps/api && alembic upgrade head

migration:
	cd apps/api && alembic revision --autogenerate -m "$(msg)"
