## Deployment and Database Migration Runbook

This document describes recommended steps to deploy the backend and run database migrations safely.

1. Build and push the Docker image (CI should handle this automatically):

```bash
docker build -t myrepo/lm_emr:latest -f backend/Dockerfile .
docker push myrepo/lm_emr:latest
```

2. Run database migrations (using Alembic) as a separate step before switching traffic:

```bash
# Run from a machine with DB access and alembic configured
cd backend
alembic upgrade head
```

3. Health checks

- Use `/health` for basic liveness
- Use `/health/db` to confirm DB connectivity

4. Rollback plan

- If migrations are destructive, use a blue/green deploy or restore from DB backups.

5. Secrets

- Keep secrets (DB credentials, JWT_SECRET_KEY) in your secrets manager or CI environment (e.g., GitHub Secrets, Vault). Do not commit them to the repo; use `.env.example` as the template.
