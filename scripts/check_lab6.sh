#!/usr/bin/env sh
set -eu

printf '%s\n' '== compose status =='
docker compose ps

printf '%s\n' '== gateway health =='
curl -fsS http://127.0.0.1:${GATEWAY_PORT:-8000}/health
printf '\n'

printf '%s\n' '== storage health =='
curl -fsS http://127.0.0.1:${STORAGE_PORT:-8001}/health
printf '\n'

printf '%s\n' '== container users =='
docker compose exec -T api-gateway whoami
docker compose exec -T storage-service whoami

printf '%s\n' '== application image sizes =='
docker images python-lab6-gateway python-lab6-storage
