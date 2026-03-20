# Application Design — TaskFlow (Consolidated)

## Architecture Overview

TaskFlow is a monorepo with two applications communicating over HTTP REST:

```
+-------------------+       +-------------------+       +-------------------+
|   apps/web/       |       |   apps/api/       |       |   PostgreSQL 16   |
|   React 18 + Vite | HTTP  |   FastAPI         | async |                   |
|   TailwindCSS     +------>+   SQLAlchemy 2.0   +------>+   3 tables:       |
|   DaisyUI         |       |   Pydantic        |  pg   |   users, tasks,   |
|   React Query     |       |   structlog       |       |   comments        |
+-------------------+       +-------------------+       +-------------------+
```

## Technical Decisions Summary

| Decision | Choice |
|---|---|
| DB Operations | Fully async (asyncpg + SQLAlchemy async) |
| Client State | React Context (auth, UI) |
| Server State | React Query (data fetching/caching) |
| Error Format | Standard JSON `{"detail": "msg", "code": "CODE"}` |
| Routing | React Router v6 |
| Forms | Zod + React Hook Form |
| UI | TailwindCSS + DaisyUI |
| Drag & Drop | dnd-kit |

## Backend Architecture (apps/api/)

### Layer Structure
```
Routers (thin) --> Services (business logic) --> Models (ORM) --> PostgreSQL
    ^                    ^                           ^
    |                    |                           |
Schemas (Pydantic)   Security Module            DB Session (async)
```

### Components: 24 backend components
- **5 Routers**: Auth, Users, Tasks, Comments, Dashboard
- **5 Services**: AuthService, UserService, TaskService, CommentService, DashboardService
- **3 Models**: User, Task, Comment (SQLAlchemy)
- **5 Schema Sets**: Auth, User, Task, Comment, Dashboard (Pydantic)
- **6 Core**: Security, Config, Dependencies, Middleware, Database Session, Main App

### Key Patterns
- Dependency injection via FastAPI `Depends()` for DB session and auth
- Middleware chain: rate limiting → security headers → request ID → structured logging
- Global error handler returns standard JSON error format
- Soft delete for tasks (is_deleted flag, excluded from queries)

## Frontend Architecture (apps/web/)

### Layer Structure
```
Pages --> Components --> Hooks (React Query) --> API Client (Axios) --> Backend
  ^                       ^
  |                       |
React Router          AuthContext (React Context)
```

### Components: 22 frontend components
- **7 Pages**: Login, Register, Dashboard, TaskBoard, TaskList, TaskDetail, Team
- **7 UI Components**: TaskCard, TaskForm, KanbanBoard, FilterBar, CommentThread, StatCard, Layout
- **2 Infrastructure**: ProtectedRoute, App
- **5 Hook Sets**: useAuth, useTasks, useUsers, useComments, useDashboard
- **1 Service**: API Client (Axios + JWT interceptor)

### Key Patterns
- React Query for all server state (caching, invalidation, optimistic updates)
- React Context for auth state only (token, user, login/logout)
- Optimistic drag & drop on Kanban with rollback on API error
- Form validation with Zod schemas mirroring backend Pydantic schemas
- ProtectedRoute wrapper redirects to login if unauthenticated

## Cross-Layer Communication

### Auth Flow
1. Login: Frontend sends credentials → API returns JWT + refresh token
2. Storage: JWT stored in localStorage
3. Requests: Axios interceptor attaches `Authorization: Bearer <token>`
4. Expiry: 401 response → try refresh token → if fails, redirect to login

### Data Flow
1. User action triggers React Query hook (useQuery or useMutation)
2. Hook calls API Client (Axios) with JWT header
3. FastAPI Router receives request, validates via Pydantic schema
4. Router calls Service with validated data
5. Service executes business logic, accesses Models via async session
6. Response flows back through Pydantic response schema → JSON → React Query cache → UI re-render

## Detailed Artifacts
- Components: see [components.md](components.md)
- Methods: see [component-methods.md](component-methods.md)
- Services: see [services.md](services.md)
- Dependencies: see [component-dependency.md](component-dependency.md)
