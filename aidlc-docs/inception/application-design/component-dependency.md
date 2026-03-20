# Component Dependencies — TaskFlow

## Backend Dependency Graph

```
+------------------+     +------------------+     +------------------+
|   Auth Router    |     |  Tasks Router    |     | Comments Router  |
|   Users Router   |     | Dashboard Router |     |                  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+--------+---------+     +--------+---------+     +--------+---------+
|  Auth Service    |     |  Task Service    |     | Comment Service  |
|  User Service    |     | Dashboard Svc    |     |                  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+--------+--------------------------------------------------------+
|                    SQLAlchemy Models                              |
|  User Model  |  Task Model  |  Comment Model                    |
+--------+--------------------------------------------------------+
         |
         v
+--------+---------+
|  Async DB Session |
|  (asyncpg + PG16) |
+-------------------+
```

### Dependency Matrix

| Component | Depends On |
|---|---|
| Auth Router | AuthService, Pydantic Auth Schemas, Dependencies (get_db) |
| Users Router | UserService, Pydantic User Schemas, Dependencies (get_db, get_current_user) |
| Tasks Router | TaskService, Pydantic Task Schemas, Dependencies (get_db, get_current_user) |
| Comments Router | CommentService, Pydantic Comment Schemas, Dependencies (get_db, get_current_user) |
| Dashboard Router | DashboardService, Pydantic Dashboard Schemas, Dependencies (get_db, get_current_user) |
| AuthService | User Model, Security Module |
| UserService | User Model |
| TaskService | Task Model, User Model |
| CommentService | Comment Model, Task Model |
| DashboardService | Task Model |
| Security Module | Config (JWT_SECRET, ALGORITHM) |
| Dependencies | Security Module, User Model, DB Session |
| Middleware | Config, structlog |
| Main App | All Routers, Middleware, Config, DB Session |

### Cross-Cutting Dependencies
- **Config** → used by Security, DB Session, Middleware, Main App
- **Dependencies (get_current_user)** → used by all routers except Auth (register/login)
- **DB Session** → used by all services via dependency injection
- **Middleware** → applied globally in Main App (rate limiting, security headers, logging)

---

## Frontend Dependency Graph

```
+-------------------+
|    App.tsx         |
| (Router, Providers)|
+--------+----------+
         |
         v
+--------+----------+     +-------------------+
|    Layout          |     |  ProtectedRoute   |
| (Sidebar, Header)  |     |                   |
+--------+----------+     +-------------------+
         |
         v
+--------+---------------------------------------------------+
|                        Pages                                |
| LoginPage | RegisterPage | DashboardPage | TaskBoardPage   |
| TaskListPage | TaskDetailPage | TeamPage                   |
+--------+---------------------------------------------------+
         |
         v
+--------+---------------------------------------------------+
|                     Components                              |
| TaskCard | TaskForm | KanbanBoard | FilterBar              |
| CommentThread | StatCard                                    |
+--------+---------------------------------------------------+
         |
         v
+--------+---------------------------------------------------+
|                Custom Hooks (React Query)                    |
| useAuth | useTasks | useUsers | useComments | useDashboard |
+--------+---------------------------------------------------+
         |
         v
+--------+----------+
|   API Client       |
| (Axios + JWT)      |
+--------+----------+
         |
         v
+--------+----------+
|  FastAPI Backend   |
+--------------------+
```

### Frontend Dependency Matrix

| Component | Depends On |
|---|---|
| App.tsx | React Router, AuthContext, QueryClientProvider |
| LoginPage | useAuth, Zod, React Hook Form |
| RegisterPage | useAuth, Zod, React Hook Form |
| DashboardPage | useDashboardStats, StatCard |
| TaskBoardPage | useTaskList, useChangeStatus, KanbanBoard, TaskCard |
| TaskListPage | useTaskList, FilterBar, TaskCard |
| TaskDetailPage | useTask, useUpdateTask, useComments, TaskForm, CommentThread |
| TeamPage | useUsers |
| KanbanBoard | dnd-kit, TaskCard |
| TaskForm | Zod, React Hook Form, useUsers (for assignee select) |
| CommentThread | useComments, useCreateComment |
| FilterBar | useUsers (for assignee filter options) |
| All Hooks | API Client (Axios instance) |
| API Client | AuthContext (for JWT token) |

---

## Data Flow

```
User Action (Frontend)
    |
    v
React Component --> React Hook (useMutation/useQuery)
    |
    v
API Client (Axios + JWT header)
    |
    v [HTTP Request]
FastAPI Router --> Pydantic Validation
    |
    v
Service Layer (Business Logic)
    |
    v
SQLAlchemy Model --> PostgreSQL
    |
    v [Response]
Pydantic Response Schema --> JSON
    |
    v [HTTP Response]
React Query Cache --> Component Re-render
```
