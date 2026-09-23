# T3 — Equipar/desequipar por slot + endpoints

## Scope
- `src/db/models/miembro_accesorio_equipado.py` (nuevo)
- `src/db/migrate.py`, `src/db/migrations/0026_accesorio_equipado.py` (nuevo)
- `src/services/tienda_service.py` (edit: agrega `equipar_accesorio`, `desequipar_slot`)
- `src/api/routes/tienda.py` (nuevo)
- `src/api/main.py` (edit: registrar el router)
- `tests/integration/services/tienda_equipar.test.py` (nuevo)

## Changes

**Data Layer:**
- `MiembroAccesorioEquipado`: `miembro_id` (GUID, PK+FK), `slot` (string, PK — `"cabeza"`|`"cuello"`|`"cuerpo"`), `accesorio_id` (GUID, FK). Clave primaria compuesta `(miembro_id, slot)` — garantiza como máximo un ítem activo por slot por miembro a nivel de esquema, no solo en el service layer.

**Service Logic:**
- `tienda_service.equipar_accesorio(session, miembro_id, accesorio_id)`: valida que `accesorio_id` esté en `listar_inventario(miembro_id)` (T2) y sea compatible con la especie del avatar actual (`avatar_service.obtener_avatar_seleccionado`); si pasa, upsert de `MiembroAccesorioEquipado` sobre `(miembro_id, slot_del_accesorio)` — el upsert es lo que garantiza el reemplazo, nunca dos filas para el mismo slot.
- `tienda_service.desequipar_slot(session, miembro_id, slot)`: borra la fila si existe (no-op si no hay nada equipado en ese slot).

**API Route:**
- `GET /accesorios?miembro_id=...`, `GET /miembros/{miembro_id}/accesorios`, `POST /miembros/{miembro_id}/accesorios/{accesorio_id}/comprar`, `PUT /miembros/{miembro_id}/accesorios/equipar` (body `{accesorio_id}`), `DELETE /miembros/{miembro_id}/accesorios/{slot}/equipado`.

## Implementation Steps
1. Baseline: confirmar T2 en verde.
2. RED: escribir `tienda_equipar.test.py` con TC-006, TC-007, TC-008.
3. GREEN: implementar el modelo (clave compuesta), las 2 funciones de servicio, y las 5 rutas.
4. Confirmar que la clave primaria compuesta `(miembro_id, slot)` efectivamente rechaza a nivel de base una segunda fila para el mismo slot (no solo el service layer).

## Design Rationale
Usar `(miembro_id, slot)` como clave primaria (no un `id` autogenerado) hace que "como máximo un equipado por slot" sea una garantía del esquema, no solo una regla de negocio que un bug futuro podría saltarse — más fuerte que un `SERV-01`-style check puramente en el service layer para este caso puntual, porque la violación sería estructuralmente imposible.

## Dependencies
T2 (inventario). Consume `avatar_service.obtener_avatar_seleccionado` de `avatares-economia`.

## Done When
- [ ] TC-006, TC-007, TC-008 pasan.
- [ ] Las 5 rutas responden con los códigos esperados (200/403/404).

## Interfaces Produced
- `equipar_accesorio(session, miembro_id, accesorio_id) -> MiembroAccesorioEquipado`.
- `desequipar_slot(session, miembro_id, slot) -> None`.

## Standalone Verifiable
Sí, una vez que T2 está completo en la misma rama.
