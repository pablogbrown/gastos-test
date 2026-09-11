# Progress — Modernización de la UI

## Checklist

### Tasks
- [x] T1 — Design system, tema, shell responsivo y CrearCasa
- [x] T2 — Restyle: Miembros, Gastos, Balance
- [x] T3 — Restyle: Tareas, Ranking, InicioCasa, HistorialActividad
- [x] T4 — Pulido responsivo, adaptación de tests y docs

### Verify
- [x] Verificación end-to-end de la spec (TC-006 solo parcialmente verificado — ver nota)

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Viewport angosto muestra BottomNavigation con 7 secciones
- [x] `[TC-002]` *[UNIT]* — Viewport ancho muestra barra superior, no BottomNavigation
- [x] `[TC-003]` *[UNIT]* — Las 8 pantallas usan componentes MUI, no HTML nativo sin estilo
- [x] `[TC-004]` *[UNIT]* — Los ítems de BottomNavigation cumplen 44px mínimo
- [x] `[TC-005]` *[UNIT]* — La suite de tests existente sigue pasando tras el restyle
- [ ] `[TC-006]` *[E2E]* — Sin scroll horizontal en un viewport Android real (360x800) — **no verificado con navegador real** (ver Completion Summary)

#### Outcome Smoke Test
El `## Outcome` de spec.md ("cualquier persona abre taskia desde su
celular Android y la usa con la misma fluidez que una app nativa...")
**no fue observado en vivo en un navegador real** durante este ciclo —
este sandbox no tiene Playwright/Chromium ni otra herramienta de
automatización de navegador disponible. En su lugar se corrió un smoke
check parcial: `vite` (servidor de dev) sirviendo `index.html` y
transformando `main.tsx` → `App.tsx` → `theme.ts` sin errores de
compilación/import (confirma que la app arranca), más una revisión
manual de CSS responsivo en las 8 pantallas. Esto demuestra que la app
compila y sirve correctamente, pero **no** que la experiencia a 360×800
sea fluida sin scroll horizontal — ese nivel de la verificación
(TC-006) queda pendiente para un humano o una sesión con herramientas
de navegador reales.

## Completion Summary
Las 8 pantallas fueron reconstruidas con Material UI (tema único en
`src/frontend/theme.ts`, navegación responsiva extraída a
`src/frontend/AppNav.tsx`). Ningún cliente de API fue modificado.
`npm run build`, `npm run lint` y `npm run test` (31/31) pasan en verde.

TC-006 (E2E, viewport 360×800 en navegador real) **no pudo observarse
directamente**: este entorno no tiene Playwright/Chromium ni otra
herramienta de automatización de navegador instalada, y no se instaló
un navegador nuevo dado el alcance de la tarea. Como mitigación se hizo:
(1) revisión manual de CSS responsivo en las 8 pantallas (flex-wrap en
formularios, `TableContainer` con scroll horizontal contenido a las
tablas en vez de a la página, grid de una columna en mobile para
Inicio, `BottomNavigation` fija con `left:0;right:0`); (2) smoke test
del servidor de dev (`vite`) sirviendo el shell y compilando el grafo
de módulos sin errores. Esto NO reemplaza una verificación visual real
a 360×800 — queda pendiente para un humano o una sesión con
herramientas de navegador reales.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 6 test cases. |
| 2 | 2026-09-11 | build | T1-T4 | TC-001..TC-005 | MUI restyle de las 8 pantallas; build/lint/test verdes (31/31). TC-006 no verificado con navegador real (sin herramienta disponible en el entorno). |
