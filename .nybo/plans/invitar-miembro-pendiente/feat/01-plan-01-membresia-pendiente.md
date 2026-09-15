# T1 — `Miembro` guarda el email invitado

## Scope
- `src/db/models/miembro.py` — nueva columna `email_invitacion`.
- `src/db/migrations/0007_miembro_email_invitacion.py` (nuevo).
- `src/db/migrate.py` — agregar `0007` a `_MIGRACIONES`.

## Changes
**Data Layer**
- `Miembro`: agregar `email_invitacion = Column(String, nullable=True)`.
- Nueva migración `0007_miembro_email_invitacion.py`, mismo patrón que
  `0006` (una migración por cambio incremental, sin motor de migraciones
  con downgrade automático — `ALTER TABLE miembros ADD COLUMN IF NOT
  EXISTS email_invitacion VARCHAR` para Postgres; en SQLite (tests) esta
  columna ya se crea al vuelo vía `create_all` normal, no necesita ALTER).
- Registrar `0007_miembro_email_invitacion` en `_MIGRACIONES` de
  `migrate.py`, después de `0006`.

## Design Rationale
Mismo patrón exacto que `0006_miembro_desactivado_enum_value.py`: una
migración incremental y aditiva, nunca recrear la tabla. `ADD COLUMN IF
NOT EXISTS` es idempotente por diseño (relevante porque `main.py` corre
`run_migrations` en cada arranque).

## Dependencies
Ninguna — primera tarea.

## Done When
- [ ] La suite completa (`pytest tests/`) sigue en verde con el modelo
      actualizado.
- [ ] La migración corre limpia contra Postgres real (smoke manual o
      test de integración, ver `10-verify.md`).

## Interfaces Produced
- `Miembro.email_invitacion` — `{name: "email_invitacion", signature: "Optional[str]", kind: "export"}`

## Standalone Verifiable
Sí — se verifica que la columna existe y acepta `NULL`/valores, sin
depender de T2/T3.
