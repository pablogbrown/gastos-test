# Multi-moneda en gastos, cuotas y suscripciones

## Intention

### What
Un gasto, una cuota o una suscripción se pueden registrar en pesos (ARS,
default) o dólares (USD). El balance de la casa se calcula y se muestra
por separado para cada moneda — nunca sumadas ni convertidas entre sí —
y las transferencias sugeridas nunca mezclan una moneda con otra.

### Why
Los resúmenes de tarjeta de crédito (próxima feature de importación)
traen consumos en ambas monedas en el mismo resumen. Sin soporte real de
moneda, esos gastos en dólares quedarían mal registrados (como si fueran
pesos) o se descartarían. Esta spec es la base necesaria antes de poder
importar un resumen real.

## Solution
`Gasto` y `Suscripcion` ganan una columna `moneda` (`"ARS"` | `"USD"`,
default `"ARS"`). `calcular_balance` agrupa pagos/correspondientes por
`(miembro, moneda)` en vez de solo por miembro: la fila en pesos se
muestra siempre (comportamiento actual, sin cambios), y aparece una fila
en dólares por miembro solo si hubo algún gasto en dólares ese mes en esa
casa — evita una sección de "Dólares" vacía en el 99% de los meses.
`sugerir_transferencias` agrupa internamente por moneda antes de
emparejar deudores con acreedores, así nunca cruza monedas. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Una casa con un gasto de $50.000 y otro de USD 20 el mismo mes ve, en la
pantalla Balance, dos secciones independientes ("Pesos" y "Dólares"),
cada una con su propio total y sus propias transferencias sugeridas —
nunca un monto combinado ni una conversión.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un gasto se registra en `"ARS"` (default) o `"USD"` vía el parámetro/campo `moneda`. | Sin `moneda`, el comportamiento es idéntico al actual (ARS). |
| REQ-002 | El balance de una casa se calcula por separado para cada moneda con actividad ese mes — nunca sumadas ni convertidas. | La sección de una moneda sin ningún gasto ese mes no aparece. |
| REQ-003 | Las transferencias sugeridas nunca emparejan un deudor de una moneda con un acreedor de otra. | Cada transferencia indica en qué moneda es. |
| REQ-004 | Una suscripción se registra en ARS o USD; cada gasto que genera mensualmente hereda esa misma moneda. | La moneda de una suscripción no cambia una vez creada (no hay endpoint de edición hoy). |
| REQ-005 | Un gasto registrado en cuotas mantiene la misma moneda en todas sus cuotas. | La cuota no permite moneda mixta entre partes de una misma compra. |
| REQ-006 | Un valor de `moneda` distinto de `"ARS"`/`"USD"` es rechazado. | Aplica tanto a gastos como a suscripciones. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un gasto con `moneda="USD"` **When** se registra **Then** persiste con `moneda="USD"` | `[INTEGRATION]` |
| TC-002 (REQ-001, control) | **Given** un gasto sin `moneda` **When** se registra **Then** persiste con `moneda="ARS"`, igual que hoy | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** una casa con un gasto en ARS y otro en USD el mismo mes **When** se calcula el balance **Then** hay filas separadas por moneda, cada una sumando solo la suya | `[INTEGRATION]` |
| TC-004 (REQ-002) | **Given** un mes sin ningún gasto en USD **When** se calcula el balance **Then** no hay ninguna fila en USD | `[UNIT]` |
| TC-005 (REQ-003) | **Given** deudores y acreedores en ambas monedas **When** se sugieren transferencias **Then** ninguna transferencia mezcla monedas | `[UNIT]` |
| TC-006 (REQ-004) | **Given** una suscripción con `moneda="USD"` **When** se genera su gasto mensual **Then** el gasto generado tiene `moneda="USD"` | `[INTEGRATION]` |
| TC-007 (REQ-005) | **Given** un gasto en 3 cuotas con `moneda="USD"` **When** se registra **Then** las 3 cuotas tienen `moneda="USD"` | `[INTEGRATION]` |
| TC-008 (REQ-006) | **Given** un gasto con `moneda="EUR"` **When** se registra **Then** la API responde 400 | `[INTEGRATION]` |
| TC-009 (REQ-001) | **Given** el formulario "Nuevo gasto" con Moneda en "USD" **When** se envía **Then** el body incluye `moneda: "USD"` | `[UNIT]` |
| TC-010 (REQ-002) | **Given** la pantalla Balance con actividad en ambas monedas **When** carga **Then** se renderizan dos secciones separadas sin ningún total combinado | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió poder importar resúmenes de tarjeta de crédito (que traen consumos en ARS y USD) — 2026-09-15. Confirmado vía preguntas de aclaración: soporte real de multi-moneda, balance siempre separado (nunca convertido). |
