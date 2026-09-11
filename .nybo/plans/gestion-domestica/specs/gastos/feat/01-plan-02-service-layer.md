# Task 2 — Service Layer: Registro, División y Balance

## Scope
- `src/services/gasto_service.py`
- `src/services/balance_service.py`
- `src/services/categoria_service.py`

## Changes
### Service Logic
- `crear_categoria(casa_id, nombre, actor)`: valida rol admin (REQ-002).
- `registrar_gasto(casa_id, descripcion, importe, fecha, categoria_id, pagado_por, participantes?, actor)`: valida `requiere_membresia_activa` (guard de `casas-miembros`), valida categoría requerida (TC-002), resuelve participantes (todos los activos si no se especifican — TC-004; subconjunto explícito — TC-005), divide `importe` en partes iguales entre participantes ajustando el redondeo en el último (TC-006), persiste Gasto + GastoParticipante.
- `calcular_balance(casa_id)`: agrega por miembro el total pagado (`sum(gastos.importe) where pagado_por = miembro`) y el total correspondiente (`sum(gasto_participantes.monto_correspondiente) where miembro_id = miembro`), balance = pagado - correspondiente (TC-007).
- `sugerir_transferencias(balance)`: algoritmo greedy que empareja mayor deudor con mayor acreedor hasta saldar (TC-008).
- Los gastos ya persistidos nunca se recalculan al agregarse un nuevo miembro — `registrar_gasto` fija los participantes en el momento del registro (REQ-007 / TC-009).

## Design Rationale
Separar `balance_service` de `gasto_service` respeta SRP: el registro de gastos y el cálculo agregado de balance cambian por razones distintas (nuevas reglas de división vs. nuevas formas de mostrar el balance).

## Dependencies
T1 (modelos); guard de membresía de la spec `casas-miembros` (cross-spec).

## Done When
- [ ] TC-001 a TC-009 pasan.
- [ ] La suma de `monto_correspondiente` de un gasto siempre iguala su `importe`.
- [ ] Build y tipos compilan.

## Interfaces Produced
- `{name: "registrar_gasto", signature: "(casa_id, descripcion, importe, fecha, categoria_id, pagado_por, participantes, actor) -> Gasto", kind: "function"}`
- `{name: "calcular_balance", signature: "(casa_id: UUID) -> BalancePorMiembro[]", kind: "function"}`
- `{name: "sugerir_transferencias", signature: "(balance: BalancePorMiembro[]) -> Transferencia[]", kind: "function"}`

## Standalone Verifiable
Sí, con T1 disponible y el guard de membresía mockeado.
