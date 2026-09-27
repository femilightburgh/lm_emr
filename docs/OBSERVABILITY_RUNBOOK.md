# Observability Runbook

This runbook describes how to observe, debug, and respond to production issues for LIGHTBURGH EMR.

1. Metrics
- The application exposes Prometheus metrics at `/metrics` on the API host.
- Key metrics to monitor:
  - `process_cpu_seconds_total` (host-level)
  - `python_gc_objects_collected_total` (Python GC)
  - HTTP request metrics (implement as needed)

2. Logging
- Application logs are structured text and configured via `app.core.logging`.
- Ensure logs are shipped to a centralized system (ELK/CloudWatch) in production.

3. Health checks
- `GET /health` — general app health
- `GET /health/db` — database connectivity

4. Alerting
- Examples:
  - High error rate (>5% 5m)
  - DB unreachable for 2 minutes
  - CPU or memory spike above expected baseline

5. Incident Response
- Step 1: Check `/health` and `/health/db`.
- Step 2: Inspect recent logs for exceptions and stack traces.
- Step 3: Check Prometheus dashboards for spikes in latency or errors.
- Step 4: Roll forward/rollback deploy depending on root cause.

6. Runbook for CORS issues in dev
- The dev Vite server proxies `/api` to backend to avoid CORS (`frontend/vite.config.ts`).
- Ensure `ALLOWED_ORIGINS` includes dev hosts, or use the dev proxy.

7. Postmortem checklist
- Timeline, root cause, contributing factors, mitigations, follow-ups.

For extension: add dashboards, more application metrics (request latency, errors, DB pool usage), and log correlation IDs.
