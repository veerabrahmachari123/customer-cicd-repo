#!/usr/bin/env bash
set -euo pipefail
for n in customer-dev-net customer-uat-net customer-prod-net; do
  docker network inspect "$n" >/dev/null 2>&1 || docker network create "$n"
done
docker network ls | grep 'customer-.*-net'
