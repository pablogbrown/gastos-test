# T2 — `agregar_miembro` crea una membresía pendiente

## Scope
- `src/services/miembro_service.py` — `agregar_miembro`.
- `tests/integration/api/miembro_invitacion_pendiente.test.py` (nuevo) — TC-001, TC-002, TC-006.

## Changes
**Service Logic**
- Reemplazar el `if usuario is None: raise NotFoundError(...)` por: si
  no existe un Usuario con ese email, seguir el flujo de alta creando el
  `Miembro` con `usuario_id=None`, `email_invitacion=email_normalizado`.
- El chequeo "ya es miembro de esta casa" (REQ-003, hoy filtra por
  `Miembro.usuario_id == usuario.id`) necesita una segunda rama cuando
  `usuario is None`: buscar por `Miembro.casa_id == casa_id,
  Miembro.email_invitacion == email_normalizado, Miembro.usuario_id.is_(None)`
  y rechazar con el mismo `ValidationError` si ya existe.
- Cuando `usuario` SÍ existe (camino ya soportado hoy), el comportamiento
  no cambia — vinculación inmediata, `email_invitacion` puede guardarse
  también acá (no es obligatorio para ese camino, pero mantenerlo
  consistente no cuesta nada).

## Design Rationale
Cambio quirúrgico dentro de la misma función — no se introduce una
función nueva para "alta pendiente" porque el resto del flujo (validar
nombre/identificación, chequear duplicados, insertar, registrar
actividad) es idéntico entre ambos caminos; solo cambia de dónde sale
`usuario_id`.

## Dependencies
T1 — necesita la columna `email_invitacion`.

## Done When
- [ ] TC-001, TC-002, TC-006 pasan.
- [ ] `pytest tests/` completo sigue en verde.

## Interfaces Produced
Ninguna nueva — `agregar_miembro` mantiene su firma pública.

## Standalone Verifiable
Sí.
