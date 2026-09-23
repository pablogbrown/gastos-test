---
feature: rediseno-ux-ui/specs/pantallas-financieras
schema: build-results/2
cycle: 1
updated: '2026-09-23T13:10:00Z'
exit: ready
verdict: verified
judgment:
  entries: 5
observations:
  entries: 2
tests:
  total: 170
  passed: 170
  failed: 0
---

### Judgment

- **J001** TC-005 ("el encabezado es un `PageHeader` cuyo botón de acción abre el mismo formulario de alta que existe hoy") está redactado en `spec.md` apuntando a la pantalla Suscripciones — pero `Suscripciones.tsx` no tiene, hoy, ningún formulario de alta propio (una suscripción se crea únicamente desde `Gastos.tsx`, tipo de gasto "Suscripción mensual"). Inventar un formulario de alta nuevo en Suscripciones violaría REQ-004 (cero regresión funcional, restyle puramente de presentación) y excede el `files_touched` de T2 en `run-plan.json` (`Tarjetas.tsx`/`Suscripciones.tsx`, no `App.tsx`, que es donde viviría cualquier navegación cruzada a Gastos). Decisión: `Suscripciones`' `PageHeader` se renderiza sin `action` (pantalla sin flujo de alta propio, igual criterio que `Balance` en T1); la verificación de TC-005 se redirige a `Tarjetas.tsx`, que sí tiene un formulario "Nueva tarjeta" preexistente — su `PageHeader` action lo enfoca (ver J002). Decision class: spec-deviation, settleable a nivel semi-autonomous (L2). Registrado también en `decisions.yaml` D001 (no bloqueante).
- **J002** Las 4 pantallas con formulario de alta ya renderizado siempre visible (Gastos, Tarjetas, Préstamos, Mantenimiento, Mantenimiento Autos) nunca lo ocultan/despliegan bajo demanda — "abrir" el formulario desde la acción primaria de `PageHeader` (REQ-003) se implementó como enfocar (`.focus()`) su primer campo, sin ningún cambio de estado ni de comportamiento de envío existente. Se prefirió esto a introducir un mecanismo de mostrar/ocultar el formulario, que sí habría sido un cambio de comportamiento (REQ-004 lo prohíbe). Decision class: spec-deviation, settleable a nivel semi-autonomous.
- **J003** El task file de T1 sugiere usar `StatCard` para los totales de `Balance.tsx`. Se evaluó y se decidió NO usarlo ahí: `StatCard` separa `label`/`value` en dos nodos de texto (`Typography` distintos), lo que rompería la query exacta ya existente `screen.getByText("Total gastado: 500000")` (`Balance.test.tsx`) — prohibido por REQ-004/TC-006 (cero regresión, queries sin modificar). Se mantuvo el texto combinado dentro de un `Card` (solo Paper→Card, visual). Decision class: spec-deviation, settleable a nivel semi-autonomous.
- **J004** El chip "Pendiente de confirmación" de Préstamos usaba `color="default"` (gris neutro), inconsistente con el resto de estados "pendiente" del resto de las pantallas (`a_pagar`/`pendiente` = `warning` en Gastos/Tarjetas). Se corrigió a `color="warning"` — coherente con REQ-001 y con el propio Design Rationale de T3 ("Pendiente de confirmación" → `palette.warning`). Sin test previo lo fijaba en `default`, así que este cambio no rompe ninguna query existente.
- **J005** Se preservó la estructura semántica `<Table>`/`role="table"` en las 7 pantallas (en vez de migrar a una lista de `Card`s como sugiere la Intención de `spec.md`, "tarjetas de línea") porque `Prestamos.test.tsx` depende explícitamente de `screen.getByRole("table", { name: "Listado de préstamos" })` (con `within(tabla)` para desambiguar "Pablo"/"Maca" de los `<option>` del formulario) — cambiar esa estructura habría violado REQ-004/TC-006 en la pantalla con el gate de regresión más estricto de las 7. El lenguaje visual "tarjeta de línea con esquinas redondeadas" se logró restyleando el contenedor (`Paper` → `Card`, que sí recibe el `boxShadow`/`shape.borderRadius` del tema de `sistema-visual`) en las 7 pantallas, preservando el rol `table` y todas las queries por rol/label/texto ya existentes.

### Observations

- Las 4 pantallas con formulario de alta siempre visible repiten el mismo patrón `function enfocar...() { document.getElementById(id)?.focus(); }` — con la spec `pantallas-casa` por delante (mismo patrón compartido de lista+alta), vale la pena evaluar extraer un hook compartido (`useEnfocarCampo` o similar) en una spec futura en vez de que cada pantalla nueva lo reimplemente. [DOMAIN candidate] frontend.md — ver `suggestions.yaml` S001.
- Confirmado en vivo (vía `grep` de `main.tsx`) que `ThemeProvider`/`theme` de `sistema-visual` ya envuelve toda la app en producción — los chips que usan `color="success"/"warning"/"error"` (ya presentes en el código pre-`pantallas-financieras`) heredan automáticamente la paleta semántica nueva sin ningún cambio de código; el trabajo real de REQ-001 en esta spec fue solo la corrección puntual de J004, no una reescritura masiva de colores.

### Verification

- Build: `npm run build` (`tsc --noEmit && vite build`) — verde, sin errores de tipos. Warning preexistente de tamaño de chunk (>500kB), no introducido por esta spec.
- Lint: `npm run lint` (`eslint src/frontend --ext .ts,.tsx`) — verde, 0 warnings/errors.
- Tests: `npm run test` (`vitest run`) — 170/170 passing (25 archivos): 163 preexistentes sin regresión (heredados de `sistema-visual`, incluido) + 7 nuevos en esta spec (2 en `Gastos.test.tsx` TC-001/TC-004, 2 en `Tarjetas.test.tsx` TC-003/TC-005, 2 en `Prestamos.test.tsx` TC-002 + EmptyState, 1 en `Suscripciones.test.tsx` EmptyState).
- Coverage: no disponible — mismo gap ya reportado por `sistema-visual` (`decisions.yaml` D001 de esa spec): no hay proveedor de cobertura instalado (`@vitest/coverage-v8` ausente, `stack.yaml`'s `quality_tools.coverage.tool` es `null`). Instalar uno es decision class `new-dependency`, que SIEMPRE difiere a un humano sin importar el trust level — no se instaló nada. Registrado de nuevo en este ciclo como `decisions.yaml` D002 (mismo item, ámbito de esta spec) para que el checkpoint de `pantallas-financieras` también lo muestre.
- Test cases: TC-001 a TC-006 automatizados (`[UNIT]`/`[INTEGRATION]`) y en verde — ver detalle de redirección de TC-005 en J001.
- Live evidence: NO capturada este ciclo. El checkout principal (`feat/rediseno-ux-ui`) podía estar ocupado por otro build corriendo en simultáneo sobre esta misma spec feature (aviso explícito del dispatch) y levantar un stack Docker propio (backend + DB) para un dev server aislado, como hizo `sistema-visual`, arriesgaba interferir con ese proceso concurrente o consumir puertos ya tomados. Dado que el cambio es 100% frontend de presentación ya cubierto por 170 tests unitarios/integración + build + lint, se prioriza no arriesgar el build concurrente sobre capturar screenshots. Recomendación: correr `/nybo-ui-evidence` sobre este branch una vez que el checkout principal esté libre, antes del checkpoint humano final de `rediseno-ux-ui`.
- Regresión: `git status --short` confirma que solo cambiaron los 7 `src/frontend/pages/*.tsx` listados en `run-plan.json` y sus tests — ningún archivo bajo `src/services/`, `src/api/`, `src/db/`, ni `App.tsx`/`AppNav.tsx`/`theme.ts` (cumple constraint REQ-004).

### Curation

Se extrajeron 2 entradas nuevas a `.nybo/memory/domains/frontend.md`: (1) [FRON-05] cuando se aplica el restyle de `sistema-visual` a una pantalla existente cuyo test suite ya depende de un rol de accesibilidad estructural (`role="table"` en `Prestamos.test.tsx`), preservar esa estructura y restylear solo el contenedor (`Paper` → `Card`) en vez de migrar a una lista de Cards — aplicado en las 7 pantallas por consistencia; (2) [FRONP-05] cuando la acción primaria de `PageHeader` apunta a un formulario ya siempre visible, "abrirlo" es enfocar su primer campo (`.focus()`), nunca introducir un nuevo estado de mostrar/ocultar — y si una pantalla futura necesita un formulario de alta que hoy no existe, eso es una decision class `spec-deviation` propia, no algo para inventar en silencio (ver D001/`Suscripciones.tsx`). `evidence/decisions.yaml` (D001-D003) y `evidence/suggestions.yaml` (S001-S003) quedan con items abiertos para revisión humana — no bloquean este ciclo.
