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

<!-- [FRON-02] added: 2026-09-23 | feature: rediseno-ux-ui/sistema-visual | confidence: high | verified: 2026-09-23 -->
- [FRON-02] `theme.ts`'s "Cálido minimal" palette (spec
  `rediseno-ux-ui/sistema-visual`, D-01): primary is a deep teal/green
  (`#1b6b5c`), secondary a warm terracota accent (`#c1652f`), background
  an off-white warm tone (`#faf6f1`), `shape.borderRadius: 16`, and
  `components.MuiCard.styleOverrides.root` carries a fixed soft
  `boxShadow` (note: MUI's `variant="outlined"` Paper/Card always
  overrides this back to `boxShadow: none` at the CSS level regardless of
  `styleOverrides.root` — outlined cards show a border, not a shadow, by
  design). Semantic states (pagado/a_pagar/pendiente/rechazado) map onto
  MUI's own `success`/`warning`/`info`/`error` palette slots rather than
  ad-hoc per-screen colors. A shared `monetaryValueSx` export
  (`fontVariantNumeric: "tabular-nums"`) lives alongside `theme` for any
  screen displaying a monetary figure — use it instead of repeating the
  style inline.
- [FRON-03] Three presentational, dependency-free shared components live
  in `src/frontend/components/` (spec `rediseno-ux-ui/sistema-visual`,
  REQ-002): `PageHeader` (title/subtitle/optional primary action),
  `StatCard` (icon/label/value stat, kept intentionally minimal —
  compound content like a progress bar stays outside it rather than
  extending its props, see Patterns below), and `EmptyState`
  (icon/message/optional action, replacing a bare "no data" message).
  None of the three imports anything from `src/frontend/api/*` — that's
  what makes them safely reusable across every screen/domain. When
  swapping an existing plain-text "no data" message for `EmptyState`,
  pass the EXACT string an existing test already queries via
  `getByText(...)` — `EmptyState` renders `message` as its own leaf text
  node, so the query keeps matching with zero test changes.
- [FRON-04] The active nav item (mobile `BottomNavigation` and desktop
  `AppBar`/`GRUPOS_DESKTOP`) is highlighted with a filled/pill background
  using the theme's primary color (`alpha(primary.main, 0.12)` on
  mobile's `Mui-selected` class, `alpha('#ffffff', 0.18)` on desktop's
  primary-colored `AppBar`, since desktop buttons use `color="inherit"`
  and need a light overlay rather than the primary color itself to read
  against a primary-colored bar) — not just a color/opacity/font-weight
  cue as before (`nav-agrupada`'s S001 suggestion). `aria-current="true"`
  is set explicitly on both the mobile and desktop active items.
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

<!-- [FRON-05] added: 2026-09-23 | feature: rediseno-ux-ui/pantallas-casa | confidence: medium | verified: 2026-09-23 -->
- [FRON-05] When a screen restyle converts a table row into a `Card`
  (e.g. `Miembros.tsx`/`Tareas.tsx`, spec `rediseno-ux-ui/pantallas-casa`
  REQ-001/REQ-003), give the `Card` `role="group"` and
  `aria-label="<Entidad> <nombre>"` (e.g. `Miembro Ana`, `Tarea Sacar la
  basura`) instead of leaving it with no accessible container role. This
  keeps `within(tarjeta).getByText(...)`/`.getByRole(...)` queries
  working exactly like `within(fila).getByText(...)` did before —
  existing tests only need their scoping locator swapped
  (`.closest("tr")` or `getByRole("cell", ...)` -> `getByRole("group",
  { name: "..." })`), never the role/label assertions inside. A
  structural change mandated by the spec (table -> card/feed) can still
  break a query that was never really about role/label (a DOM-tag
  `closest` or a `cell` role tied to `<table>` semantics) even when the
  "queries por rol/label" promise otherwise holds — expect and budget for
  that, don't treat it as a regression to avoid at all costs.

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

<!-- [FRONP-04] added: 2026-09-23 | feature: rediseno-ux-ui/sistema-visual | confidence: medium | verified: 2026-09-23 -->
- [FRONP-04] When a screen wants to reuse a shared presentational
  component (e.g. `StatCard`) for a section whose content is COMPOUND
  (a stat value plus something else entirely — here, "Meta de la casa"
  pairing a value with a `LinearProgress` bar) rather than adding a
  `children`/slot prop to widen that shared component's contract, keep
  the compound section as its own local composition and reserve the
  shared component for the cases that actually fit its original, narrow
  shape. Same "duplicate a small per-caller shape over widening shared
  surface" criterion already established for backend-to-backend
  duplication (`[SERVP-02]` et al.) and the frontend/backend boundary
  (`[FRONP-03]`), extended here to a shared-component's own prop
  contract — this matters more than usual when 3 sibling specs
  (`pantallas-financieras`/`pantallas-casa`/`auth-onboarding`) already
  depend on that exact contract staying stable.

<!-- added: 2026-09-18 | feature: gamificacion-puntos | confidence: medium | verified: 2026-09-18 -->
- [FRONP-03] When a backend endpoint returns only an opaque catalog id
  (e.g. `GET .../logros` returning `logro_id: "primera_tarea"`, not a
  display name — the catalog itself, `LOGROS_CATALOGO`, is fixed
  in-code on the backend, not a DB table), the frontend keeps its own
  small `id -> nombre` display map (`Ranking.tsx`'s `NOMBRES_LOGRO`)
  rather than asking the API to also return the name. Same "duplicate
  a small per-layer helper over adding shared surface" criterion
  already established for backend-to-backend duplication (`[SERVP-02]`
  et al.), extended here across the frontend/backend boundary — keeps
  the API contract exactly what the backend task specified, at the
  cost of the two lists needing to be kept in sync by hand if the
  catalog ever changes.

<!-- added: 2026-09-16 | feature: prestamos-confirmacion-mutua | confidence: high | verified: 2026-09-16 -->
- [FRONP-02] Deciding "does this action belong to ME, specifically?"
  against TWO named roles (e.g. a préstamo's `prestamista`/`deudor`,
  each with its own confirmation field) follows a two-step order, not a
  single id comparison: [1] check the AGGREGATE state first (here,
  `estado_confirmacion === "pendiente_confirmacion"`) — an already-
  resolved record never shows the action regardless of who's looking;
  [2] only then compare `miembroIdActual` against the specific role's id
  AND confirm that role's own field is still `null` — comparing the id
  alone (skipping the `null` check) would also show the action to the
  party that already acted (confirmed or rejected), not just the one
  still pending. Same specificity criterion `Tareas.tsx`'s
  `puedeCompletar` already established for a single named role
  (`responsableId`), extended here to two independently-tracked roles on
  the same record.

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
