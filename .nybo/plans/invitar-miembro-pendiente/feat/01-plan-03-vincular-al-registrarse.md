# T3 — `registrar_usuario` vincula las membresías pendientes

## Scope
- `src/services/miembro_service.py` — nueva función `vincular_membresias_pendientes(session, usuario_id, email)`.
- `src/services/auth_service.py` — `registrar_usuario`: llamar a la función anterior tras el commit del Usuario.
- `tests/integration/api/miembro_invitacion_pendiente.test.py` — TC-003, TC-004, TC-005.

## Changes
**Service Logic**
- `miembro_service.py`: nueva función
  `vincular_membresias_pendientes(session, usuario_id: UUID, email: str) -> None`
  — recibe una sesión ya abierta (no abre la suya propia, a diferencia
  del resto de las funciones de este módulo: se ejecuta DENTRO de la
  transacción de `registrar_usuario`, para que la creación del Usuario y
  la vinculación de sus membresías sean atómicas). Busca
  `Miembro.email_invitacion == email AND Miembro.usuario_id IS NULL` y
  les asigna `usuario_id`.
- `auth_service.py`: importar `vincular_membresias_pendientes`; en
  `registrar_usuario`, después de `session.commit()`/`session.refresh(usuario)`
  y antes del `return`, llamar
  `vincular_membresias_pendientes(session, usuario.id, email_normalizado)`
  seguido de un segundo `session.commit()` para esa vinculación.

## Design Rationale
Pasar la `session` en vez de que la función abra la suya (patrón
distinto al resto de `miembro_service.py`, documentado explícitamente
en el docstring de la función nueva) porque acá SÍ hace falta que
comparta la transacción del llamador — es la única función de este
servicio pensada para ser invocada desde otro servicio, no desde una
ruta HTTP.

## Dependencies
T1 — necesita la columna `email_invitacion`. Independiente de T2 en el
sentido de que no toca el mismo código, pero conceptualmente es "la
otra mitad" del mismo flujo.

## Done When
- [ ] TC-003, TC-004, TC-005 pasan.
- [ ] `pytest tests/` completo sigue en verde.

## Interfaces Produced
- `vincular_membresias_pendientes` — `{name: "vincular_membresias_pendientes", signature: "(session, usuario_id: UUID, email: str) -> None", kind: "function"}`

## Interfaces Consumed
- `Miembro.email_invitacion` (T1)

## Standalone Verifiable
Sí — TC-003/004/005 verifican el flujo de registro completo vía la API
de `/auth/registro`, con membresías pendientes sembradas de antemano.
