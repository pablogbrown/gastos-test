# Domain: services

services domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-14 | feature: fix-membresia-duplicada-actor-2026-09-14 | confidence: high | verified: 2026-09-14 -->
- [SERV-01] Business-invariant uniqueness checks (e.g. "at most one active `Miembro` per `(casa_id, usuario_id)`") are validated in the service layer, before the write, mirroring how duplicate-`identificacion` is already checked — never as a database `UNIQUE` constraint. This keeps the check colocated with the other `agregar_miembro`-style validations and avoids a schema migration for a service-level rule; see `.nybo/plans/fix-membresia-duplicada-actor-2026-09-14/feat/00-overview.md`'s Tradeoffs for the explicit reasoning.

<!-- added: 2026-09-14 | feature: fix-historial-desactivacion-miembro | confidence: high | verified: 2026-09-14 -->
- [SERV-02] `registrar_actividad` (activity-log hook, `actividad_service.py`)
  is called only AFTER the triggering business operation's own `commit`
  succeeds, never before and never on a failure/exception path — so an
  activity entry never describes something that ultimately didn't happen.
  Established by `gasto_service.registrar_gasto`/`tarea_service.crear_tarea`/
  `completar_tarea`; `miembro_service.agregar_miembro`/`desactivar_miembro`
  now follow the same shape. Any new service action that should appear in
  the Historial de actividad calls this hook the same way, right after its
  own commit.

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- added: 2026-09-15 | feature: invitar-miembro-pendiente | confidence: high | verified: 2026-09-15 -->
- [SERVP-01] A function meant to be called FROM another service, as part of
  that caller's own transaction (not from a route), takes an already-open
  `session` as its first parameter instead of opening its own via
  `get_session()` — the one deliberate exception to this module's usual
  shape (every other function here opens/commits/closes its own session).
  It never calls `session.commit()`/`session.close()` itself; the caller
  owns the transaction boundary. Document the exception explicitly in the
  function's own docstring so it isn't "fixed" later to match the module's
  usual pattern. First example: `miembro_service.vincular_membresias_pendientes(session, usuario_id, email)`,
  called from `auth_service.registrar_usuario` right after the new
  `Usuario`'s own commit, so the Usuario's creation and its pending
  memberships' linking are atomic (one rollback undoes both).

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-14 | feature: fix-membresia-duplicada-actor-2026-09-14 | confidence: high | verified: 2026-09-14 -->
- [SERVG-01] A `.one_or_none()` query that assumes "at most one row" for an invariant enforced only in the service layer (no DB constraint) is a latent crash risk: if that invariant is ever violated (preexisting data, an unanticipated write path), SQLAlchemy raises `MultipleResultsFound`, which nothing in the call chain catches — it surfaces as an unhandled 500 (`resolver_actor_en_casa`'s original bug). When a query reads state that must never crash even if the invariant it depends on was broken by data that predates the guard, prefer `.order_by(<stable-column>).first()` — never raises, and gives a deterministic, repeatable result regardless of how many rows actually exist.

<!-- added: 2026-09-15 | feature: invitar-miembro-pendiente | confidence: high | verified: 2026-09-15 -->
- [SERVG-02] Calling `session.commit()` a SECOND time on the same
  request/service call (e.g. to persist a side-effect that happened after
  the "main" object was already committed and `session.refresh()`d)
  expires that object's attributes again (SQLAlchemy's default
  `expire_on_commit=True`). If the function returns that object without
  refreshing it again, any attribute access after `session.close()` (in
  the `finally`) raises `DetachedInstanceError` — not immediately, but at
  the caller's first attribute read, which makes it look unrelated to the
  actual cause. Whenever a function does N commits on an object it still
  needs to return, call `session.refresh(obj)` again after the LAST
  commit, not just after the first. Found in
  `auth_service.registrar_usuario` after adding a second commit for
  `vincular_membresias_pendientes`.
