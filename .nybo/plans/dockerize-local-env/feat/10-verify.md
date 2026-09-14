# Verify — Dockerizar el Entorno Local

## Test Scenarios by Task

### T1 — Backend Dockerfile
- Happy: `docker build -f Dockerfile.backend .` construye sin error.
- Happy: sin `DATABASE_URL`, el backend sigue usando `sqlite:///:memory:` (TC-003).
- Happy: las 4 migraciones corren limpias contra un Postgres real (TC-004).

### T2 — Frontend Dockerfile
- Happy: `docker build -f Dockerfile.frontend .` construye sin error.
- Regression: `npm run dev` local (sin Docker) sigue apuntando a `127.0.0.1:8000` — no debe romper el flujo ya verificado manualmente en la sesión anterior.

### T3 — docker-compose
- Happy: `docker compose up` levanta `db`, `backend`, `frontend`; `db` pasa su healthcheck antes de que `backend` arranque.
- Happy: `GET /health` del backend responde 200 (TC-001).
- Happy: un dato registrado vía API persiste en el Postgres del servicio `db` (TC-002).
- Happy: crear una casa desde el frontend dockerizado llega al backend dockerizado y se refleja en Inicio (TC-005).

### T4 — Makefile
- Happy: `make up`/`down`/`build`/`logs`/`migrate` ejecutan el comando `docker compose` correcto.
- Happy: `make test` corre la suite de pytest contra el backend dockerizado y reporta pass/fail (TC-006).

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-001 a TC-006 en verde | `[AUTO]` |
| Las 4 migraciones corren limpias contra PostgreSQL real, no solo SQLite | `[AUTO]` |
| `npm run dev` sin Docker sigue funcionando igual que antes de esta spec | `[AUTO]` |
| Revisión de que el Makefile documentado en el README coincide con los targets reales | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-002/TC-004 | Tipos de columna (`GUID`, `Enum`) contra el dialecto Postgres | SQLAlchemy no traduce un tipo custom igual en ambos dialectos |
| TC-003 | `src/db/base.py` | Se introdujo una lectura de env var que rompe el default a SQLite |
| TC-001/TC-005 | `depends_on`/healthcheck de `db` en `docker-compose.yml` | Backend arranca antes de que Postgres acepte conexiones |
| TC-006 | Comando `make test` | Apunta al backend equivocado, o el contenedor no tiene pytest instalado |

## End-to-End Verification
1. `git clone` en una máquina limpia (o simular con `docker compose down -v` para borrar todo estado previo).
2. `make up`.
3. `curl http://localhost:8000/health` → 200.
4. Abrir `http://localhost:5173`, crear una casa, agregar un miembro, registrar un gasto — confirmar que persiste (recargar la página, verificar que sigue ahí).
5. `make test` → suite de pytest pasa.
6. `make down` → los 3 servicios se detienen limpiamente.

**Gate final:** TC-001 a TC-006 en verde y los 6 pasos completan sin error.
