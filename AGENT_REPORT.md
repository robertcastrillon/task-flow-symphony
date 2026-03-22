## Deploy Report — ENG-70: PSI-03: Tests & validation

**Deployed at:** 2026-03-21 22:45 UTC
**Branch merged:** `eng-70` → `develop`
**PR:** [#5](https://github.com/robertcastrillon/task-flow-symphony/pull/5) — Merged

### Staging access

| Service | URL | Status |
|---------|-----|--------|
| API | http://localhost:8000 | OK (local) |
| API docs | http://localhost:8000/api/v1/docs | OK (200) |
| Web app | http://localhost:5173 | Not deployed (Docker Compose plugin unavailable) |

### Credentials
- Email: test@example.com
- Password: password123

### Smoke test results
- Health endpoint (`/api/v1/health`): OK — `{"status":"healthy","app_name":"TaskFlow API","version":"0.1.0"}`
- API docs (`/api/v1/docs`): OK (200)
- Root health (`/health`): 404 (expected — health lives under `/api/v1/health`)

### What to verify in staging
1. Health endpoint returns `{"status": "healthy", "app_name": "TaskFlow API", "version": "0.1.0"}`
2. API docs page loads at `/api/v1/docs`
3. Version is correctly read from `Settings.version` config field
4. `.gitignore` properly excludes `apps/web/coverage/` directory

### Deployment notes
- Docker Compose plugin (`docker compose`) is not available on this machine — only standalone `docker` CLI is installed. The API was tested locally using `uvicorn` directly with a SQLite backend.
- No database migrations were required for these changes (config/response format only).
- The PR merged cleanly with no conflicts against `develop`.
- Changes are minimal: health endpoint alignment (`"ok"` → `"healthy"`), centralized version in Settings, and `.gitignore` cleanup.
