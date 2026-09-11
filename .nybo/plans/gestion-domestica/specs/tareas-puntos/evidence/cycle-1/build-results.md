# Build Results — tareas-puntos — Cycle 1

## Summary
All four tasks (T1-T4) implemented via TDD, spec-level verify passed on the
first cycle. No escalated blockers. Backend: 47/47 tests green (pytest;
27 new for this sub-spec, 20 pre-existing from `casas-miembros`). Frontend:
10/10 tests green (vitest; 6 new for this sub-spec, 4 pre-existing).
`npm run build` and `npm run lint` clean. All 10 test cases (TC-001..
TC-010) covered across unit/integration layers, matching the mapping in
`feat/10-verify.md`. Live end-to-end smoke run against a real SQLite-file
+ uvicorn process reproduced all 5 steps of `feat/10-verify.md`'s
"End-to-End Verification" section exactly (create → complete → ranking →
recurrence → historial survives deactivation).

## Execution
| Task | Files | Tests | Result |
|---|---|---|---|
| T1 | src/db/models/tarea.py, src/db/models/historial_tarea.py, src/db/migrations/0003_tareas.py | tests/unit/db/tarea.test.py (3) | green |
| T2 | src/services/tarea_service.py, src/services/ranking_service.py, src/services/exceptions.py (added `ConflictError`) | tests/unit/services/tarea_service.test.py (13), tests/unit/services/ranking_service.test.py (4) | green |
| T3 | src/api/routes/tareas.py, src/api/schemas.py (added Tarea/Historial/Ranking schemas), src/api/main.py (registered `tareas_router`) | tests/integration/api/tareas_routes.test.py (8) | green |
| T4 | src/frontend/pages/Tareas.tsx, src/frontend/pages/Ranking.tsx, src/frontend/api/tareasClient.ts | tests/unit/frontend/Tareas.test.tsx (6) | green |

Spec-level verify (`/nybo-verify --auto` equivalent, run once after all
tasks): build succeeded (`npm run build` — `tsc --noEmit` + `vite build`),
full test suite green (57/57 across both runners: 47 pytest + 10 vitest),
lint clean (`npm run lint`), all 10 TCs traced to at least one passing
test, and a live manual smoke run reproduced `feat/10-verify.md`'s 5-step
End-to-End Verification scenario against a real uvicorn process + file
-backed SQLite DB (not just in-process test fixtures).

## Judgment Section (autonomous decisions — trust level: semi-autonomous)

Trust level settles `spec-deviation` only; every entry below stayed
within that class or was a straightforward interface-filling decision
required to make the documented signatures runnable — none touched
security, schema-migration-as-a-new-tool, api-contract-breaking,
new-dependency, cost, or external-copy classes that this trust level
must defer.

1. **Reused `casas-miembros`'s guard/model exports verbatim, as
   instructed.** `crear_tarea`/`completar_tarea` call
   `requiere_membresia_activa(casa_id, actor)` exactly as
   `casa_service.py`/`miembro_service.py` call it internally — no
   membership logic was reimplemented. `Casa`, `Miembro`, `RolEnum` are
   imported directly from `src/db/models/`, never redefined.
2. **Migration numbered `0003`, matching the run-plan exactly (gap at
   `0002` is intentional).** The sibling spec `gastos`, built in a
   parallel worktree off the same `feat/gestion-domestica` base, reserves
   `0002` for its own migration. Using `0003` here (as `run-plan.json`'s
   `files_touched` already specifies) avoids a filename collision when
   both branches merge, even though neither branch can see the other's
   commits during the build.
3. **`completar_tarea(tarea_id, miembro_id, actor)` keeps `miembro_id`
   (the credited member) and `actor` (who performs the call) as distinct
   parameters, per the given signature, and enforces:** if the tarea has
   a `responsable_id`, only that member (or an admin recording on their
   behalf) may complete it; if unassigned, any active member may
   complete it but only for themselves (or an admin recording on
   someone's behalf). This is the narrowest reading of TC-004 ("cualquier
   miembro activo la marca como completada... la tarea queda asociada a
   quien la completó") consistent with the two-parameter signature
   already fixed by T2's "Interfaces Produced".
4. **`ConflictError` added to `src/services/exceptions.py`.** T3's Done
   When explicitly requires "409 al completar una tarea ya completada",
   distinct from the 400 used for validation errors elsewhere. Neither
   `ValidationError` nor any existing exception maps to 409, so a new,
   narrowly-scoped exception class was added to the shared exceptions
   module (extending it, not replacing or duplicating the file per
   sub-spec).
5. **`TareaCreate.puntos` is `Optional[int] = None` at the Pydantic
   schema level, not a required field.** This makes an omitted `puntos`
   reach `crear_tarea`'s own business validation (→ HTTP 400) instead of
   FastAPI's automatic 422 on missing required fields — matching T3's
   Done-When criterion "400 sin nombre/puntos" and the same pattern
   `casas-miembros` used for "sin nombre" (an empty string, not an
   omitted field, since `nombre` stays a required schema field there).
6. **`responsableId`/`fechaPrevista`/`miembroId` use Pydantic aliases for
   camelCase, per `00-overview.md`'s explicit API contract; other fields
   stay snake_case, matching the ERD's field names.** `00-overview.md`'s
   "API/Data Contracts" table literally spells these three fields in
   camelCase (unlike `casas-miembros`, whose own contract never used
   camelCase), so the alias is a deliberate one-spec-specific choice, not
   a broader project convention.
7. **`procesar_recurrencia(tarea_id: UUID) -> Optional[Tarea]`** takes an
   id and re-fetches internally, rather than accepting the `Tarea` object
   `completar_tarea` returns. `completar_tarea`'s SQLAlchemy session
   closes after returning `HistorialTarea` (with `expire_on_commit=True`
   at the engine level, matching `casas-miembros`'s session config), so a
   `Tarea` instance handed across that boundary would be detached with
   expired attributes. Taking the id and opening a fresh session avoids
   that entirely, and `tareas.py` (T3) already has `tarea_id` from the
   URL path, so no extra round-trip is needed.
8. **`App.tsx` was NOT touched.** T4's `files_touched` in `run-plan.json`
   lists only `Tareas.tsx`, `Ranking.tsx`, `tareasClient.ts`; `status.yaml`
   records this sub-spec as blocking `dashboard-actividad`, which reads as
   the future integration point that wires these pages into navigation.
   Wiring them into `App.tsx` now would risk merge conflicts with the
   concurrently-built `gastos` sub-spec's own UI work on the same file
   and wasn't in scope.
9. **No dedicated `Historial.tsx` file.** `00-overview.md`'s UX/UI section
   names a third screen ("Historial de tareas") but T4's `files_touched`
   lists only 3 files, none named `Historial.tsx`. The historial table is
   rendered as a section within `Tareas.tsx` instead of a new file outside
   the task's declared scope.
10. **Responsable is entered as a free-text member id in the create-task
    form**, not a name-resolving dropdown. Building a full member picker
    would mean importing `casasClient.listarMiembros` and adding
    selection UI beyond what `Tareas.tsx`'s stated scope covers; flagged
    in Observations below as a natural follow-up, not done here to avoid
    scope creep on a UI task with no listed test file beyond
    `Tareas.test.tsx`.
11. **Ranking/Historial rows show raw member ids, not names** — same
    reason as #10: no name-resolution data is available within this
    sub-spec's contract (`calcular_ranking`/`historial` only return ids).

## Observations (candidate conventions — for /nybo-curate)
- Adding a new HTTP-conflict-shaped domain exception (`ConflictError`)
  to the *shared* `src/services/exceptions.py` (rather than each sub-spec
  growing its own exceptions module) kept the "exceptions → HTTP status"
  mapping pattern established by `casas-miembros` consistent across
  specs. Recommend continuing to extend this one shared module rather
  than forking per-domain exception files.
- This sub-spec confirms the `evidence/suggestions.yaml` prediction from
  `casas-miembros`: a service (`completar_tarea`) needed multiple related
  writes (insert `HistorialTarea` + update `Tarea.estado`) in one
  transaction, which worked fine under the existing "one `get_session()`
  per service call" pattern. No sibling-transaction-spanning-two-services
  case arose yet (this spec's `crear_tarea`/`completar_tarea` do call the
  cross-spec `requiere_membresia_activa` guard, which opens its own
  separate session — read-only, so no cross-session write consistency
  issue surfaced). Worth re-checking this suggestion once `gastos` lands.
- `EstadoTareaEnum`/`RolEnum` both follow the `str, enum.Enum` pattern
  established by `casas-miembros`'s `RolEnum` — worth naming explicitly
  as the project's enum convention in `.nybo/memory/domains/db.md`.
- A richer "pick a real member by name" UI control (backed by
  `casasClient.listarMiembros`) would improve `Tareas.tsx`'s create-task
  form and the Ranking/Historial displays; deferred to avoid scope creep
  (see Judgment #10/#11) — a good candidate for the `dashboard-actividad`
  sub-spec that already plans to integrate these pages.
- Confirms `casas-miembros`'s suggestion `adopt-alembic-on-second-migration`:
  this is now the *second* migration file (`0003_tareas.py`, with `0002`
  reserved for `gastos`); once both land, a real migration engine
  (Alembic) is worth adopting instead of hand-written `create_all` per
  file — carried forward in `evidence/suggestions.yaml`.

## Verification Evidence
- `python3 -m pytest tests/ -q` → 47 passed (20 pre-existing + 27 new:
  T1: 3, T2: 17 (13 + 4), T3: 8, historial/ranking cross-checks included).
- `npm run test` (vitest) → 10 passed (4 pre-existing + 6 new).
- `npm run build` → `tsc --noEmit` clean, `vite build` succeeded.
- `npm run lint` → no ESLint errors/warnings.
- Manual TC-to-test mapping cross-checked against `feat/10-verify.md` and
  `feat/99-progress.md` — all 10 TCs have at least one passing assertion.
- Live smoke test: started `uvicorn src.api.main:app` against a
  file-backed SQLite DB with migrations `0001`+`0003` pre-applied, and
  replayed `feat/10-verify.md`'s exact 5-step scenario via `curl`:
  1. Created tarea "Limpiar baño" (10 pts, no responsable).
  2. A member completed it → `estado: completada`.
  3. Ranking showed that member with 10 points.
  4. Created + completed a daily-recurrent tarea "Sacar la basura" (3
     pts) → confirmed a new `pendiente` instance appeared with a
     different id.
  5. Deactivated the completing member → historial still listed both
     entries (10 pts and 3 pts) under that member's id.
