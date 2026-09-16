# Préstamos entre miembros

## Intention

### What
Un miembro puede registrar que le prestó dinero a otro miembro de la
casa — quién presta, a quién, cuánto, en qué moneda, con una fecha y una
descripción opcional. El préstamo nace "pendiente" y se puede marcar
"pagado" con un clic. Vive en su propia pantalla, separada de Gastos y
Balance.

### Why
Es la única relación de deuda real que debe existir entre dos personas
(spec `gastos-sin-reparto` elimina toda deuda derivada de gastos
compartidos) — un préstamo es una decisión explícita de dos personas,
no algo que el sistema deba inferir repartiendo un gasto.

## Solution
Nueva entidad `Prestamo` (prestamista, deudor, importe, moneda, fecha,
descripción opcional, estado). Un servicio propio (`prestamo_service.py`,
mismo patrón que `tarjeta_service.py`) con alta/listado/cambio de
estado. Nunca interactúa con `Gasto`/`GastoParticipante`/
`balance_service` — es un registro completamente aparte, sin ningún
cálculo derivado ni transferencia sugerida (el préstamo en sí ya es la
transferencia). Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Pablo le presta $50.000 a Maca para pagar el alquiler del auto: lo
registra en "Préstamos" con estado "Pendiente". Cuando Maca se lo
devuelve, un clic lo marca "Pagado" — sin que esto haya tocado nunca
Gastos ni Balance.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un miembro puede registrar un préstamo indicando quién presta, a quién, cuánto, moneda y fecha (descripción opcional). | Ambos miembros deben pertenecer a la casa. |
| REQ-002 | Un préstamo no puede registrarse de un miembro a sí mismo. | `prestamista_id` y `deudor_id` deben ser distintos. |
| REQ-003 | Un préstamo nace en estado "pendiente"; se puede cambiar a "pagado" y viceversa en cualquier momento. | Cualquier miembro activo de la casa puede cambiar el estado — mismo nivel de permiso que registrar un gasto. |
| REQ-004 | Los préstamos se listan en una pantalla propia ("Préstamos"), separada de Gastos y Balance. | Ordenados por fecha descendente. |
| REQ-005 | Un préstamo no afecta ningún cálculo de Balance de la casa. | Son conceptos completamente independientes — `balance_service.py` no se toca en esta spec. |
| REQ-006 | Un valor de `moneda`/`estado` fuera de los valores válidos es rechazado. | Mismos valores de moneda que ya usa Gasto (`"ARS"`/`"USD"`); estado `"pendiente"`/`"pagado"`. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** datos válidos de préstamo **When** se registra **Then** persiste con `estado="pendiente"` | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** `prestamista_id == deudor_id` **When** se registra **Then** la API responde 400 | `[INTEGRATION]` |
| TC-003 (REQ-006) | **Given** una `moneda` inválida **When** se registra **Then** la API responde 400 | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** un préstamo "pendiente" **When** se actualiza su estado a "pagado" **Then** el cambio persiste, y viceversa | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** varios préstamos de una casa **When** se listan **Then** se devuelven ordenados por fecha descendente | `[INTEGRATION]` |
| TC-006 (REQ-005, control) | **Given** un préstamo recién creado o actualizado **When** se calcula el Balance de la casa **Then** los totales no cambian | `[INTEGRATION]` |
| TC-007 (REQ-001) | **Given** la pantalla "Préstamos" con el formulario completo **When** se envía **Then** se llama a la API con los datos correctos y el préstamo aparece en el listado | `[UNIT]` |
| TC-008 (REQ-003) | **Given** un préstamo "Pendiente" en el listado **When** se hace clic en su chip de estado **Then** cambia a "Pagado" | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió separar las deudas entre personas (préstamos) de los gastos de la casa — 2026-09-16. Confirmado vía preguntas de aclaración: registro simple pagado/pendiente, sin pagos parciales. |
| Spec | gastos-sin-reparto | .nybo/plans/gastos-sin-reparto/spec.md |
