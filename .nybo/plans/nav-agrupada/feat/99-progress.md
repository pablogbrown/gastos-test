# Progress — Menú superior agrupado por categoría

## Checklist

### Tasks
- [x] T1 — Estructura de grupos + menú desktop desplegable

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Desktop muestra 4 elementos de primer nivel
- [x] `[TC-002]` *[UNIT]* — "Casa" despliega sus 3 pantallas
- [x] `[TC-003]` *[UNIT]* — "Gastos" despliega sus 4 pantallas
- [x] `[TC-004]` *[UNIT]* — Grupo activo aunque no sea la primera pantalla
- [x] `[TC-005]` *[UNIT]* — Mobile sin cambios (control)

#### Outcome Smoke Test
NOT observed — omitido deliberadamente este ciclo. El `## Outcome` de
`spec.md` ("en desktop, el botón 'Gastos' se resalta estando en
Tarjetas; clic en 'Casa' despliega Miembros/Ranking/Actividad") es
observable vía navegador real (docker-compose, `10-verify.md`'s paso de
smoke manual), pero las instrucciones explícitas del build para este
ciclo (`/nybo-build`) indicaron que la verificación de docker/Postgres
quedaba fuera de alcance para esta spec frontend-only — ver Judgment
J003 en `evidence/1/build-results.md`. La misma ruta queda probada de
punta a punta por el suite unitario (render real de `AppNav` + MUI
`Menu` real, sin mockear el componente bajo prueba), no por un fixture
que simule el resultado. Recomendación para un futuro ciclo o para
verificación manual humana: `/nybo-e2e-write nav-agrupada` o correr
`10-verify.md`'s smoke manual una vez.

## Suggestions
- [ ] `[S001]` Dar al botón de nav activo en desktop un resaltado visual más fuerte (background/underline en vez de solo opacity/font-weight)
- [ ] `[S002]` No hay herramienta de coverage configurada para frontend (`stack.yaml` `quality_tools.coverage.tool: null`) — remedio: `/nybo-brownfield-bootstrap --quality`
- [ ] `[S003]` Decidir si el smoke check de docker-compose debería ser una excepción estándar para specs frontend-only, o seguir siendo una decisión explícita por ciclo

## Completion Summary
`GRUPOS_DESKTOP` agrega la agrupación fija (Inicio suelta, Casa =
Miembros/Ranking/Actividad, Gastos = Gastos/Balance/Tarjetas/Suscripciones,
Tareas suelta) en `AppNav.tsx`; la rama desktop reemplaza `<Tabs>` por
botones (`Button`) por entrada `GRUPOS_DESKTOP`, con un `<Menu>` MUI por
grupo reutilizando ícono/label de `SECCIONES` por `value`. El botón de un
grupo se marca `aria-current="true"` cuando `pantalla` pertenece a ese
grupo. `SECCIONES` y la rama mobile (`BottomNavigation`) quedaron
intactas. El TC-002 original de `ui-modernization` en `AppShell.test.tsx`
se actualizó al nuevo contrato (4 elementos de primer nivel + menú); su
TC-001 (mobile) no se tocó. Se detectó y corrigió una regresión no
anticipada por el plan en `tests/unit/frontend/App.test.tsx` (helper
`irAPantallaMiembros` y una aserción de `tablist`), causada por el mismo
cambio de semántica de accesibilidad — ver Judgment J001 en
`evidence/1/build-results.md`. 98/98 tests unitarios frontend en verde,
`npm run build`/`npm run lint` sin errores. Verificación de backend
(pytest)/smoke docker explícitamente fuera de alcance para este ciclo
(spec frontend-only, sin superficie de backend/datos — ver Judgment J003).

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 1 tarea (solo frontend, un archivo), 5 test cases. Independiente de `gastos-estado-pago` y `gastos-vista-mensual`. |
| 2 | 2026-09-16 | build | verified | skipped — frontend-only, sin backend/docker involucrado | T1 implementado (TDD), TC-001..TC-005 en verde, TC-002 de `ui-modernization` migrado al nuevo contrato desktop, regresión en `App.test.tsx` detectada y corregida. `npm run test`/`build`/`lint` en verde. |
