# Importar resumen de tarjeta en PDF

## Intention

### What
Subir el PDF del resumen de una tarjeta ya registrada actualiza esa
tarjeta (cierre, vencimiento, saldo) y crea automáticamente los gastos
de cada consumo del resumen — sin ningún paso de revisión o
confirmación — detectando compras en cuotas y suscripciones conocidas
(Netflix, Spotify, Disney+) para vincularlas a los mecanismos ya
existentes en vez de crearlas como gastos sueltos.

### Why
Cargar a mano cada línea de un resumen de 15-20 consumos por mes es
tedioso y propenso a errores; el resumen ya trae toda la información
estructurada.

## Solution
Un parser específico al formato de resumen BBVA Visa Platinum (el
formato de la muestra provista) extrae, del PDF: cierre/vencimiento/
saldo del encabezado, y la tabla "Consumos" (fecha, descripción, cupón,
importe en pesos o dólares). Las líneas de "Impuestos, cargos e
intereses" nunca se leen como consumos. Por cada línea: si el comercio
es un reconocido (Netflix/Spotify/Disney+) se vincula a una Suscripcion
de la casa (existente o nueva); si tiene un patrón de cuota ("C.NN/NN")
se crean solo las cuotas restantes (de la actual a la total), nunca la
serie completa desde cero; el resto se importa como un gasto normal en
la moneda que corresponda. Depende de **`gastos-multi-moneda`**
(moneda) y **`tarjetas-credito`** (la tarjeta a actualizar). Ver
**[Solution Overview](feat/00-overview.md)**.

**Advertencia de alcance**: el parser reconoce específicamente el
formato del PDF de ejemplo (BBVA Visa Platinum). Un resumen de otro
banco, u otro diseño del mismo banco, puede no reconocerse — en ese
caso la importación se rechaza con un error claro (REQ-006), nunca
importa datos a medias.

## Outcome
Pablo sube el PDF de su resumen de septiembre: la tarjeta queda con
vencimiento 07-Sep-26; se crean ~17 gastos (uno por consumo), 3 de ellos
como cuotas restantes de una compra que ya venía en curso, y 3 vinculados
a las suscripciones de Netflix/Spotify/Disney+ ya existentes en la casa.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Subir el PDF de un resumen actualiza cierre/vencimiento/saldo (ARS y USD) de la tarjeta indicada. | La tarjeta debe existir y pertenecer a la casa. |
| REQ-002 | Cada línea de "Consumos" se importa como un gasto en la moneda que corresponda (columna pesos o dólares del PDF). | Un gasto importado queda vinculado a la tarjeta de origen (`tarjeta_id`). |
| REQ-003 | Una línea con patrón de cuota ("C.NN/NN") crea solo las cuotas restantes (de la actual a la total), una por mes consecutivo desde la fecha del resumen. | El importe de cada cuota restante es el que figura en esa línea (ya es el monto mensual, no el total de la compra). |
| REQ-004 | Una línea de un comercio reconocido (Netflix, Spotify, Disney+) se vincula a una Suscripcion activa existente con esa descripción, o crea una nueva si no existe. | Crear una Suscripcion nueva requiere que quien importa sea Administrador — si no lo es, esa línea se importa como gasto suelto (degradación, no bloquea el resto). |
| REQ-005 | Las líneas de "Impuestos, cargos e intereses" nunca generan gastos. | Son cargos administrativos, no consumos del titular. |
| REQ-006 | Un PDF sin el formato reconocido es rechazado con un error claro, sin crear ningún gasto. | Todo o nada — nunca una importación parcial ante un formato no reconocido. |
| REQ-007 | La importación no pide confirmación — los gastos quedan creados de inmediato al subir el PDF. | Flujo decidido explícitamente por el usuario (sin paso de revisión). |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** el PDF de ejemplo **When** se importa contra una tarjeta existente **Then** la tarjeta queda con el cierre/vencimiento/saldo del resumen | `[INTEGRATION]` |
| TC-002 (REQ-002) | **Given** una línea en pesos **When** se importa **Then** se crea un gasto en ARS con esa fecha e importe | `[INTEGRATION]` |
| TC-003 (REQ-002) | **Given** una línea en dólares sin ser suscripción ni cuota **When** se importa **Then** se crea un gasto en USD | `[INTEGRATION]` |
| TC-004 (REQ-003) | **Given** una línea "C.04/06" con importe $X **When** se importa **Then** se crean exactamente 3 gastos (4/6, 5/6, 6/6) de $X, en meses consecutivos desde la fecha del resumen | `[INTEGRATION]` |
| TC-005 (REQ-004) | **Given** una línea "NETFLIX.COM" sin suscripción previa, actor Administrador **When** se importa **Then** se crea una Suscripcion nueva y el gasto queda vinculado a ella | `[INTEGRATION]` |
| TC-006 (REQ-004) | **Given** la misma línea con una Suscripcion "NETFLIX.COM" ya activa **When** se importa **Then** el gasto se vincula a la existente, sin crear una segunda | `[INTEGRATION]` |
| TC-007 (REQ-004) | **Given** una línea de suscripción nueva, actor no Administrador **When** se importa **Then** se crea como gasto suelto (sin `suscripcion_id`), sin fallar el resto de la importación | `[INTEGRATION]` |
| TC-008 (REQ-005) | **Given** una línea "COMISION PLATINUM" **When** se importa **Then** no se crea ningún gasto por esa línea | `[INTEGRATION]` |
| TC-009 (REQ-006) | **Given** un PDF que no es un resumen reconocible **When** se sube **Then** la API responde con error y no se crea ningún gasto | `[INTEGRATION]` |
| TC-010 (REQ-007) | **Given** el botón "Importar resumen" en la pantalla Tarjetas **When** se sube un PDF **Then** se muestra un resumen ("N gastos creados") sin pedir confirmación previa | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | El usuario adjuntó un resumen real (BBVA Visa Platinum) — 2026-09-15. Confirmado vía preguntas de aclaración: importación 100% automática, agregar `pdfplumber` como dependencia, cuotas en curso importan solo lo restante. |
| Spec | gastos-multi-moneda | .nybo/plans/gastos-multi-moneda/spec.md |
| Spec | tarjetas-credito | .nybo/plans/tarjetas-credito/spec.md |
