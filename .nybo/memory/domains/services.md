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

<!-- added: 2026-09-15 | feature: tarjetas-credito | confidence: medium | verified: 2026-09-15 -->
- [SERV-03] Whether a write action requires `_validar_actor_admin`
  (Administrador only, e.g. `suscripcion_service.crear_suscripcion`) or
  the looser `miembro_service.requiere_membresia_activa` (any active
  member, e.g. `gasto_service.registrar_gasto`/`tarea_service.crear_tarea`/
  `tarjeta_service.crear_tarjeta`) is decided per-spec by the requirement
  text, not by resource shape: "un miembro puede..." (no role mentioned)
  means any active member; an explicit "solo un Administrador" means the
  admin guard. Don't default to the admin guard just because a sibling
  resource (e.g. `Suscripcion`) happens to use it — check the spec's own
  wording for the action being added.

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- added: 2026-09-16 | feature: gastos-sin-reparto | confidence: high | verified: 2026-09-16 -->
- [SERVP-06] When a service's return type changes SHAPE (not
  additively — e.g. `calcular_balance` going from `List[BalancePorMiembro]`
  to a `BalanceCasa` dataclass), grep for every consumer of the OLD
  type name across the whole repo before considering the change
  complete, not just the files named in the task's own Scope. This
  spec's own task file for the API/dashboard layer didn't list
  `src/frontend/api/dashboardClient.ts` — it imported `BalancePorMiembro`
  from `gastosClient.ts` for its own `DashboardCasa.balance` field, and
  without updating it the frontend build (`tsc --noEmit`) would have
  failed. A scope list is a starting point, not the full consumer graph;
  a shape-changing (not additive) contract change earns a repo-wide grep
  for the old type/field names before calling the task done.

<!-- added: 2026-09-16 | feature: gastos-estado-pago | confidence: high | verified: 2026-09-16 -->
- [SERVP-05] A new purely-informational attribute on `Gasto` (e.g.
  `moneda`, `tarjeta_id`, now `estado`) is validated against a
  module-level constant set (`ESTADOS_VALIDOS`, mirroring
  `MONEDAS_VALIDAS`) in `gasto_service.py`, and every automatic
  generator (`suscripcion_service.py`, `resumen_importer_service.py`)
  passes its own value EXPLICITLY at each `registrar_gasto`/sibling call
  site — never by changing `registrar_gasto`'s own default. This is the
  4th confirmation of this exact shape (`moneda`, `tarjeta_id`, `estado`)
  — treat it as the project's settled convention for "a new Gasto
  attribute a generator marks differently from the manual-entry
  default", not a coincidence.

<!-- added: 2026-09-15 | feature: gastos-en-cuotas | confidence: high | verified: 2026-09-16 -->
- [SERVP-02] Month arithmetic (adding N calendar months to a `date`,
  clamping the day when the target month is shorter — e.g. 31 ene + 1 mes
  -> 28/29 feb; or resolving a `YYYY-MM` string to its first/last day) is
  done with stdlib only (`date.year`/`date.month` plus
  `calendar.monthrange` for the day bound), never `python-dateutil` —
  not a declared project dependency. `balance_service._rango_mes` already
  used this technique for "first/last day of a month"; `gasto_service.
  _sumar_meses` (spec `gastos-en-cuotas`) was the second independent
  case. Spec `gastos-vista-mensual` adds a THIRD: `gasto_service.
  _rango_mes` — a deliberate near-duplicate of `balance_service.
  _rango_mes` (same stdlib logic, `mes` required instead of
  defaulting to "current month" — see that spec's Design Rationale) —
  confirming both the stdlib-only approach AND "duplicate this small
  helper per-service rather than share it across `gasto_service`/
  `balance_service`" as settled conventions, not one-offs. Reach for the
  same stdlib approach (and the same per-service duplication) before
  reaching for a new dependency or a shared helper module the next time
  month/date arithmetic comes up.

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

<!-- added: 2026-09-15 | feature: importar-resumen-tarjeta | confidence: medium | verified: 2026-09-15 -->
- [SERVP-03] When a new caller needs "only the REMAINING part of a
  series already in progress" (e.g. cuotas `N..M` of a purchase that
  started before this system knew about it) rather than "a brand-new
  series from 1", write a dedicated sibling function
  (`gasto_service.registrar_gasto_cuotas_restantes`) instead of adding a
  starting-point parameter to the existing "start fresh" function
  (`_crear_gastos_en_cuotas`). The two have genuinely different inputs
  (a total to divide vs. an already-known per-installment amount) and
  different invariants (`1..N` vs `cuota_actual..cuota_total`) — forcing
  them into one function via an optional parameter would let a caller
  pass an inconsistent combination (e.g. a starting point with a
  bundled amount for the trend "starts at 1" caller to accidentally
  divide by the wrong count). Both share the real reusable primitives
  (`_dividir_importe`, `_sumar_meses`, `_resolver_participantes`) — only
  the top-level orchestration differs. Same shape as `SERVP-02`'s
  reusable-primitive rule: share the math, not the top-level flow, once
  the callers' invariants genuinely diverge.

<!-- added: 2026-09-15 | feature: importar-resumen-tarjeta | confidence: medium | verified: 2026-09-15 -->
- [SERVP-04] When a new caller wants a resource-creation function's
  find-or-create/permission logic but NOT one of its side effects (e.g.
  `suscripcion_service.crear_suscripcion` also generates a gasto dated
  "today", which would be wrong for a caller importing a historical
  transaction with its own real date/amount), write a dedicated variant
  (`registrar_suscripcion_detectada`) rather than adding a flag to
  suppress the side effect on the original. A boolean flag threaded
  through a function whose entire other behavior stays identical
  quietly turns "today, always" into "today, unless told otherwise" for
  every existing caller too, and every future reader has to check the
  flag's default to know which behavior applies where. A dedicated
  function keeps each caller's actual contract explicit at the call
  site instead of hidden in an argument.

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
