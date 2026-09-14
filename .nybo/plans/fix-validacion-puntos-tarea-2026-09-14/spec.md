# Fix — Crear tarea sin puntos crea una tarea de 0 puntos en vez de fallar

## Intention

### What
El formulario "Crear tarea" envía `puntos: Number(puntos)` siempre —
si el campo está vacío, `Number("")` es `0`, un entero no-negativo
válido. La regla de negocio de `crear_tarea`
(`"La cantidad de puntos es obligatoria y debe ser un entero no
negativo"`) nunca se dispara: el campo vacío no es lo mismo que ausente.

### Why
`puntos` es intencionalmente `Optional` a nivel de esquema (comentario
en `src/api/schemas.py`) precisamente para que su ausencia dispare esta
validación de negocio (400) en vez de un 422 genérico de Pydantic — el
frontend rompe esa intención al convertir "vacío" en "cero" antes de
enviarlo, dejando crear tareas de 0 puntos silenciosamente.

## Solution
`Tareas.tsx` envía `puntos: undefined` cuando el campo está vacío (en
vez de `Number("")`), dejando que la validación de negocio ya existente
en el backend se dispare como está diseñada. Ver
**[Solution Overview](feat/00-overview.md)**.

## Outcome
Enviar el formulario "Crear tarea" sin completar Puntos muestra el error
"La cantidad de puntos es obligatoria y debe ser un entero no negativo."
en vez de crear silenciosamente una tarea de 0 puntos.

## Requirements

| ID | Requirement | Business Rules |
|---|---|---|
| REQ-001 | Cuando el campo Puntos del formulario "Crear tarea" está vacío al enviar, el sistema muestra el error de validación de negocio en vez de crear la tarea. | El campo vacío se envía como ausente (`undefined`), nunca como `0` — la distinción "ausente" vs "cero" es la que dispara o no la regla existente en `crear_tarea`. |
| REQ-002 | Completar Puntos con un valor válido (entero ≥ 0) sigue creando la tarea normalmente. | Caso de control — no debe romperse por este fix. |

## Test Cases

| ID | Given/When/Then | Type |
|---|---|---|
| TC-001 (REQ-001) | **Given** el formulario "Crear tarea" con Nombre completo y Puntos vacío **When** se envía **Then** se muestra el mensaje de error "La cantidad de puntos es obligatoria..." y no aparece ninguna tarea nueva en el listado | `[UNIT]` |
| TC-002 (REQ-002) | **Given** el formulario "Crear tarea" con Nombre y Puntos = "5" **When** se envía **Then** la tarea se crea con 5 puntos, igual que hoy | `[UNIT]` |

## Sources

| Type | Reference |
|---|---|
| Session | QA manual profunda del entorno local dockerizado — 2026-09-14. |
