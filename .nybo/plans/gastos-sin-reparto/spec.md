# Gastos sin reparto entre participantes

## Intention

### What
Un gasto deja de repartirse entre participantes y de generar deudas
individuales — pasa a ser simplemente una salida de fondos de la casa
(a futuro se sumarán ingresos como entradas al mismo fondo). "Balance"
deja de calcular quién le debe a quién: muestra el total gastado por la
casa en el mes (por moneda) más, a modo informativo, cuánto aportó cada
miembro — sin ninguna cifra de deuda ni transferencia sugerida.

### Why
El modelo actual (estilo "cuenta compartida entre roommates", donde cada
gasto se divide y genera una deuda) no representa cómo la casa maneja su
plata: todo gasto sale de un fondo común, no es una deuda entre personas.
La única relación de deuda real entre personas es un préstamo explícito
(spec separada `prestamos-entre-miembros`) — un gasto de la casa nunca
debería generar una.

## Solution
Se elimina `GastoParticipante` (tabla, modelo, y todo el reparto que
generaba) — un `Gasto` ya no tiene participantes ni "monto
correspondiente". `pagado_por` se mantiene como dato informativo (quién
hizo la compra), sin ningún efecto sobre ningún cálculo. `balance_
service.calcular_balance` se reescribe: en vez de `BalancePorMiembro`
(pago/correspondía/balance) y `sugerir_transferencias`, devuelve el
total gastado de la casa por moneda más una lista de "cuánto pagó cada
miembro" — sin deuda, sin transferencias. El formulario "Nuevo gasto"
deja de pedir participantes. Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Al registrar un gasto ya no hay que elegir con quién se reparte —
directamente se carga descripción, importe, categoría y fecha. Balance
muestra, por ejemplo, "Pesos: $500.000 gastados este mes" y debajo
"Administrador aportó $300.000, Pablo aportó $200.000" — sin ninguna
tabla de "le correspondía" ni "debe transferir a".

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un gasto ya no se reparte entre participantes — no existe ningún concepto de "a quién le corresponde qué parte". | Aplica también a cada cuota de un gasto en cuotas y a cada gasto generado por una suscripción o una importación. |
| REQ-002 | `GastoParticipante` se elimina del sistema — modelo, tabla, esquemas de API y formulario. | Se elimina la tabla y su historial por completo (decisión explícita del usuario) — no se conserva como dato histórico. |
| REQ-003 | Balance muestra, por moneda, el total gastado por la casa en el mes. | Mismo criterio de separación por moneda ya existente (`gastos-multi-moneda`) — nunca sumado ni convertido. |
| REQ-004 | Balance muestra también, a modo informativo, cuánto pagó cada miembro ese mes. | Puramente informativo — no es una deuda, no genera ninguna transferencia sugerida. |
| REQ-005 | `pagado_por` se mantiene en cada gasto como dato de registro (quién hizo la compra), sin generar ninguna obligación de reembolso. | Sin cambios estructurales en `pagado_por` — solo deja de alimentar ningún cálculo de deuda. |
| REQ-006 | El dashboard de Inicio refleja el nuevo balance de la casa (total + aportes), sin la tabla de deuda anterior. | Reemplaza la sección "Balance" del dashboard existente. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001/REQ-002) | **Given** un gasto nuevo **When** se registra **Then** no se crea ninguna fila de reparto y la API ya no acepta `participantes` | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** la base de datos **When** corre la migración **Then** la tabla `gasto_participantes` ya no existe | `[INTEGRATION]` |
| TC-003 (REQ-003) | **Given** gastos en ARS y USD en el mes **When** se calcula el balance **Then** devuelve el total gastado de la casa por cada moneda | `[INTEGRATION]` |
| TC-004 (REQ-004) | **Given** varios miembros con gastos ese mes **When** se calcula el balance **Then** devuelve cuánto pagó cada uno, sin ningún campo de "correspondía" ni "balance" | `[INTEGRATION]` |
| TC-005 (REQ-004, control) | **Given** el balance calculado **When** se inspecciona su forma **Then** no expone ninguna transferencia sugerida | `[UNIT]` |
| TC-006 (REQ-005) | **Given** el formulario "Nuevo gasto" **When** se renderiza **Then** no muestra ningún selector de participantes ni "Todos los miembros" | `[UNIT]` |
| TC-007 (REQ-006) | **Given** el dashboard de Inicio **When** se arma **Then** muestra el nuevo total de la casa, sin la tabla de deuda anterior | `[UNIT]` |
| TC-008 (REQ-001, control de regresión) | **Given** un gasto en 3 cuotas **When** se registra **Then** se generan las 3 cuotas correctamente, sin ningún reparto por cuota | `[INTEGRATION]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario señaló que Balance está conceptualmente mal — los gastos deben ir al fondo común de la casa, no repartirse como deuda entre personas — 2026-09-16, adjuntando una captura de la pantalla Balance actual. Confirmado vía preguntas de aclaración: Balance = total de la casa + aportes informativos; se elimina GastoParticipante y su historial por completo. |
| Spec | prestamos-entre-miembros | .nybo/plans/prestamos-entre-miembros/spec.md |
