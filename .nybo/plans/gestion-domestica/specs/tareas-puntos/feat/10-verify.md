# Verify — Gestión de Tareas y Puntos

## Test Scenarios by Task

### T1 — Data Layer
- Happy: tarea creada con estado por defecto `pendiente` (TC-003).

### T2 — Service Layer
- Happy: `crear_tarea` con nombre y puntos válidos (TC-001).
- Error: `crear_tarea` sin nombre → rechazado (TC-002).
- Happy: tarea sin responsable completada por cualquier miembro activo (TC-004).
- Happy: `completar_tarea` registra quién, cuándo y otorga puntos (TC-005).
- Error: completar una tarea ya completada no otorga puntos adicionales (TC-006).
- Happy: puntos acumulados de un miembro suman correctamente (TC-007).
- Happy: ranking ordenado descendente por puntos (TC-008).
- Edge: tarea recurrente completada genera nueva instancia pendiente (TC-009).
- Edge: historial conserva registros de miembros desactivados (TC-010).

### T3 — API Routes
- Contrato: 409 al intentar completar una tarea ya completada.

### T4 — UI
- Manual/exploratorio: flujo completo crear → completar → ranking → historial.

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-001 a TC-010 en verde | `[AUTO]` |
| Ninguna tarea otorga puntos más de una vez por finalización | `[AUTO]` |
| Revisión visual de Tareas/Ranking | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-006 | Guard de estado en `completar_tarea` | Falta validar estado actual antes de insertar historial |
| TC-008 | `calcular_ranking` | Orden ascendente en vez de descendente, o exclusión indebida de miembros inactivos |
| TC-009 | `procesar_recurrencia` | No se invoca tras `completar_tarea`, o frecuencia mal interpretada |
| TC-010 | Query de historial | Join excluye miembros con `activo=false` |

## End-to-End Verification
1. Crear tarea "Limpiar baño" con 10 puntos, sin responsable.
2. Un miembro cualquiera la marca como completada.
3. Verificar que el miembro sumó 10 puntos y aparece en el ranking.
4. Crear tarea recurrente "Sacar la basura" (diaria), completarla y verificar que se genera una nueva instancia pendiente.
5. Desactivar al miembro que completó tareas y confirmar que el historial no cambia.

**Gate final:** TC-001 a TC-010 en verde y los 5 pasos completan sin error.
