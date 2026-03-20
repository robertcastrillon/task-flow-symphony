# Components — TaskFlow

## Backend Components (apps/api/)

### COMP-B01: Auth Router
- **Path**: `app/routers/auth.py`
- **Responsibility**: Handle authentication endpoints (register, login, refresh, me)
- **Interface**: REST endpoints under `/api/v1/auth/`

### COMP-B02: Users Router
- **Path**: `app/routers/users.py`
- **Responsibility**: Handle user management endpoints (list, detail, update)
- **Interface**: REST endpoints under `/api/v1/users/`

### COMP-B03: Tasks Router
- **Path**: `app/routers/tasks.py`
- **Responsibility**: Handle task CRUD, status change, assignment endpoints
- **Interface**: REST endpoints under `/api/v1/tasks/`

### COMP-B04: Comments Router
- **Path**: `app/routers/comments.py`
- **Responsibility**: Handle comment listing and creation on tasks
- **Interface**: REST endpoints under `/api/v1/tasks/{id}/comments`

### COMP-B05: Dashboard Router
- **Path**: `app/routers/dashboard.py`
- **Responsibility**: Handle dashboard statistics endpoint
- **Interface**: REST endpoint `/api/v1/dashboard/stats`

### COMP-B06: Auth Service
- **Path**: `app/services/auth_service.py`
- **Responsibility**: Business logic for registration, login, token management, password hashing

### COMP-B07: User Service
- **Path**: `app/services/user_service.py`
- **Responsibility**: Business logic for user CRUD, profile updates, role management

### COMP-B08: Task Service
- **Path**: `app/services/task_service.py`
- **Responsibility**: Business logic for task CRUD, filtering, status transitions, assignment, soft delete

### COMP-B09: Comment Service
- **Path**: `app/services/comment_service.py`
- **Responsibility**: Business logic for comment creation and retrieval

### COMP-B10: Dashboard Service
- **Path**: `app/services/dashboard_service.py`
- **Responsibility**: Aggregate task statistics (by status, by user, overdue)

### COMP-B11: User Model
- **Path**: `app/models/user.py`
- **Responsibility**: SQLAlchemy ORM model for User entity

### COMP-B12: Task Model
- **Path**: `app/models/task.py`
- **Responsibility**: SQLAlchemy ORM model for Task entity

### COMP-B13: Comment Model
- **Path**: `app/models/comment.py`
- **Responsibility**: SQLAlchemy ORM model for Comment entity

### COMP-B14: Auth Schemas
- **Path**: `app/schemas/auth.py`
- **Responsibility**: Pydantic schemas for register, login requests/responses, token payloads

### COMP-B15: User Schemas
- **Path**: `app/schemas/user.py`
- **Responsibility**: Pydantic schemas for user request/response

### COMP-B16: Task Schemas
- **Path**: `app/schemas/task.py`
- **Responsibility**: Pydantic schemas for task CRUD, filters, status change, assignment

### COMP-B17: Comment Schemas
- **Path**: `app/schemas/comment.py`
- **Responsibility**: Pydantic schemas for comment request/response

### COMP-B18: Dashboard Schemas
- **Path**: `app/schemas/dashboard.py`
- **Responsibility**: Pydantic schemas for dashboard stats response

### COMP-B19: Security Module
- **Path**: `app/core/security.py`
- **Responsibility**: JWT creation/validation, password hashing (bcrypt/argon2), token refresh

### COMP-B20: Config Module
- **Path**: `app/core/config.py`
- **Responsibility**: Application settings via pydantic-settings (env vars, DB URL, JWT secret, CORS origins)

### COMP-B21: Dependencies Module
- **Path**: `app/core/deps.py`
- **Responsibility**: FastAPI dependency injection (get_db session, get_current_user, require_admin)

### COMP-B22: Database Module
- **Path**: `app/db/session.py`
- **Responsibility**: Async SQLAlchemy engine, session factory, Base declarative class

### COMP-B23: Middleware Module
- **Path**: `app/core/middleware.py`
- **Responsibility**: Rate limiting, security headers, request ID correlation, structured logging middleware

### COMP-B24: Main Application
- **Path**: `app/main.py`
- **Responsibility**: FastAPI app factory, router registration, middleware setup, CORS config, global error handler

---

## Frontend Components (apps/web/)

### COMP-F01: App Entry
- **Path**: `src/App.tsx`
- **Responsibility**: App root, React Router setup, AuthProvider, QueryClientProvider

### COMP-F02: LoginPage
- **Path**: `src/pages/LoginPage.tsx`
- **Responsibility**: Login form with email/password, JWT storage

### COMP-F03: RegisterPage
- **Path**: `src/pages/RegisterPage.tsx`
- **Responsibility**: Registration form with validation

### COMP-F04: DashboardPage
- **Path**: `src/pages/DashboardPage.tsx`
- **Responsibility**: Dashboard with StatCards, overdue tasks, activity summary

### COMP-F05: TaskBoardPage
- **Path**: `src/pages/TaskBoardPage.tsx`
- **Responsibility**: Kanban board view with KanbanBoard component

### COMP-F06: TaskListPage
- **Path**: `src/pages/TaskListPage.tsx`
- **Responsibility**: Table view with FilterBar, search, sorting

### COMP-F07: TaskDetailPage
- **Path**: `src/pages/TaskDetailPage.tsx`
- **Responsibility**: Task detail modal/page with CommentThread

### COMP-F08: TeamPage
- **Path**: `src/pages/TeamPage.tsx`
- **Responsibility**: Team member list with role badges

### COMP-F09: TaskCard
- **Path**: `src/components/TaskCard.tsx`
- **Responsibility**: Card in Kanban showing title, priority color, assignee avatar, due date

### COMP-F10: TaskForm
- **Path**: `src/components/TaskForm.tsx`
- **Responsibility**: Create/edit task form with Zod validation + React Hook Form

### COMP-F11: KanbanBoard
- **Path**: `src/components/KanbanBoard.tsx`
- **Responsibility**: Three-column board with dnd-kit drag & drop

### COMP-F12: FilterBar
- **Path**: `src/components/FilterBar.tsx`
- **Responsibility**: Filter controls for status, priority, assignee, tags

### COMP-F13: CommentThread
- **Path**: `src/components/CommentThread.tsx`
- **Responsibility**: Comment list + reply form

### COMP-F14: StatCard
- **Path**: `src/components/StatCard.tsx`
- **Responsibility**: Dashboard metric card (count + label)

### COMP-F15: ProtectedRoute
- **Path**: `src/components/ProtectedRoute.tsx`
- **Responsibility**: Route guard that redirects to login if unauthenticated

### COMP-F16: Layout
- **Path**: `src/components/Layout.tsx`
- **Responsibility**: App shell with navigation sidebar, header, content area

### COMP-F17: AuthContext
- **Path**: `src/hooks/useAuth.tsx`
- **Responsibility**: React Context for auth state (user, token, login, logout, isAuthenticated)

### COMP-F18: API Client
- **Path**: `src/services/api.ts`
- **Responsibility**: Axios/fetch instance with JWT interceptor, base URL config

### COMP-F19: Task Hooks
- **Path**: `src/hooks/useTasks.ts`
- **Responsibility**: React Query hooks for tasks (useTaskList, useTask, useCreateTask, useUpdateTask, etc.)

### COMP-F20: User Hooks
- **Path**: `src/hooks/useUsers.ts`
- **Responsibility**: React Query hooks for users (useUsers, useUser, useUpdateProfile)

### COMP-F21: Comment Hooks
- **Path**: `src/hooks/useComments.ts`
- **Responsibility**: React Query hooks for comments (useComments, useCreateComment)

### COMP-F22: Dashboard Hooks
- **Path**: `src/hooks/useDashboard.ts`
- **Responsibility**: React Query hook for dashboard stats (useDashboardStats)
