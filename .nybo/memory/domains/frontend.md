# Domain: frontend

frontend domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-11 | feature: ui-modernization | confidence: high | verified: 2026-09-16 -->
- UI is built with Material UI (`@mui/material`, `@mui/icons-material`,
  `@emotion/react`, `@emotion/styled`). One shared theme lives at
  `src/frontend/theme.ts` (exported `theme`, via `createTheme`) — screens
  never define their own ad-hoc palette/typography, they consume this
  theme through `ThemeProvider` (wired once in `main.tsx`).
- The responsive navigation shell (bottom tab bar on mobile < `sm`
  breakpoint / top `AppBar` on desktop) is its own component,
  `src/frontend/AppNav.tsx` — kept separate from `App.tsx` specifically
  so it can be unit-tested (`tests/unit/frontend/AppShell.test.tsx`)
  without needing to drive the full "create a casa" flow first. Mobile
  (`BottomNavigation`) always renders the flat `SECCIONES` array, one
  entry per screen. Desktop (spec `nav-agrupada`, 2026-09-16) no longer
  renders `Tabs` — it renders `GRUPOS_DESKTOP` instead: a standalone
  `Button` per loose screen, and a `Button` + `Menu`/`MenuItem` per
  group, still sourcing every icon/label from `SECCIONES` by `value`
  (never hand-duplicated). A group's button gets `aria-current="true"`
  when the current `pantalla` is any screen in that group, not just its
  first. `SECCIONES` itself is the single source of truth for both
  branches — only `GRUPOS_DESKTOP` decides how desktop presents it.

<!-- added: 2026-09-11 | feature: ui-modernization | confidence: high | verified: 2026-09-11 -->
- Frontend tests query the DOM via accessible roles/labels
  (`getByRole`, `getByLabelText`, `getByText`) rather than CSS classes
  or DOM structure. This convention meant the entire pre-existing test
  suite (Miembros/Gastos/Tareas/InicioCasa/HistorialActividad) needed
  **zero selector changes** when every screen was restyled from plain
  HTML to Material UI components — keep writing tests this way.

<!-- [FRON-01] added: 2026-09-14 | feature: fix-nombres-miembro-ranking-dashboard | confidence: high | verified: 2026-09-14 -->
- [FRON-01] When a screen renders an entity by a foreign id it doesn't
  own directly (e.g. a Miembro's `miembroId`/`miembro_id`), resolve the
  display name via `lista.find((x) => x.id === id)?.nombre ?? id` —
  nullish fallback (`??`, never `||`: an empty name is still a valid,
  non-falsy-in-intent name) to the raw id so a deleted/missing referent
  still renders instead of breaking the row. Established in
  `Gastos.tsx`/`Balance.tsx`; the same helper (`nombreDe`) was added to
  `Ranking.tsx` and `InicioCasa.tsx` (its "Tareas completadas
  recientes" list and its own inline "Ranking" card) — any new screen
  facing the same shape should reuse this, not re-derive it.

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- added: 2026-09-16 | feature: gastos-estado-pago | confidence: medium | verified: 2026-09-16 -->
- [FRONP-01] When a screen has BOTH a `<Select native>` control and a
  clickable display element (e.g. a `Chip`) whose visible labels can
  overlap (e.g. a form's "Estado" selector has an `<option>A pagar
  </option>` while the list below renders a `Chip` with the exact same
  text), a plain `screen.findByText(...)`/`getByText(...)` query is
  ambiguous — native `<option>` elements are always present in the DOM
  (per the existing `<Select native>` convention above), so both match.
  Query the specific element by its ARIA role instead —
  `screen.getByRole("button", { name: "..." })` for a clickable `Chip`
  (MUI renders it with `role="button"` when `onClick` is passed) — never
  assume text alone is unique once a screen has more than one control
  sharing the same label set.

<!-- added: 2026-09-11 | feature: ui-modernization | confidence: medium | verified: 2026-09-11 -->
- When a form needs a `<select>`-like control that existing tests
  assert against with `getByRole("option", ...)`, use MUI's `Select
  native` variant (`<Select native>` rendering real `<option>`
  elements) instead of the default popup `Select` — the popup variant
  only mounts its `MenuItem`s in the DOM once the dropdown is opened
  (via a Portal), which breaks assertions expecting options to always
  be queryable. Still a real MUI component (`FormControl` +
  `InputLabel` + `Select native`), not a bare unstyled `<select>`.

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-11 | feature: ui-modernization | confidence: medium | verified: 2026-09-11 -->
- The installed `@mui/material@9.4.0` type-checks the `Stack` component
  in a way that rejects common props (`alignItems`, `gap`) unless an
  explicit `component` prop is also passed — looked like a local
  type-resolution issue rather than an intentional API change. Worked
  around by using `Box` + `sx={{ display: "flex", ... }}` instead of
  `Stack` everywhere. Worth a closer look (dependency dedupe, or
  confirming this is really this MUI major's API) before relying on
  `Stack` again.

<!-- added: 2026-09-16 | feature: nav-agrupada | confidence: high | verified: 2026-09-16 -->
- Same MUI v9.4.0 deprecated-prop pattern as the `Stack` gotcha above,
  seen again on `Menu`: the legacy `MenuListProps` prop is deprecated in
  this major and silently leaks onto the rendered DOM node as an
  unrecognized attribute (a console warning, not a type error or a
  runtime crash) instead of configuring the menu list. Use the slots API
  instead — `slotProps={{ list: { "aria-labelledby": ... } }}`. Likely a
  repo-wide pattern with this MUI major: prefer `slotProps` over any
  legacy `XxxProps` prop on components that expose slots, and watch test
  output for this exact warning shape as the tell.

<!-- added: 2026-09-14 | feature: usuarios-auth (auth-frontend) | confidence: high | verified: 2026-09-14 -->
- Node >= 22 exposes its own built-in `localStorage`/`sessionStorage`
  globals, active without any CLI flag in some Node builds (confirmed on
  Node v25.6.1). These shadow jsdom's `window.localStorage` under
  Vitest's `environment: "jsdom"` and are non-functional without
  `--localstorage-file` — any code under test that calls real
  `localStorage`/`sessionStorage` (e.g. `authClient.ts`'s JWT session)
  throws `TypeError: X.getItem is not a function`. Fixed project-wide via
  `vite.config.ts`'s `test.poolOptions.{forks,threads}.execArgv:
  ["--no-experimental-webstorage"]` — this disables Node's competing
  implementation inside the Vitest worker so jsdom's real `Storage`
  (the one actually being tested) takes effect. Keep this flag if the
  Vitest `poolOptions` config is ever touched again.

<!-- added: 2026-09-14 | feature: fix-validacion-puntos-tarea-2026-09-14 | confidence: high | verified: 2026-09-15 -->
- When a numeric form field maps to a backend `Optional[int] = None`
  whose *absence* (not `0`) intentionally triggers a business-rule
  validation (see `src/api/schemas.py`'s comment on `puntos`), never
  build the request body with `Number(value)` directly on an empty
  string — `Number("")` is `0`, a valid value, so the field is never
  actually absent and the backend rule never fires. Convert explicitly:
  `value === "" ? undefined : Number(value)`, so `JSON.stringify` omits
  the key. `Tareas.tsx`'s `handleCrear` had this bug for `puntos`; check
  any other optional-numeric form field against the same pattern.
  Generalizes beyond empty-string numerics: `gastos-en-cuotas`'s `cuotas`
  field and `gastos-multi-moneda`'s `moneda` selector (which defaults
  visibly to `"ARS"` in the UI but is only sent in the body when the
  user picks `"USD"`, via `moneda === "ARS" ? undefined : moneda`) reuse
  the same "never send the backend's own default explicitly" shape —
  confirmed a 3rd time, promote to the reflex for any optional field
  with a backend-side default.
