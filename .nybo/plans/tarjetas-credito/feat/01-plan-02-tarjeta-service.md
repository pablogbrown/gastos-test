# T2 — `tarjeta_service`: CRUD + cálculo de alerta

## Scope
- `src/services/tarjeta_service.py` (nuevo).
- `tests/integration/services/tarjeta_service.test.py` (nuevo).

## Changes
- `crear_tarjeta(casa_id, miembro_id, banco, nombre, ultimos_digitos, fecha_cierre_actual, fecha_vencimiento_actual, actor) -> TarjetaCredito`:
  valida campos obligatorios (banco/nombre/ultimos_digitos/fechas),
  `raise ValidationError` si falta alguno (TC-002).
- `listar_tarjetas(casa_id) -> List[TarjetaCredito]`: solo `activa=True`.
- `actualizar_tarjeta(casa_id, tarjeta_id, actor, fecha_cierre_actual=None, fecha_vencimiento_actual=None, saldo_actual_ars=None, saldo_actual_usd=None) -> TarjetaCredito`:
  actualiza solo los campos provistos (TC-003).
- `eliminar_tarjeta(casa_id, tarjeta_id, actor) -> None`: `activa = False` (soft-delete, TC-004).
- `obtener_tarjetas_con_alerta(casa_id) -> List[TarjetaAlerta]` (dataclass
  `id, nombre, banco, fecha_vencimiento_actual, dias_para_vencimiento,
  vencida`): para cada tarjeta activa de la casa, calcula
  `dias_para_vencimiento = (fecha_vencimiento_actual - date.today()).days`;
  incluye la tarjeta si `dias_para_vencimiento <= UMBRAL_ALERTA_DIAS`
  (constante `= 7`, TC-005/TC-007), marcando `vencida = dias_para_vencimiento < 0` (TC-006).

## Design Rationale
`obtener_tarjetas_con_alerta` vive en este servicio (no en
`dashboard_service`) siguiendo el mismo criterio que
`generar_gastos_pendientes` vive en `suscripcion_service`: la lógica de
negocio de "qué es una alerta" pertenece al dominio de la tarjeta, el
dashboard solo la consume.

## Dependencies
T1 (`TarjetaCredito`).

## Done When
- [ ] TC-001 a TC-007 pasan.

## Interfaces Produced
- `crear_tarjeta`, `listar_tarjetas`, `actualizar_tarjeta`, `eliminar_tarjeta`, `obtener_tarjetas_con_alerta`.

## Standalone Verifiable
Sí.
