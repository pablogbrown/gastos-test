# Spec: resumen-tarjeta-pago

## Feature
resumen-tarjeta-pago

### What
Cada resumen de tarjeta importado (PDF) queda registrado como un objeto
propio, vinculado a los gastos que generó. Importar dos veces el mismo
resumen (misma tarjeta + mismo cierre) se rechaza. Una nueva acción
"pagar resumen" marca de una sola vez ese resumen y todos sus gastos
como pagados.

### Why
Reportado en vivo por el usuario sobre la spec `importar-resumen-
tarjeta` ya shippeada: hoy nada impide volver a subir el mismo PDF
(duplicando gastos), no hay forma de auditar qué se importó y cuándo, y
marcar cada gasto de un resumen como pagado uno por uno es tedioso —
el usuario pidió explícitamente poder "pagar el resumen" completo.

## Solution
Nueva entidad `ResumenTarjeta` (una fila por importación exitosa:
tarjeta, fechas de cierre/vencimiento, saldos, cantidad de gastos,
estado pendiente/pagado). `importar_resumen` rechaza una segunda
importación con la misma tarjeta y fecha de cierre antes de escribir
nada, y vincula cada `Gasto` que crea (directo, en cuotas, o vía
suscripción) al `ResumenTarjeta` recién creado mediante `Gasto.
resumen_id`. Un nuevo `pagar_resumen` marca el resumen y todos sus
gastos vinculados como `"pagado"` en una sola operación. La pantalla
Tarjetas lista los resúmenes importados de cada tarjeta con su estado y
un botón "Pagar resumen" cuando está pendiente.

## Requirements

- REQ-001: Al importar un resumen exitosamente, queda registrado un
  `ResumenTarjeta` (tarjeta, fecha de cierre, fecha de vencimiento,
  saldos, cantidad de gastos creados, fecha de importación, estado
  inicial "pendiente").
- REQ-002: No se puede importar dos veces un resumen con la misma
  tarjeta y la misma fecha de cierre — la segunda vez se rechaza sin
  crear ningún gasto ni modificar la tarjeta.
- REQ-003: Cada gasto creado por una importación (directo, cuota
  restante, o vía suscripción detectada) queda vinculado al
  `ResumenTarjeta` que lo generó.
- REQ-004: Se puede "pagar" un resumen — todos sus gastos vinculados
  pasan a `estado="pagado"` y el resumen mismo queda `"pagado"`, en una
  sola acción.
- REQ-005: Los resúmenes ya importados de una tarjeta se pueden
  consultar (fecha de cierre/vencimiento, estado, cantidad de gastos) —
  control y auditoría.

## Test Cases

- TC-001 (REQ-001): importar un resumen crea un `ResumenTarjeta` con
  los datos correctos y estado `"pendiente"`.
- TC-002 (REQ-002): importar el mismo PDF (misma tarjeta, mismo
  cierre) una segunda vez responde 409 y no crea gastos ni cuotas
  adicionales.
- TC-003 (REQ-003): cada gasto creado por la importación (directo, en
  cuotas, y vía suscripción detectada) tiene `resumen_id` igual al del
  `ResumenTarjeta` creado en esa misma importación.
- TC-004 (REQ-004): pagar un resumen pasa todos sus gastos vinculados a
  `"pagado"` y el resumen mismo a `"pagado"`.
- TC-005 (REQ-004): pagar un resumen no afecta gastos de otro resumen
  ni de otra tarjeta, ni permite pagar un resumen ya pagado dos veces.
- TC-006 (REQ-005): listar los resúmenes de una tarjeta devuelve todos
  los importados, ordenados del más reciente al más antiguo, con su
  estado.
- TC-007 (REQ-001/REQ-005, frontend): la pantalla Tarjetas muestra, por
  cada tarjeta, la lista de resúmenes importados con su estado y un
  botón "Pagar resumen" visible solo cuando está pendiente.
- TC-008 (REQ-002, frontend): al intentar importar un resumen
  duplicado, la pantalla muestra el mensaje de error claro devuelto por
  la API (no un 422 de forma genérica).

## Dependencies
- Depende de `importar-resumen-tarjeta` (ya shippeada) y `tarjetas-
  credito` (ya shippeada).

## Out of Scope
- Deshacer/anular un resumen ya importado.
- Editar manualmente un `ResumenTarjeta` después de creado.
- Pago parcial de un resumen (solo todo-o-nada).
