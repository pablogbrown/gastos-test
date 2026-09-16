# T2 — `auto_service`; `mantenimiento_service` filtra por auto

## Scope
- `src/services/auto_service.py` (nuevo).
- `src/services/mantenimiento_service.py`.
- `tests/integration/services/auto_service.test.py` (nuevo).
- `tests/integration/services/mantenimiento_auto.test.py` (nuevo).

## Changes
**`auto_service.py`**
- `crear_auto(casa_id, marca, modelo, actor, patente=None, anio=None) -> Auto`:
  valida `marca`/`modelo` no vacíos; requiere `actor` miembro activo
  (TC-001).
- `listar_autos(casa_id) -> List[Auto]`.

**`mantenimiento_service.py`**
- `crear_item(..., auto_id: Optional[UUID] = None)`: si `auto_id` no es
  `None`, valida que exista un `Auto` con ese id en `casa_id`
  (`NotFoundError` si no — cubre también TC-005, un auto de otra casa)
  (TC-002).
- `listar_items(casa_id, auto_id: Optional[UUID] = None)`: sin
  `auto_id`, filtra `WHERE auto_id IS NULL` (comportamiento actual de
  `mantenimiento-casa`, sin cambios — TC-003, primera mitad); con
  `auto_id`, filtra `WHERE auto_id = :auto_id` (TC-003, segunda mitad).
- `obtener_items_con_alerta`: sin cambios en su filtro (ya incluye
  todos los ítems próximos a vencer, sin distinguir `auto_id` — TC-004)
  — solo se le agrega `auto_id`/`auto_nombre` al dataclass de resultado
  para que el frontend arme el texto correcto.

## Design Rationale
`listar_items` cambia su significado por defecto de "todos los ítems"
(spec `mantenimiento-casa`, donde `auto_id` no existía) a "solo los de
la casa" — necesario para que la pantalla "Mantenimiento" (sin cambios
de código en esta spec) siga mostrando exclusivamente ítems de la casa
una vez que empiezan a existir ítems de auto.

## Dependencies
T1 (`Auto`, `ItemMantenimiento.auto_id`).

## Done When
- [ ] TC-001 a TC-005 pasan.

## Interfaces Produced
- `crear_auto`, `listar_autos`.

## Interfaces Consumed
- Extiende `crear_item`/`listar_items`/`obtener_items_con_alerta` de `mantenimiento-casa`.

## Standalone Verifiable
Sí.
