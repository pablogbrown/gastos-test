# Registrar un gasto en cuotas

## Intention

### What
Al registrar un gasto, se puede indicar que se paga "en cuotas" (una
cantidad de meses). El sistema crea una cuota por mes, cada una por el
importe total dividido en partes iguales, con fecha en el mes que le
corresponde — cada cuota es un gasto real que participa del balance de
su propio mes cuando llega.

### Why
Una compra grande (ej. un electrodoméstico) rara vez se paga de una
sola vez — el caso de uso real de una app de gastos compartidos incluye
poder repartir un gasto en el tiempo, sin que la casa vea de golpe toda
la deuda del total.

## Solution
`registrar_gasto` acepta un nuevo parámetro opcional `cuotas` (entero
≥ 2). Cuando está presente, en vez de crear un solo `Gasto` crea
`cuotas` gastos — mismo `categoria_id`/`pagado_por`/participantes,
importe total dividido en partes iguales (ajustando el redondeo en la
última), fecha incrementada un mes por cuota, y una descripción que
indica "(N/total)". Las `cuotas` generadas comparten un identificador de
grupo. Depende de **`balance-mensual`** para que una cuota futura no
infle el balance de hoy. Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Cargar un gasto de $120.000 en 3 cuotas genera 3 gastos de $40.000, uno
por mes; el balance de este mes solo refleja la cuota de este mes, y las
otras dos aparecen al consultar el balance de sus meses correspondientes.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Al registrar un gasto indicando `cuotas` ≥ 2, el sistema crea esa cantidad de gastos, uno por mes consecutivo empezando en la fecha indicada, cada uno por el importe total dividido en partes iguales. | El ajuste de redondeo (si el total no divide exacto) se aplica en la última cuota, mismo criterio ya usado para dividir un gasto entre participantes. |
| REQ-002 | Cada cuota generada indica en su descripción cuál es (ej. "Heladera (2/3)") y todas comparten un identificador de grupo. | El identificador de grupo permite, en el futuro, listar o filtrar todas las cuotas de una misma compra — no se expone todavía en ninguna pantalla nueva en esta spec. |
| REQ-003 | Un gasto sin `cuotas` (o con `cuotas` ausente/1) se comporta exactamente igual que hoy. | Ningún gasto existente ni ningún gasto nuevo "normal" cambia de comportamiento. |
| REQ-004 | Un valor de `cuotas` menor a 2 pero explícitamente enviado como 0 o negativo es rechazado. | `cuotas` es opcional; su ausencia es válida (equivale a "sin cuotas"), pero un valor inválido si está presente no lo es. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un gasto de $120.000 con `cuotas=3` y fecha 15/09 **When** se registra **Then** se crean 3 gastos de $40.000 con fechas 15/09, 15/10 y 15/11 | `[INTEGRATION]` |
| TC-002 (REQ-001) | **Given** un gasto de $100 con `cuotas=3` **When** se registra **Then** las 3 cuotas suman exactamente $100 (ajuste de redondeo en la última) | `[UNIT]` |
| TC-003 (REQ-002) | **Given** el mismo gasto en cuotas del TC-001 **When** se inspeccionan las 3 filas creadas **Then** comparten el mismo identificador de grupo y sus descripciones terminan en "(1/3)", "(2/3)", "(3/3)" | `[INTEGRATION]` |
| TC-004 (REQ-003, control) | **Given** un gasto sin `cuotas` **When** se registra **Then** se crea un único gasto, igual que hoy | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** un gasto con `cuotas=0` **When** se registra **Then** la API responde 400 | `[INTEGRATION]` |
| TC-006 (REQ-001, integración con balance) | **Given** un gasto de hoy en 3 cuotas **When** se consulta el balance del mes actual y el de dentro de 2 meses **Then** el balance de hoy solo refleja la primera cuota, y el de dentro de 2 meses refleja la tercera | `[INTEGRATION]` |
| TC-007 (REQ-001) | **Given** el formulario "Nuevo gasto" con un campo Cuotas completado con "3" **When** se envía **Then** el body enviado a `registrarGasto` incluye `cuotas: 3` | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario pidió, junto con un bug de "Internal Server Error" al registrar un gasto, que los gastos admitan cuotas o suscripción mensual — 2026-09-15. Confirmado vía preguntas de aclaración: generar las N cuotas de una al cargar; requiere `balance-mensual` para no romper la semántica de "pendiente para más adelante". |
| Spec | balance-mensual | .nybo/plans/balance-mensual/spec.md |
