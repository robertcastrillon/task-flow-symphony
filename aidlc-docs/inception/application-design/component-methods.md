# Component Methods — TaskFlow

> Note: Detailed business rules will be defined in Functional Design (CONSTRUCTION phase).

---

## Backend Routers

### Auth Router (COMP-B01)
| Method | Signature | Purpose |
|---|---|---|
| `register` | `POST /api/v1/auth/register` → `UserResponse` | Create new user account |
| `login` | `POST /api/v1/auth/login` → `TokenResponse` | Authenticate and return JWT + refresh token |
| `refresh` | `POST /api/v1/auth/refresh` → `TokenResponse` | Refresh expired JWT |
| `me` | `GET /api/v1/auth/me` → `UserResponse` | Return current authenticated user |

### Users Router (COMP-B02)
| Method | Signature | Purpose |
|---|---|---|
| `list_users` | `GET /api/v1/users` → `list[UserResponse]` | List active team members |
| `get_user` | `GET /api/v1/users/{id}` → `UserResponse` | Get user detail |
| `update_user` | `PATCH /api/v1/users/{id}` → `UserResponse` | Update user profile |

### Tasks Router (COMP-B03)
| Method | Signature | Purpose |
|---|---|---|
| `list_tasks` | `GET /api/v1/tasks?status&assignee&priority&tag&page` → `PaginatedResponse[TaskResponse]` | List tasks with filters and pagination |
| `create_task` | `POST /api/v1/tasks` → `TaskResponse` | Create new task |
| `get_task` | `GET /api/v1/tasks/{id}` → `TaskResponse` | Get task detail |
| `update_task` | `PATCH /api/v1/tasks/{id}` → `TaskResponse` | Update task fields |
| `delete_task` | `DELETE /api/v1/tasks/{id}` → `204` | Soft delete task |
| `change_status` | `PATCH /api/v1/tasks/{id}/status` → `TaskResponse` | Change task status |
| `assign_task` | `PATCH /api/v1/tasks/{id}/assign` → `TaskResponse` | Assign/reassign task |

### Comments Router (COMP-B04)
| Method | Signature | Purpose |
|---|---|---|
| `list_comments` | `GET /api/v1/tasks/{id}/comments` → `list[CommentResponse]` | List comments on a task |
| `create_comment` | `POST /api/v1/tasks/{id}/comments` → `CommentResponse` | Add comment to task |

### Dashboard Router (COMP-B05)
| Method | Signature | Purpose |
|---|---|---|
| `get_stats` | `GET /api/v1/dashboard/stats` → `DashboardStatsResponse` | Get aggregated task statistics |

---

## Backend Services

### Auth Service (COMP-B06)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `register_user` | `RegisterRequest` | `User` | Create user, hash password |
| `authenticate` | `LoginRequest` | `TokenPair` | Validate credentials, generate tokens |
| `refresh_token` | `str (refresh_token)` | `TokenPair` | Validate refresh, generate new tokens |
| `get_current_user` | `str (jwt_token)` | `User` | Decode JWT, return user |

### User Service (COMP-B07)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `list_users` | `—` | `list[User]` | Return active users |
| `get_user` | `UUID` | `User` | Return user by ID |
| `update_user` | `UUID, UserUpdateRequest` | `User` | Update user fields |

### Task Service (COMP-B08)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `list_tasks` | `TaskFilterParams` | `PaginatedResult[Task]` | Filter, paginate, sort tasks |
| `create_task` | `TaskCreateRequest, User` | `Task` | Create task with creator |
| `get_task` | `UUID` | `Task` | Return task by ID |
| `update_task` | `UUID, TaskUpdateRequest, User` | `Task` | Update task fields |
| `delete_task` | `UUID, User` | `None` | Soft delete (check permissions) |
| `change_status` | `UUID, StatusChangeRequest` | `Task` | Update status, set completed_at |
| `assign_task` | `UUID, AssignRequest, User` | `Task` | Assign/reassign (check permissions) |

### Comment Service (COMP-B09)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `list_comments` | `UUID (task_id)` | `list[Comment]` | List comments for a task |
| `create_comment` | `UUID (task_id), CommentCreateRequest, User` | `Comment` | Create comment on task |

### Dashboard Service (COMP-B10)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `get_stats` | `—` | `DashboardStats` | Aggregate stats: by status, by user, overdue count |

---

## Backend Core

### Security Module (COMP-B19)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `hash_password` | `str` | `str` | Hash password with bcrypt/argon2 |
| `verify_password` | `str, str` | `bool` | Verify plaintext against hash |
| `create_access_token` | `dict (payload)` | `str` | Generate JWT (24h expiry) |
| `create_refresh_token` | `dict (payload)` | `str` | Generate refresh token |
| `decode_token` | `str` | `dict` | Decode and validate JWT |

### Dependencies Module (COMP-B21)
| Method | Input | Output | Purpose |
|---|---|---|---|
| `get_db` | `—` | `AsyncSession` | Yield async DB session |
| `get_current_user` | `token (header)` | `User` | Extract and validate user from JWT |
| `require_admin` | `User` | `User` | Verify user has admin role |

---

## Frontend Hooks

### Auth Hook (COMP-F17)
| Hook/Method | Input | Output | Purpose |
|---|---|---|---|
| `useAuth` | `—` | `AuthContext` | Access auth state and methods |
| `login` | `email, password` | `void` | Authenticate and store token |
| `logout` | `—` | `void` | Clear token and redirect |
| `register` | `RegisterData` | `void` | Register new account |

### Task Hooks (COMP-F19)
| Hook | Input | Output | Purpose |
|---|---|---|---|
| `useTaskList` | `filters` | `UseQueryResult<Task[]>` | Fetch filtered task list |
| `useTask` | `id` | `UseQueryResult<Task>` | Fetch single task |
| `useCreateTask` | `—` | `UseMutationResult` | Create task mutation |
| `useUpdateTask` | `—` | `UseMutationResult` | Update task mutation |
| `useDeleteTask` | `—` | `UseMutationResult` | Delete task mutation |
| `useChangeStatus` | `—` | `UseMutationResult` | Change status mutation |
| `useAssignTask` | `—` | `UseMutationResult` | Assign task mutation |

### User Hooks (COMP-F20)
| Hook | Input | Output | Purpose |
|---|---|---|---|
| `useUsers` | `—` | `UseQueryResult<User[]>` | Fetch team members |
| `useUser` | `id` | `UseQueryResult<User>` | Fetch single user |
| `useUpdateProfile` | `—` | `UseMutationResult` | Update own profile |

### Comment Hooks (COMP-F21)
| Hook | Input | Output | Purpose |
|---|---|---|---|
| `useComments` | `taskId` | `UseQueryResult<Comment[]>` | Fetch comments for task |
| `useCreateComment` | `—` | `UseMutationResult` | Create comment mutation |

### Dashboard Hooks (COMP-F22)
| Hook | Input | Output | Purpose |
|---|---|---|---|
| `useDashboardStats` | `—` | `UseQueryResult<DashboardStats>` | Fetch dashboard statistics |
