# Build Results — auth-frontend (cycle 1)

## Summary
Executed T1–T4 end-to-end via TDD, then ran a single spec-level verify
pass. Result: green. 55 frontend tests pass (`npm run test`), `npm run
build` and `npm run lint` are clean, and TC-001 through TC-006 (all
`[UNIT]`) have dedicated tests. TC-007 (`[E2E]`, real browser) could not
be executed in this sandbox — see Verification Evidence.

## Judgment

1. **Extracted `ApiError`/`esApiError`/`formatErrorDetail` out of
   `casasClient.ts` into a new `src/frontend/api/httpError.ts`, not
   listed in any task's `files_touched`.** T1's dispatch explicitly
   flagged that `authClient.ts` should reuse `formatErrorDetail()` from
   `casasClient.ts` instead of reimplementing it. But `casasClient.ts`
   (and `gastosClient.ts`/`tareasClient.ts`/`dashboardClient.ts`) also
   need to import `fetchAutenticado` *from* `authClient.ts` (T2's
   Authorization-header requirement) — importing `formatErrorDetail`
   the other way would have created a circular module dependency between
   `authClient.ts` and `casasClient.ts`. Moved the three shared
   error-handling symbols to their own dependency-free module and had
   `casasClient.ts` re-export them, so every existing import
   (`gastosClient`/`tareasClient`/`dashboardClient` import
   `formatErrorDetail` from `./casasClient`) kept working unchanged.
   In-authority spec-deviation: satisfies the explicit reuse instruction
   without introducing a cycle.

2. **Removed the `usuarioId` prop entirely from `CrearCasa.tsx`,
   `Miembros.tsx`, `Gastos.tsx`, `InicioCasa.tsx`,
   `HistorialActividad.tsx`, `Balance.tsx`, and `Ranking.tsx`** (only
   `App.tsx`/`SelectorCasas.tsx` were in T2/T3's `files_touched`, plus
   `casasClient.ts`/`gastosClient.ts`/`tareasClient.ts`/
   `dashboardClient.ts`). Once those 4 API clients drop `usuarioId` as a
   parameter (T2's explicit contract: "Los 4 clientes existentes dejan
   de recibir `usuarioId` como parámetro"), every call site passing it
   becomes a compile error under this project's `noUnusedParameters`/
   strict TS config — and in all 7 of those pages, `usuarioId` had no
   other use besides that argument. Kept the prop on `Tareas.tsx`
   specifically, because it also feeds `puedeCompletar()`'s "am I the
   responsible member" business logic, unrelated to the HTTP auth
   header. Also updated `tests/unit/frontend/MuiRestyle.test.tsx` and
   `tests/unit/frontend/casasClient.test.tsx` to match — both render/call
   these signatures directly and are not on any task's file list, but
   would not compile/pass otherwise. This is the direct, unavoidable
   consequence of T2's stated contract, not an independent design choice.

3. **`obtenerUsuarioIdActual()` (decodes the JWT's `sub` claim
   client-side, unverified) added to `authClient.ts`** to give
   `Tareas.tsx` a replacement identity value now that `App.tsx` no longer
   generates a random `usuarioId`. This does not fix the pre-existing
   mismatch (`Tareas.tsx` compares this Usuario id against
   `tarea.responsableId`, which is populated from a Miembro id, not a
   Usuario id — already true before this spec, since the old random
   `usuarioId` was never a real Miembro id either) — fixing that
   conflation is out of scope for this spec (it would require choosing
   and wiring a real "which Miembro am I in this Casa" concept, not part
   of any REQ here) and is called out as an Observation below instead.

4. **Added a "Cerrar sesión" `IconButton` to `AppNav.tsx`** (not in any
   task's `files_touched` — T3 only lists `SelectorCasas.tsx` and
   `App.tsx`) via a new optional `onCerrarSesion` prop, rather than
   inlining a floating button directly in `App.tsx`. `AppNav.tsx` is
   already the single place that knows about the mobile/desktop layout
   split; a prop-gated addition there keeps `AppShell.test.tsx` (mobile/
   desktop layout tests, unmodified) passing unchanged, since the button
   only renders when the prop is passed.

5. **Added `/auth` to `vite.config.ts`'s dev-server proxy**, alongside
   the existing `/casas` entry — not listed in any task, but `Login`/
   `Registro` call `/auth/login`/`/auth/registro` directly, and without
   this the dev server (and therefore any live/E2E check, including
   TC-007) would 404 those requests in local dev the same way `/casas`
   already needed its own proxy entry.

6. **Environment fix, not a spec change: added
   `poolOptions.{forks,threads}.execArgv: ["--no-experimental-webstorage"]`
   to `vite.config.ts`'s `test` config.** Discovered while writing
   `authClient.test.tsx`: this sandbox's Node (v25.6.1) exposes its own
   built-in `localStorage` global (a stabilizing Node feature, active
   without any flag), which shadows jsdom's `window.localStorage` and is
   non-functional without `--localstorage-file` — every call in
   `authClient.ts` (which correctly uses real `localStorage`, per the
   spec's own Tradeoffs section) threw `TypeError: localStorage.getItem
   is not a function` under `npm run test` before this fix. This is an
   environment/tooling gap, not something any task file anticipated;
   disabling Node's competing implementation inside the test pool lets
   jsdom's real `Storage` implementation — the one actually being tested
   — take effect. Verified this is the true root cause (not a stray bug
   in `authClient.ts`) by reproducing it standalone with a plain jsdom
   script outside of Vitest.

## Observations (candidate conventions for /nybo-curate)
- **Node's built-in `localStorage`/`sessionStorage` globals (Node ≥ 22)
  shadow jsdom's implementation under Vitest and are non-functional
  without `--localstorage-file`.** Any current or future frontend code
  that uses real browser storage under a jsdom test environment needs
  `--no-experimental-webstorage` passed to the test runner's Node
  process (now set project-wide in `vite.config.ts`'s `test.poolOptions`)
  — worth capturing as a `frontend` domain convention so the next spec
  that touches `localStorage`/`sessionStorage` doesn't rediscover this
  from scratch.
- **`Tareas.tsx`'s `puedeCompletar()` compares a Usuario id
  (`obtenerUsuarioIdActual()`, this spec) against `tarea.responsableId`,
  which is actually a Miembro id** — a conflation between "global
  identity" and "per-casa Miembro" that predates this spec (the same gap
  `auth-backend`'s own Observations flagged server-side, via
  `resolver_actor_en_casa`) and now exists on the frontend too. No REQ in
  this spec calls for fixing it, and doing so would require a UI concept
  ("which Miembro am I in the current Casa") that doesn't exist yet — but
  it means "Marcar completada" visibility for a responsable-assigned task
  is not actually reliable today. Worth a follow-up spec once there's a
  real per-casa Miembro identity surfaced to the frontend.

## Verification Evidence
- `npm run build` → `tsc --noEmit && vite build` clean (0 errors), bundle
  produced.
- `npm run lint` → `eslint src/frontend --ext .ts,.tsx` clean (0
  warnings/errors).
- `npm run test` → 55/55 passing across 14 test files, including 4 new
  ones (`authClient.test.tsx`, `Login.test.tsx`, `Registro.test.tsx`,
  `SelectorCasas.test.tsx`, `App.test.tsx`) plus every existing
  frontend test file updated to the new session-based signatures.
  TC-001 (`App.test.tsx`), TC-002 (`Registro.test.tsx`), TC-003/TC-004
  (`authClient.test.tsx`), TC-005 (`SelectorCasas.test.tsx`), TC-006
  (`App.test.tsx`) each have a directly-named assertion.
- No remaining reference to `X-Usuario-Id` anywhere under
  `src/frontend/` (grepped) — all 4 clients now go through
  `fetchAutenticado`'s `Authorization: Bearer <jwt>` header exclusively.
- **Not verified in this sandbox** (no live browser, no running
  dev-server + backend pair available to this agent): TC-007's full
  browser walkthrough (registro → login → crear casa → navegar el shell
  → cerrar sesión → volver a loguearse y ver la misma casa), and the
  `[HUMAN]` visual-consistency gate in `10-verify.md` (Login/Registro/
  Selector styling vs. `ui-modernization`'s theme). Both are flagged
  for a human/E2E pass before this feature ships.
