# Balance filtrable por mes

## Intention

### What
El Balance de una casa (`calcular_balance`) suma todos los gastos desde
siempre — no existe ningún concepto de "mes" en balance ni en el
dashboard. Se agrega la posibilidad de consultar el balance de un mes
puntual, con el mes actual como valor por defecto.

### Why
Es la base necesaria para que un gasto con fecha futura (cuotas,
suscripciones) tenga sentido como "pendiente para más adelante": sin
esto, cualquier gasto futuro sumaría de inmediato a la deuda total, sin
importar cuándo corresponde realmente pagarlo.

## Solution
`calcular_balance(casa_id, mes=None)` filtra los gastos considerados por
`Gasto.fecha` dentro del mes indicado (formato `YYYY-MM`); sin `mes`,
usa el mes calendario actual. La ruta `GET /casas/{id}/balance` expone
un query param `mes` opcional. `Balance.tsx` agrega un selector de mes,
con el actual preseleccionado. Ver **[Solution Overview](feat/00-overview.md)**.

## Outcome
Un miembro puede ver cuánto se debe en un mes puntual (por defecto, el
actual) en vez de un total acumulado desde el inicio de la casa. Un
gasto con fecha de un mes futuro no afecta el balance hasta que ese mes
sea el que se está consultando.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Consultar el balance sin especificar mes devuelve el balance del mes calendario actual (según la fecha del servidor). | Cambio de comportamiento respecto a hoy — antes el balance sumaba todo el historial. |
| REQ-002 | Consultar el balance especificando un mes (`YYYY-MM`) solo considera los gastos cuya `fecha` cae en ese mes. | Aplica tanto a los montos pagados como a los montos correspondientes de cada miembro — ambos lados del cálculo se filtran igual. |
| REQ-003 | Un valor de `mes` con formato inválido es rechazado con un error claro. | Formato esperado: `YYYY-MM` (ej. `2026-09`). |
| REQ-004 | La pantalla Balance permite elegir qué mes consultar, con el mes actual preseleccionado. | Cambiar el mes vuelve a consultar el balance para ese mes — no recalcula nada en el cliente. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** una casa con un gasto de este mes y otro de un mes anterior **When** se consulta el balance sin indicar mes **Then** solo el gasto de este mes está reflejado | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** una casa con gastos en agosto y en septiembre **When** se consulta el balance con `mes=2026-08` **Then** solo los gastos de agosto están reflejados | `[INTEGRATION]` |
| TC-003 (REQ-003) | **Given** una casa existente **When** se consulta el balance con `mes=fecha-invalida` **Then** la API responde 400 | `[INTEGRATION]` |
| TC-004 (REQ-004) | **Given** la pantalla Balance recién cargada **When** se renderiza **Then** el selector de mes muestra el mes actual preseleccionado | `[UNIT]` |
| TC-005 (REQ-004) | **Given** la pantalla Balance **When** el usuario elige un mes distinto en el selector **Then** se dispara una nueva consulta al backend con ese mes | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | Descubierto durante el planning de "gastos en cuotas": el balance no filtraba por fecha, lo que rompía la semántica de "cuota pendiente para más adelante" pedida por el usuario — 2026-09-15. Confirmado vía pregunta de aclaración: agregar filtro por mes, default = mes actual. |
