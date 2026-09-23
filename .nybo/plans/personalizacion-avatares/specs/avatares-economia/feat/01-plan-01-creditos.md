# T1 — Ledger de créditos + hook en `completar_tarea`

## Scope
- `src/db/models/credito_transaccion.py` (nuevo)
- `src/db/migrate.py`, `src/db/migrations/0021_creditos.py` (nuevo)
- `src/services/tarea_service.py` (edit: hook en `completar_tarea`)
- `src/services/avatar_service.py` (nuevo, arranca con `obtener_balance_creditos`)
- `tests/integration/services/creditos.test.py` (nuevo)

## Changes

**Data Layer:**
- `CreditoTransaccion`: `id` (GUID PK), `casa_id` (GUID, plano sin FK a nivel de modelo — mismo patrón `DBG-02`/`DBG-03` si la tabla referenciada ya existe con migración anterior, o `ForeignKey` directo si `casas` ya existe desde una migración temprana — confirmar orden de migraciones antes de decidir), `miembro_id` (idem contra `miembros`), `cantidad` (int, positivo en esta task), `motivo` (string, ej. `"tarea_completada"`), `creada_en` (datetime, default `func.now()`).
- Migración `0021_creditos.py`: crea la tabla — `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` no aplica acá (tabla nueva, no columna nueva), pero seguir el patrón `create_all(tables=[CreditoTransaccion.__table__], checkfirst=True)` ya usado en migraciones de tabla nueva de este proyecto.

**Service Logic:**
- `avatar_service.obtener_balance_creditos(session, miembro_id) -> int`: `SELECT SUM(cantidad) WHERE miembro_id = ...`, `0` si no hay filas — nunca un contador cacheado en `Miembro` (mismo criterio que `ranking_service.calcular_ranking`).
- `tarea_service.completar_tarea`: justo después del `commit` que persiste `HistorialTarea` (mismo punto donde `registrar_actividad` ya se engancha, `[SERV-02]`), insertar una `CreditoTransaccion(cantidad=historial.puntos_obtenidos, motivo="tarea_completada", miembro_id=beneficiario.id, casa_id=casa_id)` y comitear. Nunca dentro de la misma transacción que el `commit` de `HistorialTarea` — después, como un paso separado, mismo orden que `registrar_actividad`.

## Implementation Steps
1. Confirmar el orden de migraciones existente (`src/db/migrate.py`) para decidir si `CreditoTransaccion.casa_id`/`miembro_id` pueden ser `ForeignKey` directo o necesitan el patrón `DBG-02`/`DBG-03` (columna plana + `ALTER TABLE` en la misma migración, después del `create_all`).
2. RED: escribir `creditos.test.py` con TC-001 (completar una tarea crea la transacción) y TC-002 (recompletar no crea una segunda).
3. GREEN: implementar el modelo, la migración, `obtener_balance_creditos`, y el hook en `completar_tarea`.
4. REFACTOR: confirmar que el hook no interfiere con el `commit` de `HistorialTarea` (transacciones separadas) ni con `registrar_actividad`.

## Design Rationale
Mismo principio ya aplicado a puntos/ranking (`[SERV-01]`-adjacent): un ledger de eventos es la fuente de verdad, nunca un contador mutable — evita desincronización y da auditoría gratis (qué otorgó cada crédito y cuándo), acorde al pedido de "economía completa" del usuario.

## Dependencies
Ninguna — es la base de la que dependen T3 (selección, necesita `avatar_service.py` ya existente) y toda `tienda-accesorios` (gasta créditos).

## Done When
- [ ] TC-001, TC-002 pasan.
- [ ] `obtener_balance_creditos` exportado y usado por al menos un test.
- [ ] Migración corre limpia sobre una base vacía y sobre una ya poblada.

## Interfaces Produced
- `obtener_balance_creditos(session, miembro_id) -> int`.

## Standalone Verifiable
Sí — el ledger y el hook son completamente verificables con `pytest` sin depender de ninguna otra task de esta spec.
