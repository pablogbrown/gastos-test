# Verify — Gestión de Gastos

## Test Scenarios by Task

### T1 — Data Layer
- Happy: insertar Gasto + GastoParticipante consistentes.
- Edge: suma de `monto_correspondiente` distinta del `importe` → debe ser imposible por diseño del servicio (verificado en T2).

### T2 — Service Layer
- Happy: `registrar_gasto` con categoría válida (TC-001).
- Error: `registrar_gasto` sin categoría → rechazado (TC-002).
- Error: `crear_categoria` por actor no-admin → rechazado (TC-003).
- Happy: gasto sin participantes explícitos se divide entre todos los activos (TC-004).
- Happy: gasto con participantes explícitos solo los afecta a ellos (TC-005).
- Happy: división de $40.000 entre 4 → $10.000 c/u (TC-006).
- Happy: balance Pablo +$30.000 / Ana -$30.000 sobre el ejemplo del documento (TC-007).
- Happy: transferencia sugerida exacta entre deudor y acreedor (TC-008).
- Edge: nuevo miembro agregado no altera gastos previos (TC-009).

### T3 — API Routes
- Contrato: 400 sin categoría, 403 sin rol admin en categorías.

### T4 — UI
- Manual/exploratorio: flujo completo de registro de gasto y consulta de balance.

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-001 a TC-010 en verde | `[AUTO]` |
| Suma de partes = importe en el 100% de los gastos de prueba | `[AUTO]` |
| Revisión visual de las pantallas de Gastos/Balance | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-006 | Lógica de redondeo en división | Redondeo no ajustado al último participante |
| TC-007 | `calcular_balance` | Agregación mezclando gastos de otras casas |
| TC-009 | `registrar_gasto` | Participantes resueltos dinámicamente en vez de fijados al registrar |
| TC-010 | Query de historial | Filtro excluye miembros inactivos indebidamente |

## End-to-End Verification
1. Registrar gasto "Compra supermercado" $75.000, categoría Supermercado, todos los miembros.
2. Registrar gasto "Cena" $30.000 solo entre dos miembros.
3. Consultar balance y verificar montos a favor/en contra.
4. Agregar un nuevo miembro y confirmar que los gastos anteriores no cambian.
5. Desactivar un miembro con gastos y confirmar que sigue en el historial.

**Gate final:** TC-001 a TC-010 en verde y los 5 pasos completan sin error.
