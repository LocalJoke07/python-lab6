# Architecture

```text
Browser / Swagger
       |
       | HTTP :8000
       v
+------------------+
|   api-gateway    |
| FastAPI + httpx  |
+------------------+
       |
       | HTTP http://storage-service:8001
       v
+------------------+
| storage-service  |
| FastAPI + domain |
+------------------+
       |
       | PostgreSQL URL, host=db
       v
+------------------+
| PostgreSQL 16    |
| service name: db |
+------------------+
       |
       v
  volume: pgdata
```

## Boundaries

- `api-gateway` is the external entry point.
- `storage-service` owns item persistence and is the only application service that talks to PostgreSQL.
- PostgreSQL runs in a separate `db` container.
- Containers use Compose DNS names (`storage-service`, `db`) instead of `localhost`.
- `pgdata` stores database data outside the lifecycle of the database container.

## Readiness order

1. PostgreSQL starts and passes `pg_isready`.
2. `storage-service` starts, connects to `db`, and `/health` checks the database with `SELECT 1`.
3. `api-gateway` starts after storage is healthy; its `/health` checks storage.
