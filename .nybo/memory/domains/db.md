# Domain: db

db domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

## Patterns
<!-- Reusable patterns specific to this domain -->

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-14 | feature: usuarios-auth | confidence: high | verified: 2026-09-14 -->
- Each migration's `TABLES` list (e.g. `src/db/migrations/0001_casas_miembros.py`)
  must explicitly include every table a FK in that migration points to,
  even one owned by a model created in a *later* migration. Importing the
  model only for its SQLAlchemy metadata side-effect (so the FK resolves)
  compiles fine and passes on SQLite, but silently never creates that
  table on a real Postgres run — the FK then fails at migrate time.
  Discovered when combining `usuarios-auth` (which added `Miembro.usuario_id`
  as a FK to a `usuarios` table created in migration `0005`) with
  `dockerize-local-env`'s real Postgres for the first time; invisible in
  every prior SQLite-only build/verify pass. Fixed by adding
  `Usuario.__table__` to migration `0001`'s own `TABLES` list. Whenever a
  new FK is added to an existing migration, verify against real Postgres
  (not just SQLite) before considering it verified.

<!-- added: 2026-09-14 | feature: fix-membresia-duplicada-actor-2026-09-14 | confidence: high | verified: 2026-09-14 -->
- [DBG-01] The `rolenum` Postgres enum stores labels in UPPERCASE (`ADMIN`, `MEMBER`) even though `RolEnum`'s Python string values are lowercase (`"admin"`, `"member"`) — SQLAlchemy's `Enum` column maps the Python enum *member name*, not its `.value`, to the Postgres label. A raw SQL `INSERT`/seed against `miembros.rol` (bypassing the ORM, e.g. to simulate preexisting data in a test or a live smoke check) must use the uppercase label or it fails with `invalid input value for enum rolenum`.
