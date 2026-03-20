# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaskFlow is a task management web app with Telegram bot integration, built for small teams. The project is structured as a monorepo with three apps: API (FastAPI), Web (React), and Bot (Telegram, Phase 2).

**Language:** The PRD and domain language are in Spanish. Code identifiers, comments, and git messages should be in English.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, structlog
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, React Query, Zod, dnd-kit
- **Database:** PostgreSQL 16
- **Bot (Phase 2):** python-telegram-bot
- **Infra:** Docker, docker-compose, GitHub Actions

## Monorepo Structure

```
taskflow/
├── apps/
│   ├── api/          # FastAPI backend (pyproject.toml)
│   ├── web/          # React frontend (package.json)
│   └── bot/          # Telegram bot - Phase 2 (pyproject.toml)
├── packages/shared/  # Shared types and constants
├── docker-compose.yml
├── Makefile
└── .github/workflows/
```

## Common Commands

```bash
# Full stack
make dev              # Start all services (api + web + db)
make test             # Run all tests
make lint             # Run linters (ruff for Python, eslint+prettier for frontend)

# Backend (apps/api/)
cd apps/api
pytest                          # Run all backend tests
pytest tests/test_foo.py::test_bar  # Run a single test
ruff check .                    # Lint
ruff format .                   # Format
alembic upgrade head            # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration

# Frontend (apps/web/)
cd apps/web
npm run dev           # Dev server
npm run test          # Run tests
npm run lint          # ESLint
npm run build         # Production build

# Docker
docker-compose up -d            # Start all services
docker-compose -f docker-compose.test.yml up  # CI test environment
```

## Architecture

### Backend (apps/api/app/)

Layered architecture with clear separation:
- **routers/** — API endpoint definitions (thin, delegate to services)
- **services/** — Business logic layer
- **models/** — SQLAlchemy ORM models (User, Task, Comment)
- **schemas/** — Pydantic request/response schemas
- **db/** — Database config and session management
- **core/** — Config, security (JWT), dependencies

### Domain Model

Three entities: **User** (team members, roles: admin/member), **Task** (status: todo/in_progress/done/cancelled, priority: low/medium/high/urgent), **Comment** (on tasks).

### API Conventions

- All routes under `/api/v1/`
- Auth via JWT (24h expiry + refresh token)
- Soft deletes for tasks
- Pagination with max 50 items per page
- Rate limiting on auth endpoints (5 req/min)

### Frontend (apps/web/src/)

- **pages/** — Route-level components (Login, Dashboard, TaskBoard, TaskList, TaskDetail, Team)
- **components/** — Reusable UI (TaskCard, TaskForm, KanbanBoard, FilterBar, CommentThread, StatCard)
- **hooks/** — Custom React hooks
- **services/** — API client layer (React Query)

## Quality Standards

- TDD approach (red-green-refactor)
- Backend test coverage >= 80%
- Linting: ruff (Python), eslint + prettier (TypeScript)
- DB migrations must be reversible (Alembic downgrade support)
- API response time < 200ms for paginated listings
- PR target branch: `develop`
