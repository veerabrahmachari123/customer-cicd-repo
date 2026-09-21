#!/usr/bin/env bash
set -euo pipefail
: "${APP_CONTAINER:?}"
: "${DB_CONTAINER:?}"
: "${NETWORK:?}"
: "${HOST_PORT:?}"
: "${EXPECTED_VERSION:?}"
: "${EXPECTED_ENVIRONMENT:?}"

test "$(docker inspect -f '{{.State.Running}}' "$APP_CONTAINER")" = "true"
test "$(docker inspect -f '{{.State.Running}}' "$DB_CONTAINER")" = "true"
docker network inspect "$NETWORK" | grep -q "\"Name\": \"$APP_CONTAINER\""
docker network inspect "$NETWORK" | grep -q "\"Name\": \"$DB_CONTAINER\""
curl --fail --silent --show-error "http://localhost:${HOST_PORT}/health"
curl --fail --silent "http://localhost:${HOST_PORT}/environment" | grep -q "$EXPECTED_ENVIRONMENT"
curl --fail --silent "http://localhost:${HOST_PORT}/version" | grep -q "$EXPECTED_VERSION"
docker exec "$APP_CONTAINER" python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); socket.create_connection((h,p),5).close(); print('DATABASE CONNECTIVITY SUCCESS:',h,p)"
echo "ALL VALIDATIONS PASSED"
