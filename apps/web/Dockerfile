# ── Base stage ──────────────────────────────────────────────
FROM node:20-slim AS base

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# ── Development stage ──────────────────────────────────────
FROM base AS development

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# ── Build stage ────────────────────────────────────────────
FROM base AS build

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# ── Production stage ───────────────────────────────────────
FROM node:20-slim AS production

WORKDIR /app

RUN npm install -g serve

COPY --from=build /app/dist ./dist

EXPOSE 8080
CMD ["serve", "-s", "dist", "-l", "8080"]
