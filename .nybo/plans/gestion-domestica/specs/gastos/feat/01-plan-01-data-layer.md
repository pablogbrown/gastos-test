# Task 1 — Data Layer: Gasto, Categoría y Participantes

## Scope
- `src/db/models/gasto.py`
- `src/db/models/categoria.py`
- `src/db/migrations/0002_gastos.py`

## Changes
### Data Layer
- Tabla `categorias`: id, casa_id (fk), nombre. Seed inicial con las 8 categorías de ejemplo del documento (Supermercado, Servicios, Alquiler, Limpieza, Mantenimiento, Mascotas, Comida, Otros).
- Tabla `gastos`: id, casa_id (fk), descripcion, importe (numeric), fecha, pagado_por (fk miembro), categoria_id (fk).
- Tabla `gasto_participantes`: gasto_id (fk), miembro_id (fk), monto_correspondiente (numeric) — clave compuesta (gasto_id, miembro_id).

## Design Rationale
Modelar la participación como tabla propia (`gasto_participantes`) en vez de un array embebido permite calcular balances con una simple agregación SQL y mantiene la integridad referencial hacia Miembro.

## Dependencies
Requiere que existan las tablas `casas` y `miembros` de la spec `casas-miembros` (dependencia entre specs, no entre tasks de esta spec).

## Done When
- [ ] TC-001, TC-006 verificados contra el esquema (inserción válida, suma de participantes = importe).
- [ ] Seed de categorías corre sin duplicar en casas ya existentes.
- [ ] Migración corre limpia.

## Interfaces Produced
- `{name: "Gasto", signature: "class Gasto(id, casa_id, descripcion, importe, fecha, pagado_por, categoria_id)", kind: "class"}`
- `{name: "Categoria", signature: "class Categoria(id, casa_id, nombre)", kind: "class"}`
- `{name: "GastoParticipante", signature: "class GastoParticipante(gasto_id, miembro_id, monto_correspondiente)", kind: "class"}`

## Standalone Verifiable
Sí, contra una base con casas/miembros ya sembrados.
