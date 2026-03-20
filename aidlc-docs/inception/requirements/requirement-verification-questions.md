# Requirements Verification Questions — TaskFlow

Please answer the following questions to clarify requirements before proceeding. Fill in the letter choice after each `[Answer]:` tag.

---

## Question 1
Which phase should we build in this iteration?

A) Phase 1 only — Core (Tasks, Users, Auth, Dashboard, Frontend)
B) Phase 1 + Phase 2 — Core + Telegram Bot
C) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 2
What deployment target do you plan for this project?

A) Local development only (Docker Compose)
B) Local development + cloud staging (AWS, GCP, Azure — specify which)
C) Local development + self-hosted VPS
D) Other (please describe after [Answer]: tag below)

[Answer]:B

## Question 3
What authentication approach do you prefer?

A) Simple JWT with email/password (as described in PRD)
B) JWT with email/password + OAuth social login (Google, GitHub)
C) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 4
For the frontend, do you have a preference on UI component library?

A) TailwindCSS only — custom components (no library)
B) TailwindCSS + shadcn/ui (headless components)
C) TailwindCSS + DaisyUI
D) Other (please describe after [Answer]: tag below)

[Answer]:C

## Question 5
How should the frontend validation library work?

A) Zod for schema validation + React Hook Form for form management
B) Zod only (manual form handling)
C) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 6
For the backend test runner, do you prefer:

A) pytest with pytest-asyncio (standard for FastAPI)
B) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 7
What package manager do you want for the Python backend?

A) uv (fast, modern)
B) pip + pip-tools
C) poetry
D) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 8
What package manager do you want for the frontend?

A) npm
B) pnpm
C) yarn
D) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 9
Should the project use a monorepo management tool?

A) No — simple directory structure with independent package.json / pyproject.toml per app
B) Turborepo (for frontend build orchestration)
C) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 10
What is the primary language for the UI/UX (labels, messages, placeholders)?

A) Spanish (es)
B) English (en)
C) Both — internationalization support (i18n)
D) Other (please describe after [Answer]: tag below)

[Answer]:A

## Question 11: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)
B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)
C) Other (please describe after [Answer]: tag below)

[Answer]:A
