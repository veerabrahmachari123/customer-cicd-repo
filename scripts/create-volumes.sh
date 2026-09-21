#!/usr/bin/env bash
set -euo pipefail
for v in customer-db-dev-data customer-db-uat-data customer-db-prod-data; do
  docker volume inspect "$v" >/dev/null 2>&1 || docker volume create "$v"
done
docker volume ls | grep 'customer-db-.*-data'
