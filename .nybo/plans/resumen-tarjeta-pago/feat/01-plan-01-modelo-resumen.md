# T1 — Modelo ResumenTarjeta + columna Gasto.resumen_id + migración

## Scope
- `src/db/models/resumen_tarjeta.py` (nuevo): modelo `ResumenTarjeta`
  tal como está descripto en `feat/00-overview.md` § Data Model.
- `src/db/models/gasto.py`: agregar `resumen_id = Column(GUID(),
  nullable=True)` (plano, sin `ForeignKey()` a nivel de modelo — mismo
  criterio que `tarjeta_id`/`suscripcion_id` en ese mismo archivo;
  documentar el motivo en el docstring de la clase, siguiendo el
  mismo estilo que los bloques ya existentes ahí).
- `src/db/migrations/0019_resumen_tarjeta.py` (nuevo):
  1. Crear `resumenes_tarjeta` (FK real a `tarjetas_credito`, ver
     overview).
  2. `ALTER TABLE gastos ADD COLUMN IF NOT EXISTS resumen_id CHAR(36)
     REFERENCES resumenes_tarjeta(id)` (SQL crudo, Postgres — mismo
     patrón que `0018_mantenimiento_autos.py` con `auto_id`).
- `src/db/migrate.py`: agregar `"0019_resumen_tarjeta"` al final de
  `_MIGRACIONES`.

## Dependencies
Ninguna (task raíz).

## Done When
- `run_migrations(engine)` corre limpio contra una base Postgres nueva
  y corrido dos veces seguidas no lanza excepción (idempotente).
- `Gasto` importa y funciona sin romper ningún test existente de
  `gasto_service`/`resumen_importer_service`.
- Test de integración de migraciones (`tests/integration/db/
  postgres_migrations.test.py`, extender el existente con la nueva
  tabla) verifica que `resumenes_tarjeta` existe y que `gastos.
  resumen_id` referencia correctamente.

## Verifiability
INTEGRATION — `tests/integration/db/postgres_migrations.test.py`.
