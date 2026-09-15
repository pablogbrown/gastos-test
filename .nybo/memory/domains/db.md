# Domain: db

db domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- [DBP-01] added: 2026-09-15 | feature: gastos-multi-moneda | confidence: high | verified: 2026-09-15 -->
- [DBP-01] A `NOT NULL` column with a simple default (a single constant,
  not something dynamic) is declared as a plain Python-side
  `Column(..., nullable=False, default="ARS")` — never `server_default`
  — consistent across `Suscripcion.activa`, and now
  `Gasto.moneda`/`Suscripcion.moneda`. This is deliberate, not an
  oversight: it means the default only applies when a row is inserted
  through the ORM. Confirmed live (spec `gastos-multi-moneda`, T1) that
  this has a real split behavior depending on how the column reaches an
  existing Postgres database: (a) a brand-new table created by
  `create_all` (a fresh ephemeral Postgres, or any SQLite test) gets the
  column with no SQL-level default at all — a raw-SQL `INSERT` omitting
  it would fail; (b) a column added to an *already-existing* table via a
  migration's `ALTER TABLE ... ADD COLUMN ... DEFAULT 'ARS'` (the
  additive-migration pattern, see `0008`-`0010`) DOES leave a real
  SQL-level default in place (`information_schema.columns.column_default`
  shows `'ARS'::character varying`) — because the ALTER statement itself
  says so, regardless of the model's own Python-only default. Never
  assume "the model doesn't declare `server_default`" implies "no
  Postgres-level default exists anywhere" — check which path created the
  column before reasoning about raw-SQL insert safety.

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

<!-- added: 2026-09-15 | feature: importar-resumen-tarjeta | confidence: high | verified: 2026-09-15 -->
- [DBG-04] Even after correctly following DBG-02/DBG-03 (plain `Column`,
  no model-level `ForeignKey()`, real constraint added via a later
  migration's raw `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...
  REFERENCES`), the FK still silently never attaches on a database
  created FRESH by `run_migrations` in one pass (an ephemeral test
  Postgres, or any brand-new environment) — because the table's OWN
  creating migration (e.g. `0002_gastos.py`'s `create_all(tables=
  [Gasto.__table__])`) reads `Gasto.__table__` from the CURRENT, live
  model class, which already includes every column ever added to
  `Gasto` (including the newest one) at the time that early migration
  runs — the column exists from the very first `create_all`, so the
  later migration's `ADD COLUMN IF NOT EXISTS` is a no-op and its
  `REFERENCES` clause never executes. This is invisible to a test that
  only checks "does the column exist" — it does — and only surfaces by
  additionally checking `inspector.get_foreign_keys(...)` after a
  from-scratch `run_migrations()` run. The `REFERENCES` clause is NOT
  dead code: it's exactly what fires on the real, non-fresh path — an
  existing deployment whose `gastos` table predates the new column (a
  persisted `docker-compose` volume, a real production database) — as
  confirmed live against this project's own persisted dev DB, where the
  same column DID get a real `gastos_tarjeta_id_fkey`. `suscripcion_id`
  (`0009`) has had this exact same fresh-DB gap since it was added;
  nobody had checked for it explicitly until this spec's migration test
  started asserting FK presence. When verifying a new FK column, always
  check BOTH paths — a from-scratch `run_migrations()` AND a database
  that already had the owning table before this migration — a from-
  scratch-only check reports a false negative FOR THE COLUMN'S FK even
  though the migration file is completely correct.

<!-- added: 2026-09-14 | feature: fix-historial-desactivacion-miembro | confidence: high | verified: 2026-09-14 -->
- [DB-01] Adding a new member to a `sqlalchemy.Enum(SomePythonEnum)` column
  (e.g. a new `TipoActividadEnum` value) is invisible on SQLite (the table
  is always recreated fresh from the current model in every test) but
  requires its own migration on Postgres: `create_all`/`checkfirst` never
  retrofits an *existing* native Postgres enum type with a new label.
  Without a companion `ALTER TYPE <type> ADD VALUE IF NOT EXISTS
  '<LABEL>'` migration, any environment where the owning table already
  existed before the enum grew (a persisted `docker-compose` volume, a
  real deployment) rejects the new value with
  `psycopg2.errors.InvalidTextRepresentation`, even though every test
  passes. The label to add is the enum member's **`.name`** (uppercase,
  e.g. `MIEMBRO_DESACTIVADO`), not its `.value` — SQLAlchemy stores
  Python enum members in a native Postgres enum column by name, not by
  value, by default. Run `ALTER TYPE ... ADD VALUE` outside any explicit
  transaction (`isolation_level="AUTOCOMMIT"`) for portability across
  Postgres versions. See `src/db/migrations/0006_miembro_desactivado_enum_value.py`
  and its regression test in `tests/integration/db/postgres_migrations.test.py`.

<!-- added: 2026-09-14 | feature: fix-membresia-duplicada-actor-2026-09-14 | confidence: high | verified: 2026-09-14 -->
- [DBG-01] The `rolenum` Postgres enum stores labels in UPPERCASE (`ADMIN`, `MEMBER`) even though `RolEnum`'s Python string values are lowercase (`"admin"`, `"member"`) — SQLAlchemy's `Enum` column maps the Python enum *member name*, not its `.value`, to the Postgres label. A raw SQL `INSERT`/seed against `miembros.rol` (bypassing the ORM, e.g. to simulate preexisting data in a test or a live smoke check) must use the uppercase label or it fails with `invalid input value for enum rolenum`.

<!-- added: 2026-09-15 | feature: gastos-suscripcion-mensual | confidence: high | verified: 2026-09-15 -->
- [DBG-02] Adding a new FK **column** to an existing model (e.g. `Gasto.suscripcion_id` pointing at a table created by a *later* migration) must NEVER declare it as a SQLAlchemy-level `Column(..., ForeignKey("new_table.id"))`. `run_migrations`/`main.py`'s startup hook imports migrations in strict order, and an earlier migration's `create_all(tables=[Gasto.__table__])` resolves every `ForeignKey` on that table against `Base.metadata` at that exact moment — if the referenced table's model hasn't been imported anywhere yet (it won't be, until the later migration's own module loads), this raises `sqlalchemy.exc.NoReferencedTableError`, on every engine (SQLite tests can accidentally dodge it only if some other already-collected test module happens to import the referenced model first — never rely on that). Fix: declare the column as a plain `Column(GUID(), nullable=True)` with no `ForeignKey()` (same pattern as the pre-existing `cuota_grupo_id`), and add the real DB-level constraint via raw SQL inside the LATER migration's own `upgrade()`, after that migration's own `create_all` has made the referenced table exist for real (`ALTER TABLE gastos ADD COLUMN IF NOT EXISTS suscripcion_id CHAR(36) REFERENCES suscripciones(id)`).
- [DBG-03] That raw `ALTER TABLE ... REFERENCES` must type the new column `CHAR(36)`, never native Postgres `UUID` — `GUID()` (`src/db/types.py`) always materializes as `CHAR(36)` on Postgres (portability with SQLite's lack of a native UUID type), so a `UUID`-typed FK column against a `CHAR(36)` primary key fails at `ALTER TABLE` time with `psycopg2.errors.DatatypeMismatch` ("Key columns ... are of incompatible types: uuid and character"). Same precedent as `0005_usuarios.py`'s `usuario_id CHAR(36) REFERENCES usuarios(id)`. This is invisible to the whole SQLite test suite (no real Postgres) and only surfaced restarting the dockerized backend against the real dev database — always restart/smoke-test the dockerized backend after any migration touching a FK, not just run the test suite.
