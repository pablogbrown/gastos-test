# Build Results — Cycle 1 — fix-validacion-puntos-tarea-2026-09-14

## Execute

### T1 — Enviar Puntos como ausente cuando el campo está vacío
- TDD Red: added TC-001 (Puntos vacío → error de negocio, `puntos` ausente del body, ninguna tarea creada) and TC-002 (Puntos con valor → `puntos` enviado como número, tarea creada) to `tests/unit/frontend/Tareas.test.tsx`. Confirmed TC-001 failed before the fix (`Number("")` → `0` was sent, not absent).
- TDD Green:
  - `src/frontend/api/tareasClient.ts`: `CrearTareaInput.puntos: number` → `puntos: number | undefined`.
  - `src/frontend/pages/Tareas.tsx`'s `handleCrear`: `puntos: Number(puntos)` → `puntos: puntos === "" ? undefined : Number(puntos)`.
- Refactor: none needed — change is minimal and localized, consistent with the task's Design Rationale (no client-side duplicate validation; backend business rule remains the single source of truth).
- Completion gate for T1: full suite green, `npm run build` clean, `npm run lint` clean (see Verify below for the exact commands/output). Committed as `8d27a43`.

## Verify (spec-level, single pass)

Commands run against the whole change (`git diff --stat` confirmed only the 3 files in `run-plan.json`'s `files_touched` changed):

- `npm run test -- --run` → **59/59 passed** (14 test files), including `Tareas.test.tsx` 9/9 (7 pre-existing + TC-001 + TC-002).
- `npm run build` (`tsc --noEmit && vite build`) → clean, no type errors.
- `npm run lint` (`eslint src/frontend --ext .ts,.tsx`) → clean, no findings.

### Test-case completeness
- TC-001 (REQ-001): covered — asserts the error alert text, that the created task never appears in the list, and directly inspects the sent request body to confirm the `puntos` key is absent.
- TC-002 (REQ-002): covered — asserts `puntos` is sent as `5` (number) and the task is created/refreshed in the list, exactly as before the fix (control case, unchanged behavior).
- Both are `[UNIT]` per spec.md and `run-plan.json`; no `[E2E]` test cases exist for this spec, so the e2e pipeline was not invoked (not applicable per spec scope).

### Live evidence
- `feat/10-verify.md`'s End-to-End Verification step 2 ("Smoke manual: intentar crear una tarea sin puntos en el docker-compose local") is a manual/optional step, not one of the `[AUTO]` Gate Criteria. No live docker-compose environment was available/started in this autonomous session; the AUTO gate criteria (TC-001/TC-002 green, `npm run build`, full `npm run test -- --run`) are the authoritative pass/fail signal for this LOW-severity, single-file frontend fix and are all green. TC-001 directly asserts the real HTTP request body shape (no `puntos` key), which is the same signal a manual smoke test would confirm.

### Verdict
**Green.** Goal satisfied: submitting "Crear tarea" with Puntos empty now surfaces the backend's business-rule error instead of silently creating a 0-point task; the control case (Puntos filled) is unaffected.

## Judgment
- No autonomous judgment calls outside plan/spec-deviation were needed — the implementation matched the task file's specified change exactly (`CrearTareaInput.puntos` → `number | undefined`; `handleCrear`'s conditional `puntos` expression). No plan deviation.
- Decision: run the spec-level manual-smoke step's equivalent via the existing TC-001 request-body assertion instead of spinning up docker-compose, since no live environment was provisioned in this session and the AUTO gates already provide the definitive signal. Class: environment-blocker-adjacent but not a true blocker (build/tests were not blocked; this only concerns an optional manual step) — recorded here rather than as a `decisions.yaml` entry since it does not block "ready" and requires no human input to resolve.

## Observations
- Confirms the existing project convention (see `src/api/schemas.py`'s comment on `puntos: Optional[int] = None`) that "absent" vs "explicit 0" is a deliberate distinction backend validators rely on — frontend clients constructing request bodies from string form state must preserve that distinction (`value === "" ? undefined : Number(value)`) rather than coercing empty string through `Number()` directly. Worth keeping in mind for any other optional numeric field in this codebase (e.g. future forms) that has a similar backend "required via absence" contract.
