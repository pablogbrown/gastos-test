# Domain: frontend

frontend domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-11 | feature: ui-modernization | confidence: high | verified: 2026-09-11 -->
- UI is built with Material UI (`@mui/material`, `@mui/icons-material`,
  `@emotion/react`, `@emotion/styled`). One shared theme lives at
  `src/frontend/theme.ts` (exported `theme`, via `createTheme`) — screens
  never define their own ad-hoc palette/typography, they consume this
  theme through `ThemeProvider` (wired once in `main.tsx`).
- The responsive navigation shell (bottom tab bar on mobile < `sm`
  breakpoint / top `AppBar` + `Tabs` on desktop) is its own component,
  `src/frontend/AppNav.tsx` — kept separate from `App.tsx` specifically
  so it can be unit-tested (`tests/unit/frontend/AppShell.test.tsx`)
  without needing to drive the full "create a casa" flow first.

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
