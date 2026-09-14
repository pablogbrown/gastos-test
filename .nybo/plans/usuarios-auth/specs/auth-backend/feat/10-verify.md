# Verify — Autenticación Backend

## Test Scenarios by Task

### T1 — Data Layer
- Happy: crear un Usuario válido.
- Edge: dos Usuarios con el mismo email → falla por constraint.

### T2 — Service Layer
- Happy: `registrar_usuario` hashea la contraseña (TC-001).
- Error: email duplicado → rechazado (TC-002).
- Happy: `autenticar_usuario` + `emitir_token` con credenciales correctas (TC-003).
- Error: credenciales incorrectas → mismo mensaje que "no existe" (TC-004).

### T3 — API Routes
- Error: sin JWT o JWT inválido → 401 en cualquier ruta migrada (TC-005).
- Happy: JWT válido → comportamiento equivalente al `X-Usuario-Id` anterior (TC-006).
- Error: Usuario autenticado pero no miembro de la Casa → 403 (TC-009).

### T4 — Multi-casa linking
- Happy: un Usuario crea 2 casas, tiene 2 Miembros con el mismo `usuario_id` (TC-007).
- Happy: agregar miembro por email de un Usuario existente lo vincula correctamente (TC-008).
- Happy: `GET /casas/mias` devuelve exactamente las casas donde el usuario tiene Miembro activo, ninguna otra (TC-010).

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-001 a TC-010 en verde | `[AUTO]` |
| Ninguna contraseña aparece en texto plano en respuestas ni logs | `[AUTO]` |
| Las 4 rutas existentes (casas/gastos/tareas/dashboard) ya no aceptan `X-Usuario-Id` | `[AUTO]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-002 | Constraint único en `usuarios.email` | Falta índice único en la migración |
| TC-004 | `autenticar_usuario` | Mensajes de error distintos revelan si el email existe |
| TC-005/TC-006 | `get_current_usuario` | Dependency no reemplazó el header viejo en algún router |
| TC-007/TC-008 | `crear_casa`/`agregar_miembro` | `usuario_id` no se está persistiendo en el Miembro creado |
| TC-009 | `requiere_membresia_activa` | No se está resolviendo el Miembro correcto para el `usuario_id` del token |

## End-to-End Verification
1. `POST /auth/registro` con un email nuevo → 201.
2. `POST /auth/login` con esas credenciales → 200, JWT recibido.
3. `POST /casas` con el JWT → 201, el Miembro admin queda vinculado al `usuario_id`.
4. Repetir 1-3 con un segundo email, agregar el primer Usuario como miembro de la segunda casa por su email → el mismo `usuario_id` ahora tiene 2 Miembros.
5. Intentar `GET /casas/{id-de-la-segunda-casa}/...` con el JWT del primer login antes de agregarlo como miembro → 403; después de agregarlo → 200.
6. Cualquier request sin `Authorization` a una ruta migrada → 401.

**Gate final:** TC-001 a TC-010 en verde y los 6 pasos completan sin error.
