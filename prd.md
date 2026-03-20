# PRD: TaskFlow — Gestión de Tareas Inteligente

## Resumen Ejecutivo

TaskFlow es una aplicación web de gestión de tareas y personas con integración a Telegram. Permite a equipos pequeños crear, asignar y dar seguimiento a tareas desde la web o directamente desde un chat de Telegram.

**Objetivo:** Validar el framework AI Factory (AI-DLC → Symphony → Claude Code) construyendo un producto real de punta a punta en dos iteraciones.

---

## Stack Técnico

| Capa | Tecnología |
|---|---|
| Backend API | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Base de datos | PostgreSQL 16 |
| Frontend | React 18, Vite, TailwindCSS, React Query |
| Bot | python-telegram-bot (fase 2) |
| Contenedores | Docker, docker-compose |
| CI/CD | GitHub Actions |
| IaC | Docker Compose (local/staging), cloud-agnostico |

---

## Arquitectura del Monorepo

```
taskflow/
├── apps/
│   ├── api/                  # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── routers/      # API endpoints
│   │   │   ├── services/     # Business logic
│   │   │   ├── db/           # Database config, migrations
│   │   │   └── core/         # Config, security, deps
│   │   ├── tests/
│   │   ├── alembic/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── web/                  # React frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── hooks/
│   │   │   ├── services/     # API client
│   │   │   └── App.tsx
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   └── bot/                  # Telegram bot (Fase 2)
│       ├── bot/
│       │   ├── main.py
│       │   ├── handlers/
│       │   └── services/
│       ├── Dockerfile
│       └── pyproject.toml
│
├── packages/
│   └── shared/               # Tipos compartidos, constantes
│
├── docker-compose.yml        # Levanta todo: api + web + db + bot
├── docker-compose.test.yml   # Para CI/CD
├── CLAUDE.md                 # Convenciones del proyecto
├── Makefile                  # Shortcuts: make dev, make test, make lint
└── .github/
    └── workflows/
        ├── ci.yml            # Tests + lint en cada PR
        └── deploy-staging.yml # Deploy a staging desde develop
```

---

## Fase 1: Core — Gestión de Tareas y Personas

### Entidades del Dominio

```
User (persona/miembro del equipo)
├── id: UUID
├── email: str (unique)
├── name: str
├── avatar_url: str?
├── role: enum (admin, member)
├── telegram_chat_id: str? (para fase 2)
├── created_at: datetime
└── is_active: bool

Task (tarea)
├── id: UUID
├── title: str
├── description: str?
├── status: enum (todo, in_progress, done, cancelled)
├── priority: enum (low, medium, high, urgent)
├── due_date: date?
├── created_by: FK → User
├── assigned_to: FK → User?
├── tags: list[str]
├── created_at: datetime
├── updated_at: datetime
└── completed_at: datetime?

Comment (comentario en tarea)
├── id: UUID
├── task_id: FK → Task
├── author_id: FK → User
├── content: str
├── created_at: datetime
└── updated_at: datetime
```

### API Endpoints (FastAPI)

```
# Auth
POST   /api/v1/auth/register        # Registro
POST   /api/v1/auth/login            # Login → JWT
GET    /api/v1/auth/me               # Perfil actual

# Users
GET    /api/v1/users                 # Listar miembros
GET    /api/v1/users/{id}            # Detalle
PATCH  /api/v1/users/{id}            # Actualizar perfil

# Tasks
GET    /api/v1/tasks                 # Listar (filtros: status, assignee, priority, tag)
POST   /api/v1/tasks                 # Crear
GET    /api/v1/tasks/{id}            # Detalle
PATCH  /api/v1/tasks/{id}            # Actualizar
DELETE /api/v1/tasks/{id}            # Eliminar (soft delete)
PATCH  /api/v1/tasks/{id}/status     # Cambiar estado
PATCH  /api/v1/tasks/{id}/assign     # Asignar a usuario

# Comments
GET    /api/v1/tasks/{id}/comments   # Listar comentarios
POST   /api/v1/tasks/{id}/comments   # Agregar comentario

# Dashboard
GET    /api/v1/dashboard/stats       # Resumen: total, por estado, por usuario, overdue
```

### Frontend (React)

#### Páginas

1. **Login / Register** — Formularios simples con JWT
2. **Dashboard** — Resumen visual: tareas por estado (cards), tareas vencidas, actividad reciente
3. **Task Board** — Vista Kanban con columnas: Todo, In Progress, Done (drag & drop)
4. **Task List** — Vista tabla con filtros, búsqueda, ordenamiento
5. **Task Detail** — Modal/página con descripción, comentarios, historial, asignación
6. **Team** — Lista de miembros, invitar, roles

#### Componentes Clave

- `TaskCard` — Card en el board con título, prioridad (color), asignado (avatar), due date
- `TaskForm` — Crear/editar tarea
- `KanbanBoard` — Columnas con drag & drop (dnd-kit)
- `FilterBar` — Filtros por estado, prioridad, asignado, tags
- `CommentThread` — Lista de comentarios con formulario de respuesta
- `StatCard` — Métricas del dashboard

### Criterios de Aceptación — Fase 1

```gherkin
Feature: Gestión de tareas
  Scenario: Crear una tarea nueva
    Given estoy autenticado como miembro del equipo
    When creo una tarea con título "Diseñar landing page" y prioridad "high"
    Then la tarea aparece en la columna "Todo" del board
    And la tarea tiene mi usuario como creador

  Scenario: Mover tarea en el board
    Given existe la tarea "Diseñar landing page" en "Todo"
    When arrastro la tarea a la columna "In Progress"
    Then el estado de la tarea se actualiza a "in_progress"
    And la fecha de última actualización cambia

  Scenario: Asignar tarea a un miembro
    Given existe la tarea "Diseñar landing page"
    When asigno la tarea al usuario "maria@team.com"
    Then la tarea muestra el avatar de María
    And María puede ver la tarea en su vista filtrada

  Scenario: Filtrar tareas por prioridad
    Given existen tareas con prioridades variadas
    When filtro por prioridad "urgent"
    Then solo veo las tareas marcadas como urgentes

  Scenario: Dashboard muestra estadísticas
    Given existen 10 tareas: 3 todo, 5 in_progress, 2 done
    When accedo al dashboard
    Then veo las métricas correctas por estado
    And veo las tareas vencidas resaltadas
```

### Requisitos No Funcionales — Fase 1

- API response time < 200ms para listados (paginados, 50 items max)
- JWT con expiración 24h + refresh token
- Validación de inputs con Pydantic (backend) y Zod (frontend)
- Tests: >= 80% coverage en backend, tests de componentes clave en frontend
- Migraciones de DB con Alembic (versionadas, reversibles)
- CORS configurado para desarrollo local
- Rate limiting en endpoints de auth (5 req/min)
- Logs estructurados con structlog

---

## Fase 2: Telegram Bot — Canal Conversacional

### Comandos del Bot

```
/start              → Vincular cuenta TaskFlow con Telegram
/tasks              → Listar mis tareas pendientes
/new <título>       → Crear tarea rápida
/done <id|título>   → Marcar tarea como completada
/assign <id> @user  → Asignar tarea
/status             → Resumen rápido (cuántas pendientes, urgentes, vencidas)
/help               → Lista de comandos
```

### Flujos del Bot

```
Usuario: /new Preparar presentación para el viernes
Bot: Tarea creada: "Preparar presentación para el viernes"
     ID: TSK-42 | Prioridad: medium | Estado: todo
     ¿Quieres asignarla a alguien? Responde con @nombre o /skip

Usuario: /tasks
Bot: Tus tareas pendientes (3):
     🔴 TSK-38: Revisar PR de auth [urgent] - vence hoy
     🟡 TSK-42: Preparar presentación [medium] - vie 28
     🟢 TSK-35: Actualizar docs [low] - sin fecha

Usuario: /done TSK-38
Bot: ✅ TSK-38 "Revisar PR de auth" marcada como completada.
     Quedan 2 tareas pendientes.
```

### Criterios de Aceptación — Fase 2

```gherkin
Feature: Bot de Telegram
  Scenario: Vincular cuenta
    Given tengo una cuenta en TaskFlow con email "user@team.com"
    When envío /start al bot
    And proporciono mi email y código de verificación
    Then mi chat de Telegram queda vinculado a mi cuenta TaskFlow

  Scenario: Crear tarea desde Telegram
    Given mi cuenta está vinculada al bot
    When envío "/new Revisar código del módulo de pagos"
    Then se crea la tarea en TaskFlow con estado "todo"
    And el bot confirma con el ID de la tarea

  Scenario: Listar tareas pendientes
    Given tengo 3 tareas asignadas (2 pendientes, 1 completada)
    When envío /tasks
    Then el bot muestra solo las 2 tareas pendientes
    And las ordena por prioridad

  Scenario: Completar tarea
    Given existe la tarea TSK-42 asignada a mí
    When envío "/done TSK-42"
    Then la tarea se marca como completada en TaskFlow
    And el bot confirma la acción
```

### Requisitos Técnicos — Fase 2

- Webhook mode (no polling) para Telegram
- Cola de mensajes para operaciones async (evitar timeouts de Telegram)
- Vinculación de cuenta con código OTP de 6 dígitos (expira en 10 min)
- Notificaciones push: tarea asignada, tarea vencida (cron diario)
- Rate limiting por chat_id (30 msg/min)

---

## Plan de Iteraciones

### Iteración 1 — Core (Fase 1)
1. Setup monorepo + Docker + CI base
2. API: Auth (register/login/JWT)
3. API: CRUD Users
4. API: CRUD Tasks + filtros + paginación
5. API: Comments
6. API: Dashboard stats
7. Frontend: Auth pages
8. Frontend: Dashboard
9. Frontend: Kanban Board con drag & drop
10. Frontend: Task detail + comments
11. Frontend: Team management
12. E2E tests + BDD validation

### Iteración 2 — Bot (Fase 2)
1. Setup bot service + Telegram webhook
2. /start — Vinculación de cuenta
3. /new + /tasks + /done — Operaciones core
4. /assign + /status — Operaciones secundarias
5. Notificaciones push
6. E2E tests bot

---

## Definición de Done (por ticket)

- [ ] Código implementado siguiendo TDD (red-green-refactor)
- [ ] Tests unitarios >= 80% coverage
- [ ] Tests de integración para endpoints API
- [ ] Lint + format passing (ruff, eslint + prettier)
- [ ] Sin secretos hardcodeados
- [ ] Sin vulnerabilidades OWASP Top 10
- [ ] Docker build exitoso
- [ ] Servicios levantan con docker-compose
- [ ] Documentación de API actualizada (OpenAPI auto-generado)
- [ ] PR creado contra branch `develop`
