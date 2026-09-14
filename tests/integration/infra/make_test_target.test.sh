#!/usr/bin/env bash
# T4 (dockerize-local-env) — TC-006: `make test` corre la suite de pytest
# del backend dockerizado y refleja su resultado (exit code).
#
# Requiere Docker + Docker Compose + make. Solo levanta db+backend (no
# necesita frontend para correr la suite de pytest).
set -uo pipefail

cd "$(dirname "$0")/../../.."

cleanup() {
  docker compose down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "== docker compose up --build db backend =="
docker compose up -d --build db backend

echo "== esperando a que el backend responda en /health =="
ok=false
for _ in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8000/health -o /dev/null 2>&1; then
    ok=true
    break
  fi
  sleep 1
done
if [ "$ok" != true ]; then
  echo "TC-006 FAILED: el backend nunca respondió, no se puede correr 'make test'"
  docker compose logs backend
  exit 1
fi

echo "== make test =="
make test
exit_code=$?

if [ "${exit_code}" -eq 0 ]; then
  echo "TC-006 OK: 'make test' corrió la suite de pytest contra el backend dockerizado y salió con código 0"
else
  echo "TC-006 FAILED: 'make test' salió con código ${exit_code} (la suite falló o el target apunta mal)"
  exit 1
fi
