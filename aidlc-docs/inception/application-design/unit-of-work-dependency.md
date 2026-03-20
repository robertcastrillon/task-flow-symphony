# Unit of Work Dependencies — TaskFlow

## Dependency Matrix

| Unit | Depends On | Dependency Type |
|---|---|---|
| Unit 1: Setup & Infra | — | None (first) |
| Unit 2: Auth | Unit 1 | Project structure, DB, base app |
| Unit 3: Tasks & Users | Unit 2 | Auth system, User model, JWT dependencies |
| Unit 4: Comments & Dashboard | Unit 3 | Task model, User model |
| Unit 5: Frontend | Units 2, 3, 4 | All API endpoints |
| Unit 6: GCP Deploy | Units 1-5 | Full working application |

## Dependency Graph

```
Unit 1: Setup & Infra
    |
    v
Unit 2: Auth
    |
    v
Unit 3: Tasks & Users
    |
    v
Unit 4: Comments & Dashboard
    |
    v
Unit 5: Frontend
    |
    v
Unit 6: GCP Deploy
```

## Shared Resources Between Units

| Resource | Created In | Used By |
|---|---|---|
| PostgreSQL (Docker) | Unit 1 | Units 2, 3, 4 |
| Base FastAPI app (main.py) | Unit 1 | Units 2, 3, 4 (add routers) |
| DB Session (session.py) | Unit 1 | Units 2, 3, 4 |
| Config (config.py) | Unit 1 | Units 2, 3, 4 |
| User Model | Unit 2 | Units 3, 4 (foreign keys) |
| Security Module | Unit 2 | Units 3, 4 (auth dependencies) |
| Auth Dependencies (get_current_user) | Unit 2 | Units 3, 4 (protect endpoints) |
| Middleware (rate limit, headers, logging) | Unit 2 | Units 3, 4 (applied globally) |
| Task Model | Unit 3 | Unit 4 (comments FK, dashboard queries) |
| All API Endpoints | Units 2-4 | Unit 5 (API client) |
| Dockerfiles | Unit 1 (base) | Unit 6 (production optimized) |
| CI workflow | Unit 1 | Unit 6 (adds deploy step) |

## Integration Points

### Unit 2 → Unit 3
- Unit 3 reuses `get_current_user` dependency from Unit 2
- Unit 3 references User model FK in Task.created_by and Task.assigned_to
- Unit 3 adds new routers to existing main.py

### Unit 3 → Unit 4
- Unit 4 references Task model FK in Comment.task_id
- Unit 4 queries Task model for dashboard aggregation
- Unit 4 adds new routers to existing main.py

### Units 2-4 → Unit 5
- Frontend API client calls all endpoints from Units 2-4
- Frontend auth flow depends on Unit 2 token endpoints
- Frontend Kanban depends on Unit 3 task status endpoints
- Frontend comments depend on Unit 4 comment endpoints

### Units 1-5 → Unit 6
- Unit 6 creates production Dockerfiles based on Unit 1 base
- Unit 6 configures Cloud Run for API and Web containers
- Unit 6 configures Cloud SQL connection for production
