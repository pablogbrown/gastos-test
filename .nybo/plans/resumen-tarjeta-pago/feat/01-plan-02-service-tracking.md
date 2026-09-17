# T2 — Tracking de resúmenes + pagar_resumen + threading resumen_id

## Scope
- `src/services/gasto_service.py`:
  - `registrar_gasto(...)` y `registrar_gasto_cuotas_restantes(...)`
    ganan `resumen_id: Optional[UUID] = None`, poblando `Gasto.
    resumen_id` en cada fila creada — mismo patrón que `tarjeta_id`.
- `src/services/suscripcion_service.py`:
  - `registrar_suscripcion_detectada(...)` gana `resumen_id:
    Optional[UUID] = None`, pasado a su llamada interna a
    `registrar_gasto`.
- `src/services/resumen_importer_service.py`:
  - `ResumenImportado` (dataclass en memoria, sin cambiar de nombre)
    gana el campo `resumen_id: UUID`.
  - `importar_resumen`: agregar el chequeo de duplicado (REQ-002) ANTES
    de `actualizar_tarjeta` — buscar `ResumenTarjeta` con
    `(tarjeta_id, fecha_cierre=resumen.fecha_cierre_actual)`; si existe,
    `raise ConflictError(f"Ya se importó un resumen con cierre "
    f"{resumen.fecha_cierre_actual} para esta tarjeta el "
    f"{existente.importado_en}.")` sin escribir nada más. Si no existe,
    crear el `ResumenTarjeta` (estado `"pendiente"`) después de
    actualizar la tarjeta, y pasar `resumen_id=resumen_registro.id` a
    cada una de las tres llamadas de creación de gasto dentro del loop.
    Al final del loop, actualizar `resumen_registro.gastos_creados`.
  - Nuevo `pagar_resumen(casa_id, resumen_id, actor) -> ResumenTarjeta`:
    `NotFoundError` si el resumen no existe en esa casa;
    `ConflictError` si ya está `"pagado"`; si no, `UPDATE gastos SET
    estado='pagado' WHERE resumen_id=:resumen_id` (bulk, vía sesión de
    SQLAlchemy) + `resumen.estado = "pagado"`, commit.
  - Nuevo `listar_resumenes(casa_id, tarjeta_id) -> List[ResumenTarjeta]`:
    `NotFoundError` si la tarjeta no existe en esa casa; ordenado por
    `fecha_cierre` descendente.

## Dependencies
T1 (necesita el modelo `ResumenTarjeta` y `Gasto.resumen_id`).

## Done When
- TC-001, TC-002, TC-003, TC-004, TC-005, TC-006 pasan en
  `tests/integration/services/resumen_tarjeta.test.py` (nuevo archivo).
- El test existente `tests/integration/services/resumen_importer.
  test.py` sigue pasando sin modificaciones (el nuevo parámetro
  `resumen_id` es opcional en todos lados).
- Reutilizar la fixture de PDF ya existente en
  `resumen_importer.test.py` para TC-002/TC-003 (importar el mismo PDF
  dos veces).

## Verifiability
INTEGRATION — `tests/integration/services/resumen_tarjeta.test.py`.
Regression gate: sí (toca `gasto_service`/`suscripcion_service`, ya
cubiertos por sus propias suites existentes).
