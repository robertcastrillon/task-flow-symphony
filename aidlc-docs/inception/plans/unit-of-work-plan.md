# Unit of Work Plan — TaskFlow

## Decomposition Strategy
TaskFlow is a monorepo with two main applications (API + Web) sharing a database. Each application is a logical unit of work with clear boundaries. A third unit covers shared infrastructure (Docker, CI/CD, project setup).

## Proposed Units

### Unit 1: Project Setup & Infrastructure
- Monorepo scaffolding, Docker Compose, Makefile, CI/CD, database setup
- Must be completed first — all other units depend on it

### Unit 2: Backend API
- FastAPI application with all routers, services, models, schemas, core modules
- All 15+ REST endpoints, auth, middleware, migrations
- Tests with pytest + pytest-asyncio

### Unit 3: Frontend Web
- React application with all pages, components, hooks, API client
- Depends on Unit 2 (API must exist for frontend to connect)

## Execution Checklist

### Phase A: Unit Definitions
- [x] A1: Define Unit 1 (Project Setup & Infrastructure) — scope, stories, components
- [x] A2: Define Units 2-4 (Backend API sub-units: Auth, Tasks&Users, Comments&Dashboard)
- [x] A3: Define Unit 5 (Frontend Web) — scope, stories, components
- [x] A4: Define Unit 6 (Integration & GCP Deployment) — scope, components

### Phase B: Dependencies & Story Mapping
- [x] B1: Generate unit-of-work-dependency.md
- [x] B2: Generate unit-of-work-story-map.md
- [x] B3: Document code organization strategy (greenfield)

### Phase C: Validation
- [x] C1: Validate all 21 stories are assigned to units
- [x] C2: Validate unit boundaries and dependencies are correct
- [x] C3: Generate unit-of-work.md (consolidated)

---

## Clarification Questions

## Question 1
For the construction phase, should each unit go through the full per-unit loop (Functional Design → NFR Requirements → NFR Design → Infrastructure Design → Code Generation), or should we streamline?

A) Full loop for all 3 units — each gets its own design stages
B) Streamlined — Unit 1 (Setup) goes straight to Code Generation; Units 2 and 3 get full treatment
C) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 2
Should the backend API unit be further subdivided into sub-units (e.g., Auth module first, then Tasks module, then Comments/Dashboard)?

A) No — keep backend as a single unit, implement all together
B) Yes — subdivide into sub-units for incremental implementation (Auth → Tasks → Comments → Dashboard)
C) Other (please describe after [Answer]: tag below)

[Answer]:B
