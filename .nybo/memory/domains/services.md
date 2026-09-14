# Domain: services

services domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-14 | feature: fix-membresia-duplicada-actor-2026-09-14 | confidence: high | verified: 2026-09-14 -->
- [SERV-01] Business-invariant uniqueness checks (e.g. "at most one active `Miembro` per `(casa_id, usuario_id)`") are validated in the service layer, before the write, mirroring how duplicate-`identificacion` is already checked — never as a database `UNIQUE` constraint. This keeps the check colocated with the other `agregar_miembro`-style validations and avoids a schema migration for a service-level rule; see `.nybo/plans/fix-membresia-duplicada-actor-2026-09-14/feat/00-overview.md`'s Tradeoffs for the explicit reasoning.

## Patterns
<!-- Reusable patterns specific to this domain -->

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-14 | feature: fix-membresia-duplicada-actor-2026-09-14 | confidence: high | verified: 2026-09-14 -->
- [SERVG-01] A `.one_or_none()` query that assumes "at most one row" for an invariant enforced only in the service layer (no DB constraint) is a latent crash risk: if that invariant is ever violated (preexisting data, an unanticipated write path), SQLAlchemy raises `MultipleResultsFound`, which nothing in the call chain catches — it surfaces as an unhandled 500 (`resolver_actor_en_casa`'s original bug). When a query reads state that must never crash even if the invariant it depends on was broken by data that predates the guard, prefer `.order_by(<stable-column>).first()` — never raises, and gives a deterministic, repeatable result regardless of how many rows actually exist.
