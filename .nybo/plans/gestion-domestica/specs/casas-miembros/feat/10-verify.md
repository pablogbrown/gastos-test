# Verify — Casas y Miembros

## Test Scenarios by Task

### T1 — Data Layer
- Happy path: crear fila Casa y Miembro válidas.
- Edge: dos miembros con misma identificación en la misma casa → debe fallar por constraint (TC-004).
- Edge: mismos identificacion en casas distintas → debe permitirse (TC-009).

### T2 — Service Layer
- Happy: `crear_casa` crea Casa + Miembro admin (TC-001).
- Error: `crear_casa` con nombre vacío → ValidationError (TC-002).
- Happy: `agregar_miembro` por admin (TC-003).
- Error: `agregar_miembro` por actor no-admin → PermissionError (TC-006).
- Error: `agregar_miembro` con identificación duplicada → ValidationError (TC-004).
- Happy: `desactivar_miembro` preserva gastos/tareas asociados (TC-005).
- Error: operación de gasto/tarea para usuario no-miembro → rechazada (TC-008).

### T3 — API Routes
- Contrato: cada ruta devuelve el status code esperado por rol (TC-006, TC-007).

### T4 — UI
- Manual/exploratorio: flujo completo crear casa → agregar miembro → desactivar miembro.

## Gate Criteria
| Criterio | Tag |
|---|---|
| Todas las TC-001..TC-009 en verde | `[AUTO]` |
| Constraint de unicidad (casa_id, identificacion) verificado en BD | `[AUTO]` |
| Revisión visual de la UI de miembros | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-004 | Constraint único en migración | Falta índice compuesto (casa_id, identificacion) |
| TC-005 | Query de desactivación | Borrado físico en vez de flag `activo` |
| TC-006/TC-007 | `permisos.puede` | Tabla de permisos mal mapeada a rol |
| TC-008 | Guard `requiere_membresia_activa` | Guard no invocado antes de la operación |

## End-to-End Verification
1. Crear casa "Casa Brown" como usuario nuevo.
2. Confirmar que el creador aparece como Administrador.
3. Agregar miembro "Ana" con identificación "ANA1".
4. Confirmar que un segundo miembro con identificación "ANA1" es rechazado.
5. Desactivar a "Ana" y confirmar que su historial (vacío en este punto) no se borra.
6. Confirmar que un usuario con rol Miembro no puede agregar otro miembro.

**Gate final:** todos los pasos anteriores completan sin error y las TC listadas están en verde.
