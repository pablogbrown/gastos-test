#!/usr/bin/env bash
# T3 (dockerize-local-env) — TC-001, TC-002 y la pata de proxy de TC-005:
# `docker compose up` levanta los 3 servicios, el backend responde 200 en
# /health, y un dato registrado vía API persiste en el Postgres real del
# servicio `db`. También ejercita el proxy /casas del frontend
# dockerizado (sin automatizar el navegador — ver README de esta suite y
# evidence/build-results.md para el alcance real de TC-005).
#
# Requiere Docker + Docker Compose. No se corre como parte de `pytest`
# (no hay entorno Python involucrado en lo que valida) — se invoca
# directamente o vía `make test-infra` / CI con Docker disponible.
#
# Nota sobre reintentos: cada aserción reintenta durante varios segundos
# en vez de fallar en el primer intento — algunos entornos Docker (rebuild
# rápido de contenedores, port-forwarding) pueden dar una respuesta
# transitoriamente inconsistente justo en el instante en que un servicio
# recién pasa a estar listo; reintentar es más robusto que asumir que el
# primer resultado ya es el estado estable.
set -uo pipefail

cd "$(dirname "$0")/../../.."

cleanup() {
  docker compose down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

retry() {
  # retry <intentos> <segundos-entre-intentos> <comando...>
  local intentos="$1" espera="$2"
  shift 2
  local i
  for ((i = 1; i <= intentos; i++)); do
    if "$@"; then
      return 0
    fi
    sleep "${espera}"
  done
  return 1
}

echo "== docker compose up --build =="
docker compose up -d --build

echo "== Esperando a que el backend responda en /health =="
if ! retry 60 1 curl -sf http://127.0.0.1:8000/health -o /dev/null; then
  echo "TC-001 FAILED: /health nunca respondió"
  docker compose logs
  exit 1
fi
curl -sf http://127.0.0.1:8000/health | grep -q '"status":"ok"' \
  || { echo "TC-001 FAILED: /health no devolvió status ok"; exit 1; }
echo "TC-001 OK: los 3 servicios arrancan y /health responde 200"

echo "== TC-002: un dato registrado vía API persiste en Postgres =="
usuario_id=$(python3 -c 'import uuid; print(uuid.uuid4())')
resp=$(curl -sf -X POST http://127.0.0.1:8000/casas \
  -H 'Content-Type: application/json' \
  -H "X-Usuario-Id: ${usuario_id}" \
  -d '{"nombre":"Casa Docker Test"}')
casa_id=$(echo "${resp}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

_check_casa_persistida() {
  local count
  count=$(docker compose exec -T db psql -U "${POSTGRES_USER:-taskia}" -d "${POSTGRES_DB:-taskia}" -tAc \
    "select count(*) from casas where id='${casa_id}'" 2>/dev/null)
  [ "$(echo "${count}" | tr -d '[:space:]')" = "1" ]
}
if ! retry 15 1 _check_casa_persistida; then
  echo "TC-002 FAILED: la casa creada no aparece en el Postgres del servicio db"
  exit 1
fi
echo "TC-002 OK: la casa creada vía API persiste en el Postgres del servicio db"

echo "== TC-005 (pata de proxy): frontend dockerizado -> backend dockerizado =="
if ! retry 60 1 curl -sf http://127.0.0.1:5173/ -o /dev/null; then
  echo "TC-005 (proxy leg) FAILED: el frontend nunca respondió"
  docker compose logs frontend
  exit 1
fi

_check_proxy_crea_casa() {
  local usuario resp nombre
  usuario=$(python3 -c 'import uuid; print(uuid.uuid4())')
  resp=$(curl -sf -X POST http://127.0.0.1:5173/casas \
    -H 'Content-Type: application/json' \
    -H "X-Usuario-Id: ${usuario}" \
    -d '{"nombre":"Casa via Frontend Proxy"}' 2>/dev/null) || return 1
  nombre=$(echo "${resp}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["nombre"])' 2>/dev/null) || return 1
  [ "${nombre}" = "Casa via Frontend Proxy" ]
}
if ! retry 15 1 _check_proxy_crea_casa; then
  echo "TC-005 (proxy leg) FAILED: el proxy /casas del frontend nunca devolvió la respuesta esperada del backend"
  exit 1
fi
echo "TC-005 (proxy leg) OK: el proxy /casas del frontend dockerizado llega al backend dockerizado"

echo
echo "T3 gate: TC-001, TC-002 y la pata de proxy de TC-005 en verde."
