# Build Results — auth-backend (cycle 1)

## Summary
Executed T1–T4 end-to-end via TDD, then ran a single spec-level verify
pass. Result: green. 127 backend tests pass
(`pytest tests/ --ignore=tests/unit/frontend`), including 10/10 spec
test cases and a full end-to-end JWT flow (registro → login → crear
casa → agregar miembro por email → GET /casas/mias → 403 sin
membresía), validated both in automated tests and a manual smoke test
against the real `src.api.main.app`.

## Judgment

1. **`resolver_actor_en_casa` added to `miembro_service.py` (T3), not
   listed in `run-plan.json`'s T3 `files_touched`.** T3's own task doc
   says routes should "resolver el Miembro correspondiente a ese
   usuario_id... reutilizando `requiere_membresia_activa`". But
   `requiere_membresia_activa(casa_id, usuario_id)` is already consumed
   by `gasto_service`/`tarea_service` with a *Miembro.id* as the second
   argument (confirmed by reading those callers) — changing its query
   semantics to filter by the new `usuario_id` FK instead would have
   broken those two already-shipped internal call sites. Decision: leave
   `requiere_membresia_activa` untouched, and add a new, separate bridge
   function (`resolver_actor_en_casa`) that translates the JWT's global
   `usuario_id` into the per-casa `Miembro.id` that all existing service
   signatures expect. Recorded as a deliberate, in-authority
   spec-deviation (adds one function to a file T3 didn't list, but
   doesn't touch any interface T3 already commits to).

2. **`resolver_actor_en_casa` (membership + 403 gate) applied uniformly
   to *every* casa-scoped route in `casas.py`/`gastos.py`/`tareas.py`/
   `dashboard.py`, including read-only routes whose underlying service
   never checked membership before (e.g. `listar_miembros`,
   `listar_categorias`, `calcular_ranking`).** Before this spec, those
   routes accepted the `X-Usuario-Id` header but never validated it
   against anything — a latent gap that only mattered because there was
   no real identity to check. `10-verify.md`'s own End-to-End
   Verification step 5 exercises a GET route expecting 403 for a
   non-member, and REQ-005's "nadie puede operar sobre una casa sin
   haberse registrado" reads as intentionally closing that gap now that
   real auth exists. Decision: enforce active membership on every
   `casa_id`-scoped route, not just the ones whose service layer already
   had a check. This is a spec-deviation (broader than "swap the header
   for a JWT") but stays inside the spec's stated intent and directly
   satisfies TC-009 and the e2e walkthrough.

3. **`crear_casa` now generates a fresh `Miembro.id` (`uuid.uuid4()`)
   instead of reusing `usuario_creador` as the Miembro's primary key.**
   This breaks the literal assertion in the pre-existing
   `casas-miembros` test `admin.id == usuario_creador` — but preserving
   the old behavior is mathematically impossible once a single Usuario
   can create two Casas (TC-007): `Miembro.id` is the table's single-
   column primary key, global across all casas, so reusing the same
   `usuario_id` value for two different Miembro rows would violate the
   PK constraint on the second `crear_casa` call. This was flagged in
   the dispatch as an expected breaking change; updated the assertion to
   check `admin.usuario_id == usuario_creador` instead (the FK is now
   the identity link, not the PK).

4. **Ripple fix across all four already-shipped `gestion-domestica`
   sub-specs' test suites** (`casas-miembros`, `gastos`, `tareas-puntos`,
   `dashboard-actividad` — 13 test files total), because those suites
   call `crear_casa(nombre, admin_id)` directly at the service layer and
   then reuse `admin_id` downstream *as if it were the admin's
   `Miembro.id`* (true before this spec, since Miembro.id used to equal
   the raw actor id). Fixed by reassigning `admin_id = casa.miembros[0].id`
   immediately after `crear_casa` in each fixture/test, and by registering
   a real `Usuario` row before every `agregar_miembro` call (which now
   requires a real email to resolve). No business-rule assertion was
   weakened — only the identity-resolution mechanics were adapted, per
   the dispatch's explicit instruction to preserve every existing rule
   "exactly; only HOW the actor's identity is resolved changes."

5. **Migration `0001_casas_miembros.py` now imports `Usuario` (noqa,
   side-effect only) and `0005_usuarios.py` uses an idempotent,
   inspector-checked `ALTER TABLE ... ADD COLUMN` instead of an
   unconditional one.** Root cause: this project's migrations operate
   directly on `Base.metadata`/`ModelClass.__table__`, which always
   reflects the *current* Python model, not a historical snapshot. Two
   real scenarios both had to work: (a) a brand-new test DB, where 0001
   already creates `miembros` with the current `usuario_id` column
   (since `Miembro.__table__` already has it) — 0005 must skip the
   `ALTER` there; and (b) an actually-deployed DB where 0001 ran *before*
   this spec existed (T1's own "Done When": "corre limpia sobre una base
   con las 4 migraciones anteriores ya aplicadas") — 0005 must add the
   column there. Verified both paths directly (a simulated pre-existing
   DB without the column takes the `ALTER` branch; a second `upgrade()`
   call is idempotent).

6. **Duplicate email in `registrar_usuario` reuses the existing
   `ConflictError` (409)** rather than a new exception class — TC-002
   specifies 409, and `ConflictError` is already defined and already
   mapped to 409 by `tareas.py`'s existing exception handling pattern;
   reusing it keeps one exception vocabulary across the whole app.

7. **`auth.py`'s request schemas use plain `str` for `email`, not
   Pydantic's `EmailStr`.** `EmailStr` requires the `email-validator`
   extra, which is not among the two dependencies pre-approved in the
   spec (`pyjwt`, `bcrypt`). Format validation stays a non-goal;
   `registrar_usuario` already rejects empty/whitespace-only emails.

8. **`bcrypt` pinned to `>=4.1,<5.0`** in `requirements.txt` (matching
   what got installed in the worktree venv) rather than the `5.0.0` that
   `pip install bcrypt` resolved to initially, for a narrower, more
   conservative version range consistent with the other pins in the
   file (all use `<major+1`).

## Observations (candidate conventions for /nybo-curate)
- This project's migrations are **not** historical snapshots — each
  migration file's `create_all` reflects the *current* model definition,
  so any new column on an existing table needs an idempotent
  `ALTER TABLE` fallback (inspector-checked), not just a `create_all`.
  Worth capturing as a domain convention under `db` before the next
  schema change hits the same surprise.
- Existing services conflate "the identity of an actor" with
  "`Miembro.id` scoped to one casa" throughout `gasto_service`,
  `tarea_service`, `casa_service`, and `miembro_service`. Any future
  auth-adjacent spec touching these needs the same
  global-identity-to-per-casa-id bridge pattern established here
  (`resolver_actor_en_casa`).

## Verification Evidence
- `pytest tests/ --ignore=tests/unit/frontend -q` → 127 passed.
- Manual end-to-end smoke test against `src.api.main.app` (via
  `TestClient` used as a context manager, to trigger the real startup
  migration path) — registro/login/crear casa/GET casas/mias/401
  without JWT, all behaved as expected.
- Migration 0005's `ALTER TABLE` fallback verified directly against a
  hand-built "pre-existing DB" schema lacking `usuario_id`, plus an
  idempotency check (second `upgrade()` call does not raise).
- No remaining functional references to `X-Usuario-Id` in `src/api` or
  `src/services` (only historical mentions in docstrings/comments);
  the frontend TS clients under `src/frontend/api/` still use it
  on purpose — that migration belongs to the sibling `auth-frontend`
  sub-spec, out of scope here.
