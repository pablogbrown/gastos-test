# Task 1 — Data Layer: Casa y Miembro

## Scope
- `src/db/models/casa.py` — modelo Casa.
- `src/db/models/miembro.py` — modelo Miembro (FK a Casa).
- `src/db/migrations/0001_casas_miembros.py` — migración inicial.

## Changes
### Data Layer
- Tabla `casas`: id (uuid pk), nombre (string, not null), creado_en (timestamp).
- Tabla `miembros`: id (uuid pk), casa_id (fk → casas.id), nombre (string, not null), identificacion (string, not null), rol (enum: admin|member, not null), activo (boolean, default true).
- Constraint único compuesto (casa_id, identificacion) para evitar duplicados dentro de una misma casa (REQ-002 / TC-004).

## Design Rationale
Separar Casa y Miembro en tablas propias respeta SRP: cada entidad tiene su propio ciclo de vida y reglas de validación (unicidad de identificación es propia de Miembro, no de Casa).

## Dependencies
Ninguna — primer task de la spec.

## Done When
- [ ] TC-001, TC-002, TC-004 pasan contra la capa de datos (constraints y defaults verificados).
- [ ] Migración corre limpia sobre una base vacía.
- [ ] Tipos exportados e importables desde `src/db/models`.

## Interfaces Produced
- `{name: "Casa", signature: "class Casa(id, nombre, creado_en)", kind: "class"}`
- `{name: "Miembro", signature: "class Miembro(id, casa_id, nombre, identificacion, rol, activo)", kind: "class"}`

## Standalone Verifiable
Sí — se puede probar el esquema y sus constraints sin la capa de servicio.
