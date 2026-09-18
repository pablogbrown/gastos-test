# T2 — Logros

## Scope
- `src/db/models/logro_obtenido.py` (nuevo): modelo `LogroObtenido`
  (shape en `00-overview.md`) — `ForeignKey()` real a `casas`/
  `miembros` (seguro, ambas tablas existen desde la migración `0001`).
- `src/db/migrations/0020_gamificacion.py` (nuevo): crea
  `logros_obtenidos` y agrega `Casa.meta_puntos_mensual` (columna
  nullable en una tabla existente — ver T3, se hace en la misma
  migración porque ambas piezas de esquema son chicas y van juntas en
  esta spec).
- `src/db/migrate.py`: agregar `"0020_gamificacion"`.
- `src/services/logro_service.py` (nuevo): `LOGROS_CATALOGO`,
  `evaluar_logros(casa_id, miembro_id)` (chequeo de duplicado en el
  service layer antes del insert — `[SERV-01]`, nunca un constraint de
  DB), `listar_logros_obtenidos(casa_id)`.
- `src/services/tarea_service.py`: `completar_tarea` llama a
  `logro_service.evaluar_logros(casa_id, miembro_id)` después del
  commit, junto a los hooks de `registrar_actividad` existentes.
- `src/api/routes/tareas.py`: nuevo `GET /casas/{casa_id}/logros`.
- `src/frontend/api/tareasClient.ts`: tipo `Logro`,
  `listarLogros(casaId)`.

## Dependencies
T1 (`evaluar_logros` reusa `ranking_service.calcular_racha`).

## Done When
- TC-005 pasa.
- Completar una tarea sigue funcionando exactamente igual para un
  miembro que no cruza ningún umbral (no crea ningún `LogroObtenido`,
  no rompe el flujo existente de `completar_tarea`).

## Verifiability
INTEGRATION — nuevo `tests/integration/services/logros.test.py`
(migración incluida — confirmar idempotencia contra Postgres real en
`tests/integration/db/postgres_migrations.test.py`, extendido).
