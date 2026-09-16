# T1 — `listar_gastos` acepta `mes` opcional

## Scope
- `src/services/gasto_service.py`
- `tests/integration/services/gasto_listar_mes.test.py` (nuevo)

## Changes
- Agregar un helper privado `_rango_mes(mes: str) -> Tuple[date, date]`
  en `gasto_service.py` (misma lógica que
  `balance_service._rango_mes`: primer y último día del mes, `raise
  ValidationError` si el formato no es `YYYY-MM` o el mes no es 1-12 —
  duplicado deliberadamente, ver Design Rationale en `00-overview.md`).
- `listar_gastos(casa_id: UUID, mes: Optional[str] = None) ->
  List[Gasto]`:
  - Llama primero a `suscripcion_service.generar_gastos_pendientes`
    (sin cambios, ya existe).
  - Si `mes` es `None`: comportamiento idéntico al actual — todos los
    gastos de la casa (TC-002).
  - Si `mes` está presente: filtra además por
    `Gasto.fecha.between(desde, hasta)` (TC-001).

## Design Rationale
`mes=None` preserva el 100% del comportamiento actual — necesario
porque `dashboard_service.armar_dashboard` llama a `listar_gastos(casa_id)`
sin `mes` esperando el historial completo (TC-006 lo confirma como
control de regresión).

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] TC-001 y TC-002 pasan.
- [ ] TC-006 (control de `armar_dashboard`) pasa sin cambios.

## Interfaces Produced
- `listar_gastos(casa_id, mes: Optional[str] = None)`.

## Standalone Verifiable
Sí.
