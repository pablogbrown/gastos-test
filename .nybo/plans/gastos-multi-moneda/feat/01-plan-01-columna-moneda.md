# T1 — `Gasto`/`Suscripcion` guardan `moneda`; migración

## Scope
- `src/db/models/gasto.py` — 1 columna nueva.
- `src/db/models/suscripcion.py` — 1 columna nueva.
- `src/db/migrations/0010_gasto_suscripcion_moneda.py` (nuevo).
- `src/db/migrate.py` — agregar `0010` a `_MIGRACIONES`.

## Changes
**Data Layer**
- `Gasto`: agregar `moneda = Column(String(3), nullable=False, default="ARS")`.
- `Suscripcion`: agregar `moneda = Column(String(3), nullable=False, default="ARS")`.
- Migración `0010_gasto_suscripcion_moneda.py`: `ALTER TABLE gastos ADD
  COLUMN IF NOT EXISTS moneda VARCHAR(3) NOT NULL DEFAULT 'ARS'`, ídem
  para `suscripciones` — mismo patrón aditivo que `0006`/`0007`/`0008`.
- Registrar `0010_gasto_suscripcion_moneda` en `_MIGRACIONES`, después
  de `0009` (verificar al implementar que sigue siendo el próximo
  número libre — no asumir a ciegas).

## Design Rationale
Una sola columna `moneda` en ambas tablas, sin tabla de "monedas"
separada — solo hay 2 valores válidos, hardcodeados como constante en
el servicio (T2), no como una entidad de catálogo.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] Suite completa en verde con los modelos actualizados.
- [ ] Migración corre limpia e idempotente contra Postgres real (base
      temporal, nunca `DATABASE_URL` directo).

## Interfaces Produced
- `Gasto.moneda: str` (default `"ARS"`).
- `Suscripcion.moneda: str` (default `"ARS"`).

## Standalone Verifiable
Sí.
