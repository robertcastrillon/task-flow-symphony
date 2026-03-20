# TaskFlow — Requirements Document

## Intent Analysis

- **User Request**: Build the TaskFlow product described in prd.md using AI-DLC methodology
- **Request Type**: New Project (greenfield)
- **Scope Estimate**: System-wide — full-stack web application (API + Frontend + DB + Infrastructure)
- **Complexity Estimate**: Complex — multiple layers, authentication, real-time UI interactions, cloud deployment
- **Phase Scope**: Phase 1 only (Core — Tasks, Users, Auth, Dashboard, Frontend)

---

## Functional Requirements

### FR-01: User Authentication
- Register with email and password
- Login returns JWT (24h expiry) + refresh token
- `GET /api/v1/auth/me` returns current user profile
- Password hashing with adaptive algorithm (bcrypt/argon2)
- Rate limiting on auth endpoints: 5 req/min

### FR-02: User Management
- List team members (`GET /api/v1/users`)
- View user detail (`GET /api/v1/users/{id}`)
- Update user profile (`PATCH /api/v1/users/{id}`)
- User roles: `admin`, `member`
- Fields: id (UUID), email (unique), name, avatar_url?, role, telegram_chat_id?, created_at, is_active

### FR-03: Task Management (CRUD)
- Create task (`POST /api/v1/tasks`)
- List tasks with filters: status, assignee, priority, tag (`GET /api/v1/tasks`)
- View task detail (`GET /api/v1/tasks/{id}`)
- Update task (`PATCH /api/v1/tasks/{id}`)
- Delete task — soft delete (`DELETE /api/v1/tasks/{id}`)
- Change task status (`PATCH /api/v1/tasks/{id}/status`)
- Assign task to user (`PATCH /api/v1/tasks/{id}/assign`)
- Fields: id (UUID), title, description?, status (todo/in_progress/done/cancelled), priority (low/medium/high/urgent), due_date?, created_by (FK User), assigned_to? (FK User), tags (list[str]), created_at, updated_at, completed_at?

### FR-04: Comments
- List comments on a task (`GET /api/v1/tasks/{id}/comments`)
- Add comment to a task (`POST /api/v1/tasks/{id}/comments`)
- Fields: id (UUID), task_id (FK Task), author_id (FK User), content, created_at, updated_at

### FR-05: Dashboard
- Summary endpoint (`GET /api/v1/dashboard/stats`)
- Metrics: total tasks, tasks by status, tasks by user, overdue tasks

### FR-06: Frontend — Authentication Pages
- Login form (email + password)
- Registration form
- JWT stored client-side, sent as Authorization header

### FR-07: Frontend — Dashboard Page
- Visual summary: task count cards by status
- Overdue tasks highlighted
- Recent activity

### FR-08: Frontend — Kanban Board
- Columns: Todo, In Progress, Done
- Drag & drop with dnd-kit
- TaskCard shows: title, priority (color-coded), assignee avatar, due date
- Drag changes task status via API

### FR-09: Frontend — Task List
- Table view with filters, search, sorting
- FilterBar: status, priority, assignee, tags

### FR-10: Frontend — Task Detail
- Modal or page: description, comments, history, assignment
- CommentThread: list + reply form

### FR-11: Frontend — Team Page
- List of team members
- Role display

---

## Non-Functional Requirements

### NFR-01: Performance
- API response time < 200ms for paginated listings (max 50 items/page)

### NFR-02: Security
- JWT with 24h expiry + refresh token
- Bcrypt/argon2 password hashing
- Rate limiting on auth endpoints (5 req/min)
- CORS configured for local development and production origins
- All SECURITY rules (SECURITY-01 through SECURITY-15) enforced as blocking constraints
- HTTP security headers on all responses
- Input validation with Pydantic (backend) and Zod (frontend)
- Parameterized queries only (SQLAlchemy ORM)
- Object-level authorization (users can only access/modify their allowed resources)

### NFR-03: Testing
- Backend test coverage >= 80%
- pytest + pytest-asyncio
- Frontend: component tests for key components
- TDD approach (red-green-refactor)

### NFR-04: Database
- PostgreSQL 16
- Migrations with Alembic (versionable, reversible)
- SQLAlchemy 2.0 async

### NFR-05: Logging
- Structured logging with structlog
- Logs include: timestamp, correlation/request ID, log level, message
- No secrets/PII in logs

### NFR-06: Code Quality
- Python: ruff (lint + format)
- Frontend: eslint + prettier
- Dependency pinning via lock files

### NFR-07: Containerization
- Docker + docker-compose for local development
- Separate Dockerfiles per app (api, web)
- No `latest` tags in production Dockerfiles

---

## Technical Decisions

| Decision | Choice |
|---|---|
| Phase scope | Phase 1 only (Core) |
| Deployment | Local (Docker Compose) + GCP staging (Cloud Run + Cloud SQL) |
| Auth | Simple JWT email/password |
| UI Library | TailwindCSS + DaisyUI |
| Form handling | Zod + React Hook Form |
| Backend tests | pytest + pytest-asyncio |
| Python package manager | uv |
| Frontend package manager | npm |
| Monorepo tooling | None — simple directory structure |
| UI language | Spanish (es) |
| Security rules | All SECURITY rules enforced |

---

## Architecture Overview

```
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|   React (Vite)    | ----> |   FastAPI (API)   | ----> |  PostgreSQL 16    |
|   TailwindCSS     |  HTTP |   SQLAlchemy 2.0  |  SQL  |                   |
|   DaisyUI         |       |   Pydantic        |       |                   |
|                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+
     apps/web/                   apps/api/                  Docker / Cloud SQL
```

### Monorepo Structure
```
taskflow/
+-- apps/
|   +-- api/          # FastAPI backend (pyproject.toml, uv)
|   +-- web/          # React frontend (package.json, npm)
+-- docker-compose.yml
+-- Makefile
+-- .github/workflows/
```

---

## Acceptance Criteria Summary

1. User can register and login with email/password
2. Authenticated user can CRUD tasks with status, priority, assignee, tags
3. Tasks can be dragged between Kanban columns (Todo, In Progress, Done)
4. Tasks can be filtered by status, priority, assignee, tags
5. Dashboard shows task metrics and overdue tasks
6. Comments can be added to tasks
7. Team page lists members with roles
8. All API endpoints validated, authenticated, and authorized
9. Backend test coverage >= 80%
10. Full stack runs via `docker-compose up`
