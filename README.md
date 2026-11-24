# Python Lab 6: Docker + Compose + CI

Lab 6 is based on the Lab 5 microservice application.

Architecture:

```text
client -> api-gateway:8000 -> storage-service:8001 -> PostgreSQL (db:5432)
```

## 1. Prepare environment

Create the real `.env` from the committed template:

```bash
cp .env.example .env
```

For a local lab run, replace `POSTGRES_PASSWORD=change-me` in `.env` with any local password you choose. The real `.env` is ignored by git.

## 2. Start all containers

```bash
docker compose up --build
```

The command starts PostgreSQL, storage-service, and api-gateway. Compose waits for healthchecks in dependency order.

Swagger:

```text
http://127.0.0.1:8000/docs
```

Storage Swagger (exposed for demonstration):

```text
http://127.0.0.1:8001/docs
```

## 3. Verify health

```bash
docker compose ps
```

The services should become `healthy`.

Direct checks:

```bash
curl -f http://127.0.0.1:8000/health
curl -f http://127.0.0.1:8001/health
```

Expected JSON:

```json
{"status":"ok"}
```

## 4. End-to-end request

Create an item through api-gateway:

```bash
curl -X POST http://127.0.0.1:8000/items \
  -H 'Content-Type: application/json' \
  -d '{"name":"CPU","price":199,"quantity":3}'
```

Read it back (use the returned id):

```bash
curl http://127.0.0.1:8000/items/1
```

The request path is gateway -> storage-service -> PostgreSQL and back.

## 5. Persistence through a named volume

Create an item, then recreate the containers:

```bash
docker compose down
docker compose up -d
```

The item remains because PostgreSQL data is stored in the named volume `pgdata`.

To remove the data intentionally:

```bash
docker compose down -v
```

## 6. Verify non-root users

```bash
docker compose exec api-gateway whoami
docker compose exec storage-service whoami
```

Both commands should print:

```text
app
```

## 7. Check image sizes

```bash
docker images python-lab6-gateway python-lab6-storage
```

The lab target is less than 200 MB for each final application image.

## 8. Local quality checks

Create a clean virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run checks:

```bash
ruff check .
(cd api_gateway && mypy app tests)
(cd storage_service && mypy app tests)
(cd api_gateway && pytest -q)
(cd storage_service && pytest -q)
```

## 9. CI

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

On push/pull request it creates a clean venv and runs, in order:

1. `ruff check .`
2. `mypy` for both services
3. `pytest` for both services
4. `docker build .` for api-gateway
5. Docker build for storage-service

Any failed command fails the job.

## 10. Docker files

- Root `Dockerfile`: multi-stage image for api-gateway.
- `storage_service/Dockerfile`: multi-stage image for storage-service.
- `.dockerignore`: excludes git data, local venv, caches, tests, and `.env` from the root build context.
- `storage_service/.dockerignore`: same protection for the storage build context.
- Both runtime images create and use the unprivileged user `app`.

## 11. Stop

```bash
docker compose down
```

CI check: application is ready.
