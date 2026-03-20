# Services — TaskFlow

## Backend Service Layer

### Service Architecture Pattern
- **Pattern**: Service Layer (Domain Services)
- **Orchestration**: Routers are thin — they validate input via Pydantic schemas, call services, return responses
- **Services**: Contain all business logic, receive DB session via dependency injection
- **Models**: SQLAlchemy ORM models accessed only through services (never directly in routers)

### Service Definitions

#### AuthService
- **Responsibility**: User registration, authentication, token lifecycle
- **Dependencies**: User Model, Security Module
- **Orchestration**:
  - `register_user`: Validate email uniqueness → hash password → create User → return User
  - `authenticate`: Find user by email → verify password → generate JWT + refresh token
  - `refresh_token`: Decode refresh token → validate expiry → generate new token pair
  - `get_current_user`: Decode JWT → find user by ID → validate is_active

#### UserService
- **Responsibility**: User profile management, team listing
- **Dependencies**: User Model
- **Orchestration**:
  - `list_users`: Query active users → return list
  - `get_user`: Find by ID → raise 404 if not found
  - `update_user`: Validate permissions (own profile or admin) → update fields

#### TaskService
- **Responsibility**: Task CRUD, status management, assignment, filtering
- **Dependencies**: Task Model, User Model
- **Orchestration**:
  - `list_tasks`: Build query from filters → apply pagination → execute
  - `create_task`: Set created_by → set defaults (status=todo, priority=medium) → save
  - `update_task`: Find task → validate ownership/admin → update fields
  - `delete_task`: Find task → validate ownership/admin → set soft delete flag
  - `change_status`: Find task → update status → set completed_at if "done"
  - `assign_task`: Find task → validate assignee exists → validate permissions (admin or self-assign) → update assigned_to

#### CommentService
- **Responsibility**: Comment CRUD on tasks
- **Dependencies**: Comment Model, Task Model
- **Orchestration**:
  - `list_comments`: Validate task exists → query comments ordered by created_at
  - `create_comment`: Validate task exists → create comment with author_id

#### DashboardService
- **Responsibility**: Aggregate statistics
- **Dependencies**: Task Model
- **Orchestration**:
  - `get_stats`: Count by status → count by assignee → count overdue (due_date < now AND status != done) → return aggregate

---

## Frontend Service Layer

### API Client Service
- **Responsibility**: HTTP client configured with base URL and JWT interceptor
- **Pattern**: Axios instance with request interceptor that attaches Authorization header
- **Error handling**: Response interceptor catches 401 → triggers token refresh or logout

### React Query Integration
- **Pattern**: Custom hooks wrapping `useQuery` / `useMutation`
- **Cache strategy**:
  - Task list: stale time 30s, refetch on window focus
  - Single task: stale time 60s
  - Dashboard stats: stale time 60s
  - User list: stale time 5min (rarely changes)
- **Optimistic updates**: Kanban drag & drop uses optimistic mutation with rollback on error
- **Invalidation**: Mutations invalidate related query keys (e.g., create task → invalidate task list + dashboard stats)

### Auth Context (React Context)
- **Responsibility**: Manage auth state across the app
- **State**: `{ user: User | null, token: string | null, isAuthenticated: boolean, isLoading: boolean }`
- **Methods**: `login(email, password)`, `register(data)`, `logout()`, `refreshToken()`
- **Persistence**: JWT stored in localStorage, loaded on app init
- **Guard**: ProtectedRoute component checks `isAuthenticated` before rendering children
