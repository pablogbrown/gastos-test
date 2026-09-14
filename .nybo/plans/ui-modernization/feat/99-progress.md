# Progress — Modernización de la UI

## Checklist

### Tasks
- [x] T1 — Design system, tema, shell responsivo y CrearCasa
- [x] T2 — Restyle: Miembros, Gastos, Balance
- [x] T3 — Restyle: Tareas, Ranking, InicioCasa, HistorialActividad
- [x] T4 — Pulido responsivo, adaptación de tests y docs

### Verify
- [x] Verificación end-to-end de la spec (TC-006 verificado por la sesión coordinadora con Chrome real, ver nota)

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Viewport angosto muestra BottomNavigation con 7 secciones
- [x] `[TC-002]` *[UNIT]* — Viewport ancho muestra barra superior, no BottomNavigation
- [x] `[TC-003]` *[UNIT]* — Las 8 pantallas usan componentes MUI, no HTML nativo sin estilo
- [x] `[TC-004]` *[UNIT]* — Los ítems de BottomNavigation cumplen 44px mínimo
- [x] `[TC-005]` *[UNIT]* — La suite de tests existente sigue pasando tras el restyle
- [x] `[TC-006]` *[E2E]* — Sin scroll horizontal en un viewport Android real (360x800) — verificado (ver Completion Summary)

#### Outcome Smoke Test
El `## Outcome` de spec.md fue verificado en vivo por la sesión
coordinadora (no el builder original — este build corrió sin
herramientas de navegador) usando Chrome real vía `mcp__claude-in-chrome`:
un iframe forzado a 360px de ancho, flujo completo crear casa → crear
categoría → registrar un gasto con descripción larga, sin errores de
consola ni scroll horizontal (`document.documentElement.scrollWidth ===
clientWidth`). La `BottomNavigation` se confirmó visible y funcional en
ese ancho.

## Completion Summary
Las 8 pantallas fueron reconstruidas con Material UI (tema único en
`src/frontend/theme.ts`, navegación responsiva extraída a
`src/frontend/AppNav.tsx`). Ningún cliente de API fue modificado.
`npm run build`, `npm run lint` y `npm run test` (31/31) pasan en verde.

TC-006 (E2E, viewport 360×800 en navegador real) fue verificado
posteriormente por la sesión coordinadora (el builder original no tenía
herramientas de navegador disponibles) con Chrome real: sin scroll
horizontal, bottom nav visible y funcional, flujo crear casa → crear
categoría → registrar gasto completado sin errores.

**Hallazgo durante esa verificación, corregido por separado**: al
intentar registrar un gasto con la categoría mal seleccionada, la API
devolvió un 422 de validación (Pydantic) cuyo `detail` es un array de
objetos, no un string — el cliente HTTP lo pasaba tal cual a
`<Alert>{error}</Alert>`, crasheando toda la SPA sin error boundary.
Bug pre-existente (no introducido por esta spec, afecta a los 4
clientes desde `casas-miembros`) — corregido en `main` directamente vía
`/nybo-fix`, PR #9 (`fix/frontend-api-error-detail-array`), no en esta
branch.

**Observación menor, no bloqueante**: en la tabla de historial de
Gastos a 360px, el nombre de categoría en la columna angosta se
envuelve carácter por carácter cuando es largo (ej. "Supermercado y
Verdulería del Barrio Norte") — legible pero no prolijo. Candidato a
un ajuste de `TableCell` (`word-break`/truncado con tooltip) en un
futuro pase de pulido, no crítico para TC-006 (que exige ausencia de
scroll horizontal, no un word-wrap prolijo).

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 6 test cases. |
| 2 | 2026-09-11 | build | T1-T4 | TC-001..TC-005 | MUI restyle de las 8 pantallas; build/lint/test verdes (31/31). TC-006 no verificado con navegador real (sin herramienta disponible en el entorno). |
