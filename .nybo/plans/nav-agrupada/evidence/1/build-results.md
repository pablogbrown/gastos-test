---
feature: nav-agrupada
schema: build-results/2
cycle: 1
updated: '2026-09-16T15:01:59.172Z'
exit: ready
verdict: verified
judgment:
  entries: 3
observations:
  entries: 1
tests:
  total: 98
  passed: 98
  failed: 0
  suite: vitest
build:
  status: pass
  command: npm run build
lint:
  status: pass
  command: npm run lint
coverage:
  status: unavailable
  reason: 'no coverage tool configured (stack.yaml quality_tools.coverage.tool: null)'
summary: 'nav-agrupada T1: menu agrupado desktop, TC-001..005 + TC-002 migrado en verde'
curated_at: '2026-09-16T15:03:00.000Z'
curated_duration: 90
---
### Goal

Implementar T1: agrupar el menú superior desktop (Inicio/Casa/Gastos/Tareas) en AppNav.tsx sin tocar SECCIONES ni la BottomNavigation mobile; actualizar el TC-002 de ui-modernization en AppShell.test.tsx.

### Observations

- [DOMAIN candidate — frontend.md] MUI está pinneado en v9.4.0. Props "legacy" tipo `MenuListProps`/`PaperProps` en `Menu` (y equivalentes en otros componentes con slots) quedaron deprecadas en esta major sin error de tipos ni warning de runtime consistente — usar la API de slots (`slotProps={{ list: {...} }}`, `slotProps={{ paper: {...} }}`, etc.) en vez de los props legacy al escribir componentes MUI nuevos en este repo.

### Verification

### Build
`npm run build` (`tsc --noEmit && vite build`) — **pass**, no errors. 640 modules transformed, `dist/` produced.

### Tests
`npm run test -- --run` (vitest) — **98/98 pass**, 18 test files, 0 failures. Includes the full frontend suite, not just the two files this spec's scope names — this cycle's regression fix in `App.test.tsx` (Judgment J001) is included and green.

`tests/unit/frontend/AppShell.test.tsx` in isolation — 9/9 pass (TC-001/TC-002 from `ui-modernization` + TC-001..TC-005 from this spec).

### Coverage
`unavailable — not configured`: `.nybo/foundation/stack.yaml`'s `quality_tools.coverage.tool` is `null` (pre-existing gap, not introduced by this cycle). `nybo.config.yaml`'s `testing.coverage_threshold: 80` cannot be checked mechanically. Remedy: `/nybo-brownfield-bootstrap --quality` (listed again in the checkpoint below).

### Test cases & progress
All 5 `[UNIT]` test cases from `spec.md` are automated and green:
- TC-001 — desktop muestra 4 elementos de primer nivel.
- TC-002 — clic en "Casa" despliega Miembros/Ranking/Actividad; elegir "Ranking" llama `onChange("ranking")` y cierra el menú.
- TC-003 — clic en "Gastos" despliega Gastos/Balance/Tarjetas/Suscripciones.
- TC-004 — con `pantalla="tarjetas"`, "Gastos" se marca activo (`aria-current="true"`).
- TC-005 (control) — mobile sigue mostrando las 9 pantallas sin agrupar.

The pre-existing `ui-modernization` TC-002 in the same file was updated (not deleted) to the new desktop contract; its sibling TC-001 (mobile) was left byte-for-byte untouched, as required. `feat/99-progress.md`'s Tasks/Verify/Test-Cases checkboxes are all `[x]`.

### Manual test cases
None declared as `[MANUAL]` or `[E2E]` in this spec's `spec.md` — nothing deferred to a human or to the e2e pipeline.

### Live evidence
Relevance gate: this cycle's change is live-checkable (a visual desktop-nav regrouping). Per the human's own explicit build instruction, docker/Postgres/live-browser verification was waived for this cycle — the spec is frontend-only (no backend/API/data surface touched) and the grouped-vs-flat behavior is already exercised end-to-end by the unit test suite (React Testing Library render + real MUI Menu interaction, not a mock of the component under test). Recorded as a Judgment entry (J003) rather than a silent skip. `stack.yaml`'s `dev_runbook` docker-compose smoke (10-verify.md's manual step) is available for a future ad-hoc human check but was not run here.

### Judgment log
3 entries this cycle (`evidence/1/build-results.md`'s Judgment section):
- J001 — fixed an unanticipated regression in `tests/unit/frontend/App.test.tsx` caused by this change's a11y semantics shift (tab → button/menu); confirmed it does not reproduce on the base commit, so it is this cycle's own to fix, not a pre-existing failure to exclude.
- J002 — MUI v9.4.0's `Menu` deprecates `MenuListProps` in favor of `slotProps.list`; switched to the current API (also captured as an Observations candidate for `frontend.md`).
- J003 — scoped verify to the frontend-only surface per the human's explicit instruction; backend pytest and docker/Postgres live smoke intentionally not run this cycle.

### Security
No new dependency, no new endpoint, no data/auth surface touched — pure client-side UI regrouping over already-existing screens. Nothing to flag.

### Design principles
Consistent with the project's existing patterns (`Clarity, Consistency, OOP` per `CLAUDE.md`'s Summary): reuses `SECCIONES` as the single source of icon/label truth (no hand-duplication), keeps `AppNav` as the sole navigation component, and keeps `App.tsx`'s `onChange(pantalla)` contract unchanged regardless of whether the pantalla came from a group menu or a standalone button.

### Wiki alignment
No `docs/`/wiki content describes the old flat 9-tab menu that would need updating; `.nybo/memory/domains/frontend.md` gets the MUI-v9-slots note via curate (Observations candidate above).

### Curation

Applied to `.nybo/memory/domains/frontend.md`:
- Updated the existing "responsive navigation shell" convention (added `ui-modernization`, verified bumped to 2026-09-16): desktop no longer renders `Tabs`, it renders `GRUPOS_DESKTOP` (standalone `Button`s + `Button`+`Menu` per group), still sourcing icon/label from `SECCIONES` by value; mobile is unchanged.
- Added a new Gotchas entry `[nav-agrupada, 2026-09-16]`: MUI v9.4.0's `Menu` deprecates `MenuListProps` (silently leaks onto the DOM instead of erroring) — use `slotProps={{ list: {...} }}` instead. Filed alongside the existing `Stack`-props gotcha since it's the same MUI-v9-deprecated-prop shape.

No new domain file was needed (frontend.md already existed and covers this surface); no new convention file/persona/ADR warranted for a single-component UI regrouping.
