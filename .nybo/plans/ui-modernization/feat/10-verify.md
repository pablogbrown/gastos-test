# Verify — Modernización de la UI

## Test Scenarios by Task

### T1 — Design system, tema, shell
- Happy: viewport < 600px → `BottomNavigation` visible con 7 secciones (TC-001).
- Happy: viewport ≥ 600px → `AppBar`/tabs visible, no `BottomNavigation` (TC-002).
- Happy: `BottomNavigationAction` cumple 44px mínimo en el tema (TC-004).
- Regression: `CrearCasa` sigue creando una casa real contra la API.

### T2 — Miembros, Gastos, Balance
- Happy: las 3 pantallas usan componentes MUI, no HTML nativo sin estilo (TC-003).
- Regression: los 3 flujos (agregar miembro, registrar gasto, ver balance) siguen funcionando contra la API real.

### T3 — Tareas, Ranking, InicioCasa, HistorialActividad
- Happy: las 4 pantallas usan componentes MUI (TC-003).
- Regression: los 4 flujos (crear/completar tarea, ver ranking, ver inicio, ver actividad) siguen funcionando contra la API real.

### T4 — Pulido y tests
- Happy: la suite completa de frontend pasa tras adaptar selectores (TC-005).
- Happy: en un viewport 360×800 real, sin scroll horizontal ni elementos cortados (TC-006).

## Gate Criteria
| Criterio | Tag |
|---|---|
| TC-001 a TC-005 en verde | `[AUTO]` |
| TC-006 verificado en un navegador real a 360×800 | `[AUTO]` |
| `npm run build`/`npm run lint` limpios | `[AUTO]` |
| Revisión visual subjetiva de "se ve moderno" en las 8 pantallas | `[HUMAN]` |

## Failure Triage
| Si falla | Revisar primero | Patrón de causa raíz probable |
|---|---|---|
| TC-001/TC-002 | `useMediaQuery`/breakpoint en `App.tsx` | Breakpoint mal leído, o el hook no re-renderiza al cambiar el viewport |
| TC-003 | Componentes usados en la pantalla que falla | Quedó un elemento HTML nativo sin migrar a MUI |
| TC-004 | `theme.ts`, overrides de `BottomNavigationAction` | El `sx`/override no se aplicó, o MUI lo sobreescribe con su propio default |
| TC-005 | Selectores de los tests adaptados | Selector sigue apuntando a una clase/tag vieja que MUI ya no usa |
| TC-006 | CSS de layout (flex/grid) de la pantalla específica | Ancho fijo en vez de responsivo, o contenido que no envuelve |

## End-to-End Verification
1. Abrir la app en un viewport de 360×800 (o un dispositivo Android real).
2. Confirmar que la navegación es una bottom tab bar con las 7 secciones.
3. Crear una casa, agregar un miembro, registrar un gasto, ver el balance, crear y completar una tarea, ver el ranking, ver Inicio y Actividad — el mismo flujo ya verificado manualmente antes de esta spec, ahora con la UI nueva.
4. Confirmar que ningún paso requiere scroll horizontal ni zoom para ser legible/clickeable.
5. Achicar el viewport a ≥ 600px y confirmar que la navegación cambia a barra superior.
6. `npm run test` → suite completa en verde. `npm run build` → sin errores.

**Gate final:** TC-001 a TC-006 en verde y los 6 pasos completan sin error.
