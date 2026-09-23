# T2 — Inventario + compra (gasta créditos)

## Scope
- `src/db/models/miembro_accesorio_comprado.py` (nuevo)
- `src/db/migrate.py`, `src/db/migrations/0025_accesorio_comprado.py` (nuevo)
- `src/services/tienda_service.py` (edit: agrega `comprar_accesorio`, `listar_inventario`)
- `tests/integration/services/tienda_compra.test.py` (nuevo)

## Changes

**Data Layer:**
- `MiembroAccesorioComprado`: `miembro_id` (GUID, PK+FK), `accesorio_id` (GUID, PK+FK), `comprado_en` (datetime).

**Service Logic:**
- `tienda_service.comprar_accesorio(session, miembro_id, accesorio_id)`: rechaza (`ValidationError`) si ya está en `MiembroAccesorioComprado`; rechaza si `avatar_service.obtener_balance_creditos(miembro_id) < accesorio.precio_creditos`; si pasa, crea una `CreditoTransaccion(cantidad=-precio, motivo="compra_accesorio")` (reusando el modelo de `avatares-economia`) y la fila de compra, ambas en la misma transacción.
- `tienda_service.listar_inventario(session, miembro_id) -> list[AccesorioAvatar]`: todo lo que el miembro compró, SIN aplicar el filtro de ventana de disponibilidad de T1 (un ítem ya comprado se conserva). Actualizar `listar_catalogo_accesorios` (T1) para excluir del catálogo de compra cualquier ítem que ya esté en `listar_inventario` fuera de ventana... en realidad, la regla real es la inversa: un ítem fuera de ventana SÍ debe seguir en el catálogo si ya fue comprado (para no romper su visibilidad ahí también) — completar ese join pendiente de T1 acá.

## Implementation Steps
1. Baseline: confirmar T1 en verde.
2. RED: escribir `tienda_compra.test.py` con TC-003, TC-004, TC-005, TC-010.
3. GREEN: implementar el modelo, la migración, `comprar_accesorio`, `listar_inventario`, y completar el join pendiente de T1.
4. Confirmar atomicidad: la `CreditoTransaccion` negativa y la fila de compra se escriben en una sola transacción (ambas o ninguna).

## Design Rationale
Reusar el mismo ledger `CreditoTransaccion` para gastos (cantidad negativa) que para ganancias (cantidad positiva) evita un segundo mecanismo de contabilidad — el saldo sigue siendo una sola suma, consistente con el principio ya establecido en `avatares-economia`.

## Dependencies
T1 (catálogo). Consume `avatar_service.obtener_balance_creditos` y el modelo `CreditoTransaccion` de `avatares-economia`.

## Done When
- [ ] TC-003, TC-004, TC-005, TC-010 pasan.
- [ ] Una compra exitosa y una rechazada dejan el saldo de créditos exactamente donde corresponde (verificado, no solo asumido).

## Interfaces Produced
- `comprar_accesorio(session, miembro_id, accesorio_id) -> MiembroAccesorioComprado`.
- `listar_inventario(session, miembro_id) -> list[AccesorioAvatar]`.

## Standalone Verifiable
Sí, una vez que T1 está completo en la misma rama.
