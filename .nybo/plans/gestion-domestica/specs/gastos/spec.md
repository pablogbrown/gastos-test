# Gestión de Gastos

## Intention

### What
Permite a los miembros de una casa registrar gastos compartidos, definir quién participa de cada uno, y consultar cuánto pagó y cuánto le corresponde pagar a cada persona.

### Why
Compartir una vivienda implica gastos comunes; sin un registro y un balance claro, resolver "quién le debe a quién" se vuelve una fuente constante de fricción entre convivientes.

## Solution
Un modelo Gasto asociado a una o varias participaciones (Miembro + monto correspondiente), agrupado en categorías administrables. El balance por miembro se calcula agregando lo pagado contra lo que le correspondía, y el sistema sugiere transferencias para saldar cuentas.
See **[Solution Overview](feat/00-overview.md)** for the full architecture, data model, contracts, and UX/UI.

## Outcome
Cualquier miembro puede registrar un gasto en segundos, ver de inmediato cómo queda el balance de la casa, y saber exactamente cuánto debe transferir (o recibir) para quedar a mano — sin perder el historial cuando cambian los miembros de la casa.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Un miembro debe poder registrar un gasto indicando descripción, importe, fecha, persona que lo realizó y categoría. | Debe existir al menos una categoría asignada al gasto entre las predefinidas (Supermercado, Servicios, Alquiler, Limpieza, Mantenimiento, Mascotas, Comida, Otros). |
| REQ-002 | El administrador debe poder gestionar el catálogo de categorías de gasto disponibles para la casa. | Solo el rol Administrador puede crear o modificar categorías. |
| REQ-003 | Un gasto debe poder corresponder a todos los miembros activos de la casa o solo a un subconjunto explícito. | Si no se seleccionan participantes, el gasto aplica por defecto a todos los miembros activos al momento del registro. |
| REQ-004 | Cuando un gasto tiene más de un participante, el sistema debe dividir el importe en partes iguales entre ellos. | La suma de las partes debe coincidir exactamente con el importe total, ajustando el redondeo en el último participante si corresponde. |
| REQ-005 | El sistema debe calcular, por miembro, cuánto pagó y cuánto le correspondía pagar, y mostrar el balance resultante. | balance = total pagado − total correspondiente; positivo indica dinero a favor, negativo indica dinero pendiente. |
| REQ-006 | El sistema debe indicar cuánto debería transferir cada miembro con balance negativo para equilibrar las cuentas. | Se resuelve con un algoritmo de compensación simple (mayor deudor con mayor acreedor); no se optimiza el número mínimo de transferencias — asunción, no especificada en el documento fuente. |
| REQ-007 | Los gastos ya registrados no deben recalcularse ni modificarse automáticamente cuando se agreguen nuevos miembros a la casa. | El balance de un gasto se calcula sobre los participantes vigentes al momento de su registro, no sobre la membresía actual. |
| REQ-008 | El sistema debe mantener un historial de gastos consultable por cualquier miembro, ordenado por fecha. | El historial debe incluir gastos de miembros ya desactivados. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** un miembro activo **When** registra un gasto con descripción, importe, fecha y categoría válidos **Then** el gasto se guarda asociado a quien lo pagó | `[UNIT]` |
| TC-002 (REQ-001) | **Given** un miembro activo **When** intenta registrar un gasto sin categoría **Then** el sistema rechaza la operación | `[UNIT]` |
| TC-003 (REQ-002) | **Given** un miembro sin rol admin **When** intenta crear una nueva categoría **Then** el sistema rechaza la operación | `[UNIT]` |
| TC-004 (REQ-003) | **Given** una casa con 4 miembros activos **When** se registra un gasto sin especificar participantes **Then** el gasto se divide entre los 4 miembros activos | `[UNIT]` |
| TC-005 (REQ-003) | **Given** una casa con 4 miembros **When** se registra un gasto especificando solo a 2 como participantes **Then** únicamente esos 2 son responsables del gasto | `[UNIT]` |
| TC-006 (REQ-004) | **Given** un gasto de $40.000 con 4 participantes **When** se calcula la división **Then** cada participante debe exactamente $10.000 | `[UNIT]` |
| TC-007 (REQ-005) | **Given** los gastos del ejemplo del documento (Pablo pagó $80.000, Ana pagó $20.000, correspondía $50.000 c/u) **When** se calcula el balance **Then** Pablo queda en +$30.000 y Ana en −$30.000 | `[UNIT]` |
| TC-008 (REQ-006) | **Given** un balance con un deudor y un acreedor **When** se calculan las transferencias sugeridas **Then** el sistema indica el monto exacto que el deudor debe transferir al acreedor | `[UNIT]` |
| TC-009 (REQ-007) | **Given** un gasto ya registrado con 2 participantes **When** se agrega un nuevo miembro a la casa **Then** el gasto y su división original no cambian | `[INTEGRATION]` |
| TC-010 (REQ-008) | **Given** una casa con gastos de un miembro ya desactivado **When** se consulta el historial de gastos **Then** esos gastos siguen apareciendo | `[INTEGRATION]` |

## Sources

| Type | Reference | Location |
|---|---|---|
| Doc | Aplicación de Gestión Doméstica — Especificación Funcional | Aplicación de Gestión Doméstica — Especificación Funcional.md (§5-7, §18) |
| Spec | casas-miembros | .nybo/plans/gestion-domestica/specs/casas-miembros/spec.md |
