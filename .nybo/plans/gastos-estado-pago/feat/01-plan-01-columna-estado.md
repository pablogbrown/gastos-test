# T1 — `Gasto` guarda `estado`; migración

## Scope
- `src/db/models/gasto.py` — 1 columna nueva.
- `src/db/migrations/0013_gasto_estado.py` (nuevo).
- `src/db/migrate.py` — agregar `0013` a `_MIGRACIONES`.

## Changes
- `Gasto`: agregar `estado = Column(String, nullable=False, default="pagado")`.
- Migración `0013_gasto_estado.py`: `ALTER TABLE gastos ADD COLUMN IF
  NOT EXISTS estado VARCHAR NOT NULL DEFAULT 'pagado'` — mismo patrón
  aditivo que `0010`/`0011`/`0012`.
- Registrar `0013_gasto_estado` en `_MIGRACIONES`, después de `0012`
  (verificar al implementar que sigue siendo el próximo número libre).

## Design Rationale
Columna `String` simple, sin enum nativo de Postgres — mismo criterio
ya elegido para `moneda` (`gastos-multi-moneda`), evita el gotcha ya
documentado de valores de enum en mayúsculas por nombre de miembro.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] Suite completa en verde con el modelo actualizado.
- [ ] Migración corre limpia e idempotente contra Postgres real.

## Interfaces Produced
- `Gasto.estado: str` (default `"pagado"`).

## Standalone Verifiable
Sí.
