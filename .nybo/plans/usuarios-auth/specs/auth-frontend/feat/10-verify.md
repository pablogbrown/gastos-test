# Verify — Autenticación Frontend

## Test Scenarios by Task

### T1 — Login/Registro screens
- Happy: sin JWT guardado, se muestra Login (TC-001).
- Happy: registro válido llama a `POST /auth/registro` y termina en Login (TC-002).

### T2 — Sesión JWT
- Happy: tras login, el header `Authorization: Bearer <jwt>` está en cada request posterior, sin `X-Usuario-Id` (TC-003).
- Edge: una respuesta 401 dispara logout automático y vuelve a Login (TC-004).

### T3 — Selector de casas y shell gate
- Happy: usuario con 2 casas ve el selector y puede elegir una (TC-005).
- Happy: "Cerrar sesión" borra el JWT y vuelve a Login (TC-006).

### T4 — Tests y docs
- Happy: flujo completo registro → login → crear casa → navegar el shell, en un navegador real (TC-007).

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-001 a TC-006 en verde | `[AUTO]` |
| TC-007 verificado end-to-end en un navegador real | `[AUTO]` |
| `npm run build`/`npm run lint`/`npm run test` limpios | `[AUTO]` |
| Revisión visual de Login/Registro/Selector coherente con el tema de `ui-modernization` | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-001 | Lógica de gate en `App.tsx` | No chequea `obtenerToken()` antes de renderizar el shell |
| TC-003 | Los 4 clientes existentes | Alguno sigue enviando `X-Usuario-Id` en vez de `Authorization` |
| TC-004 | Manejo de 401 en los clientes | El 401 no propaga hasta disparar `cerrarSesion()` |
| TC-005 | `GET /casas/mias` (auth-backend) o `SelectorCasas.tsx` | El backend no devuelve las casas esperadas, o el frontend no las renderiza |

## End-to-End Verification
1. Abrir la app sin sesión previa → se muestra Login.
2. Ir a Registro, crear una cuenta nueva → vuelve a Login.
3. Loguearse con esas credenciales → entra (selector de casas, vacío) → crear una casa nueva.
4. Navegar el shell existente (Miembros, Gastos, Tareas, etc.) — mismo comportamiento que antes de esta spec.
5. Cerrar sesión → vuelve a Login.
6. Volver a loguearse → la casa creada en el paso 3 sigue ahí (selector la muestra).

**Gate final:** TC-001 a TC-007 en verde y los 6 pasos completan sin error.
