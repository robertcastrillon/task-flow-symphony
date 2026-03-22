#!/usr/bin/env bash
# Setup GCP staging infrastructure for TaskFlow
# Run once to create the initial GCP resources.
#
# Prerequisites:
#   - gcloud CLI authenticated with project owner/editor permissions
#   - Billing enabled on the GCP project
#
# Usage:
#   export GCP_PROJECT_ID=your-project-id
#   ./infra/gcp/setup-staging.sh

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID environment variable}"
REGION="${GCP_REGION:-us-central1}"
DB_INSTANCE="taskflow-staging"
DB_NAME="taskflow"
DB_USER="taskflow"
REPO_NAME="taskflow"
API_SERVICE="taskflow-api-staging"
WEB_SERVICE="taskflow-web-staging"
MIGRATE_JOB="taskflow-migrate-staging"
SA_NAME="taskflow-deploy"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "==> Setting project to ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

echo "==> Enabling required APIs"
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com

echo "==> Creating Artifact Registry repository"
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="TaskFlow Docker images" \
  2>/dev/null || echo "Repository already exists"

echo "==> Creating Cloud SQL instance (PostgreSQL 16)"
gcloud sql instances create "${DB_INSTANCE}" \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region="${REGION}" \
  --storage-type=SSD \
  --storage-size=10GB \
  --availability-type=zonal \
  --no-assign-ip \
  --network=default \
  2>/dev/null || echo "SQL instance already exists"

echo "==> Creating database"
gcloud sql databases create "${DB_NAME}" \
  --instance="${DB_INSTANCE}" \
  2>/dev/null || echo "Database already exists"

echo "==> Setting database user password"
DB_PASSWORD=$(openssl rand -base64 24)
gcloud sql users set-password "${DB_USER}" \
  --instance="${DB_INSTANCE}" \
  --password="${DB_PASSWORD}" \
  2>/dev/null || gcloud sql users create "${DB_USER}" \
  --instance="${DB_INSTANCE}" \
  --password="${DB_PASSWORD}"

CLOUD_SQL_CONNECTION="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CLOUD_SQL_CONNECTION}"

echo "==> Creating secrets in Secret Manager"
echo -n "${DATABASE_URL}" | gcloud secrets create "taskflow-staging-db-url" \
  --data-file=- \
  2>/dev/null || echo -n "${DATABASE_URL}" | gcloud secrets versions add "taskflow-staging-db-url" \
  --data-file=-

JWT_SECRET=$(openssl rand -base64 48)
echo -n "${JWT_SECRET}" | gcloud secrets create "taskflow-staging-jwt-secret" \
  --data-file=- \
  2>/dev/null || echo -n "${JWT_SECRET}" | gcloud secrets versions add "taskflow-staging-jwt-secret" \
  --data-file=-

echo "==> Creating service account for deployment"
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="TaskFlow Deploy SA" \
  2>/dev/null || echo "Service account already exists"

echo "==> Granting roles to service account"
for role in \
  roles/run.admin \
  roles/artifactregistry.writer \
  roles/cloudsql.client \
  roles/secretmanager.secretAccessor \
  roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${role}" \
    --quiet
done

echo "==> Creating Cloud Run migration job"
gcloud run jobs create "${MIGRATE_JOB}" \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/api:latest" \
  --region="${REGION}" \
  --set-cloudsql-instances="${CLOUD_SQL_CONNECTION}" \
  --set-secrets="TASKFLOW_DATABASE_URL=taskflow-staging-db-url:latest" \
  --command="alembic" \
  --args="upgrade,head" \
  --max-retries=1 \
  --task-timeout=120s \
  2>/dev/null || echo "Migration job already exists — update with 'gcloud run jobs update'"

echo "==> Setting up Workload Identity Federation for GitHub Actions"
WIF_POOL="github-actions-pool"
WIF_PROVIDER="github-actions-provider"
GITHUB_REPO="${GITHUB_REPO:?Set GITHUB_REPO (e.g., org/repo)}"

gcloud iam workload-identity-pools create "${WIF_POOL}" \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  2>/dev/null || echo "WIF pool already exists"

POOL_ID=$(gcloud iam workload-identity-pools describe "${WIF_POOL}" \
  --location="global" \
  --format="value(name)")

gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER}" \
  --location="global" \
  --workload-identity-pool="${WIF_POOL}" \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  2>/dev/null || echo "WIF provider already exists"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_REPO}" \
  --quiet

PROVIDER_ID=$(gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER}" \
  --location="global" \
  --workload-identity-pool="${WIF_POOL}" \
  --format="value(name)")

echo ""
echo "========================================"
echo "  Staging setup complete!"
echo "========================================"
echo ""
echo "Add these GitHub repository secrets:"
echo "  GCP_PROJECT_ID          = ${PROJECT_ID}"
echo "  GCP_WORKLOAD_IDENTITY_PROVIDER = ${PROVIDER_ID}"
echo "  GCP_SERVICE_ACCOUNT     = ${SA_EMAIL}"
echo "  STAGING_API_URL         = (Cloud Run API URL, set after first deploy)"
echo "  STAGING_WEB_URL         = (Cloud Run Web URL, set after first deploy)"
echo ""
echo "Add this GitHub repository variable:"
echo "  GCP_REGION              = ${REGION}"
echo ""
echo "Database password (save securely): ${DB_PASSWORD}"
echo "JWT secret (save securely): ${JWT_SECRET}"
