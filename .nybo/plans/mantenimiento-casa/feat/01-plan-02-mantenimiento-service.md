# T2 — `mantenimiento_service` (alta/materiales/completar/alerta)

## Scope
- `src/services/mantenimiento_service.py` (nuevo).
- `tests/integration/services/mantenimiento_service.test.py` (nuevo).

## Changes
- Constantes: `PERIODICIDADES_VALIDAS = {"semanal", "mensual",
  "trimestral", "semestral", "anual"}`, `_DIAS_POR_PERIODICIDAD =
  {"semanal": 7, "mensual": 30, "trimestral": 90, "semestral": 180,
  "anual": 365}`, `UMBRAL_ALERTA_DIAS = 7` (mismo criterio que
  `tarjeta_service.py`).
- `crear_item(casa_id, nombre, descripcion, fecha_estimada, recurrente, periodicidad, actor, materiales=None) -> ItemMantenimiento`:
  - Valida `nombre` no vacío.
  - Si `recurrente`: exige `periodicidad` en `PERIODICIDADES_VALIDAS` Y
    `fecha_estimada` no `None` (`ValidationError` si falta cualquiera de
    las dos, TC-002) — mismo criterio recién corregido en
    `tarea_service.crear_tarea`.
  - Requiere `actor` miembro activo de la casa
    (`requiere_membresia_activa`).
  - `materiales` (opcional): lista de `{nombre, cantidad}` — crea una
    fila `MaterialMantenimiento` por cada uno, `conseguido=False`
    (TC-003).
- `agregar_material(casa_id, item_id, nombre, cantidad, actor) -> MaterialMantenimiento`.
- `actualizar_material(casa_id, item_id, material_id, conseguido: bool, actor) -> MaterialMantenimiento`
  (TC-004).
- `listar_items(casa_id) -> List[ItemMantenimiento]`.
- `completar_item(casa_id, item_id, actor) -> ItemMantenimiento`:
  - Si ya está `"completado"`: `ConflictError`.
  - Si `recurrente` y `fecha_estimada` en el futuro: `ConflictError`
    (TC-007) — mismo gate recién agregado a `tarea_service.completar_tarea`.
  - Marca `estado="completado"`.
  - Si `recurrente`: crea una nueva `ItemMantenimiento` en
    `"pendiente"`, misma definición, `fecha_estimada` = fecha estimada
    actual + `_DIAS_POR_PERIODICIDAD[periodicidad]` días (TC-006). Si NO
    es recurrente, no genera nada (TC-005).
- `obtener_items_con_alerta(casa_id) -> List[ItemMantenimientoAlerta]`
  (dataclass `id, nombre, fecha_estimada, dias_para_vencimiento,
  vencido`): mismo criterio que `tarjeta_service.obtener_tarjetas_con_alerta`
  — incluye ítems pendientes con `fecha_estimada` a `UMBRAL_ALERTA_DIAS`
  días o menos, o ya vencidos (TC-008).

## Design Rationale
Ver `00-overview.md` — por qué `_DIAS_POR_PERIODICIDAD`/el gate de
completar-antes-de-tiempo no se comparten con `tarea_service.py` pese a
ser conceptualmente el mismo patrón.

## Dependencies
T1 (`ItemMantenimiento`, `MaterialMantenimiento`).

## Done When
- [ ] TC-001 a TC-008 pasan.

## Interfaces Produced
- `crear_item`, `agregar_material`, `actualizar_material`, `listar_items`, `completar_item`, `obtener_items_con_alerta`.

## Standalone Verifiable
Sí.
