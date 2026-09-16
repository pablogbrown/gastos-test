# T2 — Servicios propagan `estado`; `actualizar_estado_gasto`

## Scope
- `src/services/gasto_service.py`
- `src/services/suscripcion_service.py`
- `src/services/resumen_importer_service.py`
- `tests/integration/services/gasto_estado.test.py` (nuevo)

## Changes
**`gasto_service.py`**
- `registrar_gasto(..., estado: str = "pagado")`: valida `estado in
  {"pagado", "a_pagar"}`, si no `raise ValidationError`. Persiste en
  `Gasto.estado`.
- `_crear_gastos_en_cuotas`: recibe y propaga `estado` a cada una de las
  N cuotas generadas (TC-003) — mismo criterio que `moneda`.
- `registrar_gasto_cuotas_restantes` (ya existente, spec
  `importar-resumen-tarjeta`): agrega parámetro `estado`, propagado a
  cada cuota restante generada.
- `actualizar_estado_gasto(casa_id, gasto_id, estado, actor) -> Gasto`
  (nueva): valida `estado`, valida que el gasto exista en la casa
  (`NotFoundError` si no), lo actualiza y devuelve el gasto actualizado
  (TC-006/TC-007). Cualquier miembro activo de la casa puede llamarla —
  mismo nivel de permiso que `registrar_gasto` (sin `_validar_actor_admin`).

**Control (TC-008)**: agregar un test que registra gastos con distintos
`estado`, cambia alguno vía `actualizar_estado_gasto`, y confirma que
`balance_service.calcular_balance` devuelve exactamente los mismos
montos antes y después — `balance_service.py` no se modifica en esta
spec.

**`suscripcion_service.py`**
- `crear_suscripcion`/`generar_gastos_pendientes`: sus llamadas a
  `registrar_gasto` pasan explícitamente `estado="a_pagar"` (TC-004) —
  un cargo automático de suscripción nunca nace "pagado".
- `registrar_suscripcion_detectada` (spec `importar-resumen-tarjeta`):
  su llamada a `registrar_gasto` pasa `estado="a_pagar"`.

**`resumen_importer_service.py`**
- Las 3 rutas de creación de gasto dentro de `importar_resumen` (gasto
  normal, `registrar_gasto_cuotas_restantes`,
  `registrar_suscripcion_detectada`) pasan explícitamente
  `estado="a_pagar"` (TC-005) — un resumen recién importado nunca se
  asume pagado.

## Design Rationale
El estado "a_pagar" para generadores automáticos se pasa como argumento
explícito en cada call-site, en vez de cambiar el default de
`registrar_gasto` — mantiene `registrar_gasto(...)` (sin `estado`)
significando "ya lo pagué", el caso más común de carga manual, y hace
explícito en cada generador automático por qué nace distinto.

## Dependencies
T1 (`Gasto.estado`).

## Done When
- [ ] TC-001 a TC-006 y TC-008 pasan.
- [ ] Suite completa en verde (tests existentes de cuotas/suscripciones/importación siguen pasando sin cambios de comportamiento salvo el nuevo campo).

## Interfaces Produced
- `registrar_gasto(..., estado: str = "pagado")`.
- `actualizar_estado_gasto(casa_id, gasto_id, estado, actor) -> Gasto`.

## Standalone Verifiable
Sí.
