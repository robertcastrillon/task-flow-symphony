<<<<<<< HEAD
.PHONY: dev test lint format

=======
.PHONY: dev test lint format clean

# Full stack
>>>>>>> origin/eng-88
dev:
	docker compose up -d

down:
	docker compose down

<<<<<<< HEAD
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
=======
# Backend
test-api:
	cd apps/api && pytest --cov --cov-report=term-missing

lint-api:
	cd apps/api && ruff check .

format-api:
	cd apps/api && ruff format .

# Frontend
test-web:
	cd apps/web && npm run test

lint-web:
	cd apps/web && npm run lint

# Combined
test: test-api test-web

lint: lint-api lint-web

format: format-api

# Docker test environment
test-docker:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
>>>>>>> origin/eng-88
