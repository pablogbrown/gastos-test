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

## Gotchas
<!-- Things that tripped us up -->
