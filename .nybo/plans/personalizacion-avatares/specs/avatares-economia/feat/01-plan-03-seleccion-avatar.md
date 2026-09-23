# T3 — Desbloqueo por nivel + selección + endpoints

## Scope
- `src/db/models/miembro_avatar_seleccionado.py` (nuevo)
- `src/db/migrate.py`, `src/db/migrations/0023_avatar_seleccionado.py` (nuevo)
- `src/services/avatar_service.py` (edit: agrega `listar_avatares_disponibles`, `seleccionar_avatar`, `obtener_avatar_seleccionado`)
- `src/api/routes/avatares.py` (nuevo)
- `src/api/main.py` (edit: registrar el router)
- `tests/integration/services/avatar_seleccion.test.py` (nuevo)

## Changes

**Data Layer:**
- `MiembroAvatarSeleccionado`: `miembro_id` (GUID, PK + FK a `miembros`), `avatar_personaje_id` (GUID, FK a `avatar_personajes`), `actualizado_en` (datetime, `onupdate=func.now()`).

**Service Logic:**
- `avatar_service.listar_avatares_disponibles(session, miembro_id) -> list[AvatarPersonaje]`: reusa `listar_catalogo` (T2) filtrado a `nivel_requerido <= nivel actual del miembro` — el nivel se calcula llamando a `ranking_service._nivel_de` sobre el total histórico de puntos de ese miembro (nunca duplicar el umbral acá).
- `avatar_service.seleccionar_avatar(session, miembro_id, avatar_personaje_id)`: valida que `avatar_personaje_id` esté en `listar_avatares_disponibles(miembro_id)` — si no, `PermissionDeniedError`; si sí, upsert de `MiembroAvatarSeleccionado`.
- `avatar_service.obtener_avatar_seleccionado(session, miembro_id) -> Optional[AvatarPersonaje]`: `None` si no hay fila.

**API Route:**
- `GET /miembros/{miembro_id}/avatares-disponibles`, `GET /miembros/{miembro_id}/avatar`, `PUT /miembros/{miembro_id}/avatar` (body `{avatar_personaje_id}`, 403 si no desbloqueada), `GET /miembros/{miembro_id}/creditos` (usa `obtener_balance_creditos` de T1).

## Implementation Steps
1. Baseline: confirmar que T1 y T2 están en verde antes de empezar (dependencia real, no solo declarada).
2. RED: escribir `avatar_seleccion.test.py` con TC-005/006/007/008.
3. GREEN: implementar el modelo, la migración, las 3 funciones de servicio, y las 4 rutas.
4. REFACTOR: confirmar que ningún umbral de nivel quedó duplicado fuera de `ranking_service.NIVELES`.

## Design Rationale
El nivel se recalcula en el momento (nunca cacheado) — un miembro que subió de nivel recién ahora puede elegir razas antes bloqueadas sin esperar ningún proceso de sincronización, mismo criterio "derivado, no cacheado" que el resto de esta spec.

## Dependencies
T1 (créditos, para el endpoint `GET .../creditos`), T2 (catálogo, para filtrar por nivel).

## Done When
- [ ] TC-005, TC-006, TC-007, TC-008 pasan.
- [ ] Las 4 rutas responden con los códigos esperados (200/403/404).

## Interfaces Produced
- `listar_avatares_disponibles(session, miembro_id) -> list[AvatarPersonaje]`.
- `seleccionar_avatar(session, miembro_id, avatar_personaje_id) -> MiembroAvatarSeleccionado`.
- `obtener_avatar_seleccionado(session, miembro_id) -> Optional[AvatarPersonaje]`.

## Standalone Verifiable
Sí, una vez que T1 y T2 están mergeados/completos en la misma rama de esta spec.
