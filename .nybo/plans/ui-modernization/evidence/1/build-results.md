---
feature: ui-modernization
schema: build-results/2
cycle: 1
updated: '2026-09-11T21:55:04.419Z'
exit: ready
verdict: verified
tests:
  total: 31
  passed: 31
  failed: 0
judgment:
  entries: 3
observations:
  entries: 1
---
### Judgment

- **J003** Avoided MUI's `Stack` component: the installed @mui/material@9.4.0 type-checked Stack in a way that rejected alignItems/gap props without an explicit component prop. Replaced every intended Stack usage with Box + sx={{ display: 'flex', ... }}, functionally equivalent. Flagged as a Question for the Human in evidence/suggestions.yaml (S002).
- **J004** TC-006 (E2E, 360x800 real browser) could not be directly observed — this sandbox has no Playwright/Chromium or other browser automation tool, and none was installed given the scope of a UI-only restyle spec. Mitigated with (a) a manual responsive-CSS review of all 8 screens, and (b) a dev-server smoke check confirming the module graph compiles and serves without runtime errors. This is NOT equivalent to a real-browser observation — TC-006 stays unchecked in feat/99-progress.md and is called out in the handoff (S001) as needing a human or a session with real browser tooling.
- **J001** Extracted `AppNav` as its own component (`src/frontend/AppNav.tsx`) instead of leaving the responsive nav inline in `App.tsx` as T1's task file implied — makes TC-001/TC-002/TC-004 directly testable without routing through the 'create a casa' flow. Decision class: spec-deviation, settleable at semi-autonomous trust; no API/contract impact.

### Observations

- The existing test suite needed zero selector changes after the MUI restyle — every getByLabelText/getByRole/getByText query already used semantic, accessible queries that MUI's rendered output satisfies out of the box. Worth recording as a reusable convention: write frontend tests against accessible roles/labels, not CSS classes or DOM structure.

### Verification

- Build: `npm run build` (tsc --noEmit + vite build) — green.
- Lint: `npm run lint` — green, 0 warnings/errors.
- Tests: `npm run test` — 31/31 passing (7 files): existing 23 tests unmodified and passing, plus 8 new tests (MuiRestyle.test.tsx, TC-003) and 4 new tests (AppShell.test.tsx, TC-001/002/004).
- Test cases: TC-001 through TC-005 automated and green. TC-006 ([E2E]) not observed live — see Judgment J004.
- Live evidence: dev server (vite) smoke-checked — serves index.html shell and transforms main.tsx/App.tsx/theme.ts without error. No screenshot/video captured (no browser tool available in this sandbox).
- Regression: no backend or API client files were changed in any of the 4 tasks — git diff confirms only src/frontend/**, tests/unit/frontend/**, package.json/package-lock.json, and README.md changed.

### Curation

Extracted 4 durable conventions/patterns/gotchas into .nybo/memory/domains/frontend.md: (1) MUI theme lives at src/frontend/theme.ts, consumed via ThemeProvider; (2) responsive nav shell is its own component (AppNav.tsx) for testability; (3) accessible-role-based test queries survive a full component-library restyle with zero selector changes; (4) MUI Select native variant needed when existing tests assert getByRole('option', ...) without opening the dropdown; (5) Stack component type-checking gotcha in @mui/material@9.4.0 — use Box+sx instead.
