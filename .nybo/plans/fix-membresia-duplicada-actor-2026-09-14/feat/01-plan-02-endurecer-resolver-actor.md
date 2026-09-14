# T2 — Endurecer `resolver_actor_en_casa` contra duplicados preexistentes

## Scope
- `src/services/miembro_service.py` — `resolver_actor_en_casa`: reemplazar `.one_or_none()` por una resolución determinística que tolera duplicados.
- `tests/integration/api/miembro_membresia_unica.test.py` — agrega TC-003, TC-004 (mismo archivo que T1, mismo concern de membresía).

## Changes
**Service Logic**
- Cambiar la query de
  `filter(casa_id, usuario_id, activo=True).one_or_none()` a
  `filter(casa_id, usuario_id, activo=True).order_by(Miembro.id).first()`.
  `.first()` nunca lanza `MultipleResultsFound` — devuelve `None` si no
  hay filas, o la primera según el orden, sin importar cuántas existan.
  El resto de la función (chequeo `None` → `PermissionDeniedError`) no
  cambia.
- `Miembro` no tiene columna de fecha de creación (confirmado en
  `src/db/models/miembro.py`) — no se agrega una en este fix (fuera de
  scope: requeriría una migración solo para un caso defensivo que, tras
  T1, no debería volver a ocurrir). `order_by(Miembro.id)` da un orden
  estable y determinístico (mismo resultado en cada corrida) aunque
  arbitrario respecto a cuál membresía es la "correcta" — eso es
  aceptable porque el objetivo de T2 es eliminar el 500, no arbitrar
  intención de negocio. Documentar este comentario inline en el código.

## Design Rationale
Defensa en profundidad (Liskov-safe, no rompe el contrato de la
función: sigue devolviendo `Miembro.id` o lanzando
`PermissionDeniedError`). No revierte T1 — T1 evita que se CREEN nuevos
duplicados; T2 asegura que un duplicado que de todos modos exista (dato
previo al fix, o cualquier vía no anticipada) nunca vuelva a crashear un
request con 500.

## Dependencies
Ninguna estricta sobre T1 (query distinta), pero se implementa después
en el mismo PR porque comparte archivo de test y el orden T1→T2 refleja
"cerrar la entrada, después blindar la lectura".

## Done When
- [ ] TC-003 y TC-004 pasan (requieren sembrar el duplicado directo en la
      sesión de test, insertando ambas filas por SQLAlchemy directo —
      bypaseando la validación de T1 a propósito, como haría un dato
      preexistente a este fix).
- [ ] `pytest tests/` completo sigue en verde.
- [ ] Ningún llamador existente de `resolver_actor_en_casa` cambia de
      comportamiento en el caso sin duplicados (regresión cero).

## Interfaces Produced
Ninguna nueva — firma pública de `resolver_actor_en_casa` sin cambios.

## Standalone Verifiable
Sí — TC-003/TC-004 verifican este cambio sembrando el estado duplicado
directamente en la sesión de test, sin depender de que T1 haya fallado
en producción.
