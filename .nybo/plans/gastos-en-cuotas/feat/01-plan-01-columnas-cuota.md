# T1 — `Gasto` guarda grupo/número/total de cuota

## Scope
- `src/db/models/gasto.py` — 3 columnas nuevas.
- `src/db/migrations/0008_gasto_cuotas.py` (nuevo).
- `src/db/migrate.py` — agregar `0008` a `_MIGRACIONES`.

## Changes
**Data Layer**
- `Gasto`: agregar
  ```python
  cuota_grupo_id = Column(GUID(), nullable=True)
  cuota_numero = Column(Integer, nullable=True)
  cuota_total = Column(Integer, nullable=True)
  ```
- Migración `0008_gasto_cuotas.py`: `ALTER TABLE gastos ADD COLUMN IF
  NOT EXISTS cuota_grupo_id UUID`, ídem `cuota_numero`/`cuota_total`
  como `INTEGER` — mismo patrón aditivo que `0006`/`0007`.
- Registrar `0008_gasto_cuotas` en `_MIGRACIONES`, después de `0007`
  (si `invitar-miembro-pendiente` ya la agregó; si no, ajustar el
  número al siguiente realmente libre en `migrate.py` al momento de
  implementar — no asumir el número a ciegas).

## Design Rationale
Tres columnas simples en vez de una tabla nueva — no hay necesidad de
una entidad "grupo de cuotas" separada porque nada más que estos 3
valores se necesita para reconstruir la relación entre cuotas de una
misma compra.

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] Suite completa en verde con el modelo actualizado.
- [ ] Migración corre limpia e idempotente contra Postgres real (misma
      técnica de base temporal que `postgres_migrations.test.py`).

## Interfaces Produced
- `Gasto.cuota_grupo_id`, `Gasto.cuota_numero`, `Gasto.cuota_total` — todos `Optional`.

## Standalone Verifiable
Sí.
