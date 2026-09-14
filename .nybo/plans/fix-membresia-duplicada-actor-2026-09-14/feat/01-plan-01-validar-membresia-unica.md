# T1 — Validar membresía única por Usuario en `agregar_miembro`

## Scope
- `src/services/miembro_service.py` — `agregar_miembro`: nueva validación antes del insert.
- `tests/integration/api/miembro_membresia_unica.test.py` (nuevo) — TC-001, TC-002.

## Changes
**Service Logic**
- Antes de construir el `Miembro` nuevo (después de resolver `usuario`
  por email, antes del chequeo de `identificacion` duplicada), agregar
  una consulta: `session.query(Miembro).filter(Miembro.casa_id == casa_id,
  Miembro.usuario_id == usuario.id, Miembro.activo.is_(True)).one_or_none()`.
  Si devuelve una fila, `raise ValidationError("El usuario ya es miembro
  activo de esta casa.")` (400, mismo patrón que las validaciones
  existentes de esta función).

## Design Rationale
Single Responsibility: la validación de unicidad de membresía vive junto
a las otras validaciones de `agregar_miembro` (nombre, identificación,
email), en el mismo servicio, sin introducir una nueva capa. Esta
consulta usa `.one_or_none()` a propósito — antes de este fix, por
diseño, nunca puede haber más de una fila activa (recién se está
validando eso); no es el mismo caso que T2, que blinda contra datos que
YA rompieron esa invariante.

## Dependencies
Ninguna — es la primera tarea, cierra la puerta de entrada del bug antes
de que T2 blinde la lectura.

## Done When
- [ ] TC-001 y TC-002 pasan.
- [ ] `pytest tests/` completo sigue en verde (127+ tests previos).
- [ ] Tipos/build sin errores.

## Interfaces Produced
Ninguna nueva — `agregar_miembro` mantiene su firma pública exacta
(`casa_id, nombre, identificacion, email_usuario, actor`).

## Standalone Verifiable
Sí — TC-001/TC-002 verifican este cambio de forma completa e
independiente de T2.
