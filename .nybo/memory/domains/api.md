# Domain: api

api domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-15 | feature: tarjetas-credito | confidence: medium | verified: 2026-09-15 -->
- [API-01] `DashboardOut`'s own top-level fields use a camelCase `alias`
  (e.g. `gastos_recientes` -> `gastosRecientes`, `tarjetas_con_alerta` ->
  `tarjetasConAlerta`) so the frontend consumes camelCase keys for the
  dashboard's own section names. The individual objects INSIDE those
  lists (e.g. each `Gasto`/`TarjetaAlertaOut`) keep their own fields in
  plain snake_case, unaliased — `RankingEntryOut.miembro_id -> miembroId`
  is the one existing exception (its own schema declares that alias
  directly), not a rule to generalize to every nested schema. When adding
  a new field to `DashboardOut` or a schema nested inside it, alias only
  the new top-level container field; leave the nested object's own field
  names as-is unless that specific nested schema already aliases them.

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- [APIP-02] added: 2026-09-23 | feature: tienda-accesorios | confidence: medium | verified: 2026-09-23 -->
- [APIP-02] `ValidationError` maps to 400 everywhere in this project by
  default — but a single route MAY map one specific, named condition of
  that same exception type to a different code when spec.md's own
  Contracts table documents it explicitly (e.g.
  `POST .../accesorios/{id}/comprar`, spec `tienda-accesorios`: "402 si
  saldo insuficiente" — `comprar_accesorio` raises a plain
  `ValidationError`, and only THIS route's own `except ValidationError`
  clause maps it to 402, with a comment naming the deviation). This is a
  per-route override on top of the general convention, never a
  redefinition of it — every other `ValidationError` in this same route
  (or any other route) still maps to 400 unless spec.md documents its
  own distinct code for that specific condition too. Prefer this over
  inventing a new exception subclass just to carry a status code that
  only one call site needs.

<!-- added: 2026-09-15 | feature: importar-resumen-tarjeta | confidence: medium | verified: 2026-09-15 -->
- [APIP-01] First file-upload endpoint in this project
  (`POST .../resumen`, `src/api/routes/tarjetas.py`): a plain FastAPI
  `archivo: UploadFile` parameter (no `= File(...)` default needed),
  read via `await archivo.read()` inside an `async def` route handler —
  every other route in this project is synchronous `def`, this is the
  first `async def` too, required because `UploadFile.read()` is a
  coroutine. Requires `python-multipart` as a runtime dependency (not
  bundled with `fastapi` itself) — install it before adding a second
  upload endpoint, don't assume it's already present. A recognized-but-
  invalid-content error (the file parses as the right MIME type but the
  wrong internal format) maps to 422, kept distinct from a plain
  `ValidationError` (400, a malformed individual field) — see
  `exceptions.py`'s `PdfFormatoNoReconocidoError` docstring for the
  full 400-vs-422 rationale, reusable for any future "recognized
  container, unrecognized content" upload.

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-18 | feature: gamificacion-puntos | confidence: medium | verified: 2026-09-18 -->
- [APIG-01] There is no `GET /casas/{casa_id}` single-casa endpoint —
  only `GET /casas/mias` (list) and `GET /casas/{casa_id}/miembros`
  (its members). A screen that lets an admin edit one scalar field on
  `Casa` itself (e.g. `Miembros.tsx`'s "Meta de puntos mensual") has no
  cheap way to pre-fill the control with the CURRENT value on mount —
  `actualizar_meta_puntos`'s own PATCH response has it, but only after
  a save, not before. Accepted as write-only (a field + a save button,
  no pre-fill) for `gamificacion-puntos` rather than adding a new GET
  endpoint just for this; revisit if a second casa-level scalar needs
  the same treatment.
