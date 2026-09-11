# Verify — Vista General y Actividad

## Test Scenarios by Task

### T1 — Data Layer
- Happy: insertar y leer filas de `historial_actividad` ordenadas por fecha.

### T2 — Service Layer
- Happy: `armar_dashboard` sobre una casa vacía no lanza error (TC-002).
- Happy: registrar un gasto dispara una entrada de actividad (TC-003).
- Happy: completar una tarea dispara entradas de actividad para la tarea y los puntos (TC-004).
- Happy: `obtener_actividad` devuelve orden descendente por fecha (TC-005).

### T3 — API Routes
- Contrato: `GET /inicio` devuelve 200 con estructura completa incluso sin datos.

### T4 — UI
- E2E: flujo completo del ejemplo del documento (§19) — crear casa, agregar miembros, registrar gastos, completar tareas, y verificar que la pantalla principal y el historial reflejan todo correctamente (TC-001).

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-002, TC-003, TC-004, TC-005 en verde | `[AUTO]` |
| TC-001 verificado end-to-end contra el ejemplo del documento | `[AUTO]` |
| Revisión visual de la pantalla de inicio | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-002 | `armar_dashboard` | Falta manejar colecciones vacías antes de agregar |
| TC-003/TC-004 | Hooks en `gasto_service`/`tarea_service` | Hook no invocado, o invocado antes de confirmar la transacción |
| TC-005 | `obtener_actividad` | Orden ascendente en vez de descendente |

## End-to-End Verification
1. Ejecutar el ejemplo de uso del documento (§19): crear "Casa Brown", agregar Ana/Juan/Laura, registrar gastos y completar tareas.
2. Abrir la pantalla principal y verificar que muestra miembros, gastos recientes, balance, tareas pendientes/completadas y ranking coherentes con el ejemplo.
3. Abrir el historial de actividad y verificar el orden cronológico descendente con las entradas esperadas.

**Gate final:** TC-001 a TC-005 en verde y los 3 pasos completan sin error.
