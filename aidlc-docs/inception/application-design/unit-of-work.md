# Units of Work — TaskFlow

## Decomposition Summary
6 units of work, executed sequentially with dependencies.

---

## Unit 1: Project Setup & Infrastructure
- **Type**: Infrastructure
- **Scope**: Monorepo scaffolding, Docker Compose, Makefile, GitHub Actions CI, PostgreSQL setup, Alembic init, base FastAPI app, base React app
- **Components**: Docker configs, Makefile, CI workflow, docker-compose.yml, pyproject.toml, package.json, base app shells
- **Dependencies**: None (first unit)
- **Construction Stages**: Full loop (Functional Design, NFR Requirements, NFR Design, Infrastructure Design, Code Generation)

---

## Unit 2: Backend — Auth Module
- **Type**: Backend Module
- **Scope**: User registration, login, JWT token management, refresh tokens, password hashing, rate limiting on auth, security middleware, auth dependencies
- **Components**: COMP-B01 (Auth Router), COMP-B06 (Auth Service), COMP-B11 (User Model), COMP-B14 (Auth Schemas), COMP-B15 (User Schemas), COMP-B19 (Security), COMP-B20 (Config), COMP-B21 (Dependencies), COMP-B22 (DB Session), COMP-B23 (Middleware), COMP-B24 (Main App updates)
- **Dependencies**: Unit 1 (project structure, DB, base app)
- **Construction Stages**: Full loop

---

## Unit 3: Backend — Tasks & Users Module
- **Type**: Backend Module
- **Scope**: Task CRUD, status changes, assignment, filtering/pagination, soft delete, user listing/detail/update, Alembic migration for tasks
- **Components**: COMP-B02 (Users Router), COMP-B03 (Tasks Router), COMP-B07 (User Service), COMP-B08 (Task Service), COMP-B12 (Task Model), COMP-B16 (Task Schemas)
- **Dependencies**: Unit 2 (auth system, User model, dependencies)
- **Construction Stages**: Full loop

---

## Unit 4: Backend — Comments & Dashboard Module
- **Type**: Backend Module
- **Scope**: Comment CRUD on tasks, dashboard statistics aggregation, Alembic migration for comments
- **Components**: COMP-B04 (Comments Router), COMP-B05 (Dashboard Router), COMP-B09 (Comment Service), COMP-B10 (Dashboard Service), COMP-B13 (Comment Model), COMP-B17 (Comment Schemas), COMP-B18 (Dashboard Schemas)
- **Dependencies**: Unit 3 (Task model, User model, task endpoints)
- **Construction Stages**: Full loop

---

## Unit 5: Frontend Web
- **Type**: Frontend Application
- **Scope**: All React pages, components, hooks, API client, auth context, routing, DaisyUI styling
- **Components**: COMP-F01 through COMP-F22 (all frontend components)
- **Dependencies**: Units 2-4 (all API endpoints must exist)
- **Construction Stages**: Full loop

---

## Unit 6: Integration & GCP Deployment
- **Type**: Infrastructure / DevOps
- **Scope**: GCP Cloud Run configuration, Cloud SQL setup, staging deployment, GitHub Actions deploy workflow, production Docker optimizations
- **Components**: Dockerfiles (production), Cloud Run configs, GitHub Actions deploy-staging.yml
- **Dependencies**: Units 1-5 (full application must be functional)
- **Construction Stages**: Full loop

---

## Execution Order

```
Unit 1: Setup & Infra ──> Unit 2: Auth ──> Unit 3: Tasks & Users ──> Unit 4: Comments & Dashboard ──> Unit 5: Frontend ──> Unit 6: GCP Deploy
```

All units are sequential — each depends on the previous.

## Code Organization Strategy (Greenfield)

```
taskflow/                          # Workspace root
+-- apps/
|   +-- api/                       # Units 2, 3, 4
|   |   +-- app/
|   |   |   +-- main.py
|   |   |   +-- models/
|   |   |   |   +-- __init__.py
|   |   |   |   +-- user.py
|   |   |   |   +-- task.py
|   |   |   |   +-- comment.py
|   |   |   +-- schemas/
|   |   |   |   +-- auth.py
|   |   |   |   +-- user.py
|   |   |   |   +-- task.py
|   |   |   |   +-- comment.py
|   |   |   |   +-- dashboard.py
|   |   |   +-- routers/
|   |   |   |   +-- auth.py
|   |   |   |   +-- users.py
|   |   |   |   +-- tasks.py
|   |   |   |   +-- comments.py
|   |   |   |   +-- dashboard.py
|   |   |   +-- services/
|   |   |   |   +-- auth_service.py
|   |   |   |   +-- user_service.py
|   |   |   |   +-- task_service.py
|   |   |   |   +-- comment_service.py
|   |   |   |   +-- dashboard_service.py
|   |   |   +-- core/
|   |   |   |   +-- config.py
|   |   |   |   +-- security.py
|   |   |   |   +-- deps.py
|   |   |   |   +-- middleware.py
|   |   |   +-- db/
|   |   |       +-- session.py
|   |   +-- alembic/
|   |   +-- tests/
|   |   +-- pyproject.toml
|   |   +-- Dockerfile
|   |
|   +-- web/                       # Unit 5
|       +-- src/
|       |   +-- App.tsx
|       |   +-- pages/
|       |   +-- components/
|       |   +-- hooks/
|       |   +-- services/
|       +-- package.json
|       +-- Dockerfile
|       +-- vite.config.ts
|       +-- tailwind.config.js
|
+-- docker-compose.yml             # Unit 1
+-- docker-compose.test.yml        # Unit 1
+-- Makefile                       # Unit 1
+-- .github/
|   +-- workflows/
|       +-- ci.yml                 # Unit 1
|       +-- deploy-staging.yml     # Unit 6
+-- CLAUDE.md
+-- prd.md
```
