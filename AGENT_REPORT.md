## Deploy Report — ENG-82: B—CD-03: Tests & validation

NEXT_STATE: Deployed to Staging

**Deployed at:** 2026-03-22 15:17 UTC
**Branch merged:** `eng-82` → `develop`
**PR:** #15 — Merged ✓

### Staging access

| Service | URL | Status |
|---------|-----|--------|
| API | http://localhost:8002 | ✅ Running |
| API health | http://localhost:8002/api/v1/health | ✅ `{"status":"healthy"}` |
| API docs | http://localhost:8002/api/v1/docs | ✅ Available |
| Web app | http://localhost:5176 | ⚠️ Port mismatch (see notes) |
| DB | localhost:5435 | ✅ Healthy |

### Credentials
- Register via `POST /api/v1/auth/register` with email/password
- Then login via `POST /api/v1/auth/login`

### Smoke test results
- Health endpoint: ✅ `{"status":"healthy","app_name":"TaskFlow API","version":"0.1.0"}`
- API docs (Swagger): ✅ Accessible at `/api/v1/docs`
- Tasks API: ✅ Returns 401 (auth required — correct behavior)
- Comments endpoints: ✅ Registered (`/api/v1/tasks/{task_id}/comments`)
- Dashboard endpoint: ✅ Registered (`/api/v1/dashboard/stats`)

### What to verify in staging
1. **US-C01**: GET `/api/v1/tasks/{task_id}/comments` returns comments ordered chronologically with author info
2. **US-C02**: POST `/api/v1/tasks/{task_id}/comments` creates comment; validates non-empty content; returns 404 for nonexistent task
3. **US-D01**: GET `/api/v1/dashboard/stats` returns correct task counts by status, overdue tasks, and per-user breakdown
4. Confirm all BDD scenarios from PR #15 pass (`pytest apps/api/tests/test_bdd_comments_dashboard.py`)

### Deployment notes
- Ports adjusted to avoid conflicts with ENG-78 (8000) and ENG-81 (8001): API on 8002, DB on 5435, Web on 5176
- **Known issue**: `docker-compose.yml` maps web container port 5173 but the Dockerfile serves on 8080. This is a pre-existing config issue not related to ENG-82. Fix: change web service ports to `"5176:8080"` or update Dockerfile.
- No new migrations were needed for this test-only ticket
- All 24 BDD tests pass (verified in CI and locally before merge)

### Test results (from QA phase)

| Level | Check | Result |
|-------|-------|--------|
| Lint (ruff) | All checks passed | ✅ |
| Security (bandit) | No findings | ✅ |
| Unit tests | 316 passed | ✅ |
| Coverage | 97.44% (threshold: 80%) | ✅ |
| BDD scenarios | 24 passed | ✅ |
