# Solution Overview — Membresía duplicada crashea la resolución de actor

## File Index
- [../spec.md](../spec.md)
- [10-verify.md](10-verify.md)
- [99-progress.md](99-progress.md)

### Task Index

| Task | File | Description | Dependencies |
|---|---|---|---|
| T1 | [01-plan-01-validar-membresia-unica.md](01-plan-01-validar-membresia-unica.md) | `agregar_miembro` rechaza una segunda membresía activa para el mismo Usuario en la misma casa | — |
| T2 | [01-plan-02-endurecer-resolver-actor.md](01-plan-02-endurecer-resolver-actor.md) | `resolver_actor_en_casa` resuelve duplicados preexistentes de forma determinística en vez de crashear | — |

## Problema y solución
- `agregar_miembro` solo valida `identificacion` duplicada dentro de la
  casa — nunca chequea si el `Usuario` (por `usuario_id`, resuelto del
  email) ya tiene otra fila `Miembro` activa ahí.
- `resolver_actor_en_casa` asume `.one_or_none()` sobre
  `filter(casa_id, usuario_id, activo=True)` — si esa asunción se rompe
  (por el bug anterior, o por datos ya existentes), SQLAlchemy lanza
  `MultipleResultsFound`, no manejada por ningún `except` de la cadena,
  y FastAPI la convierte en un 500 genérico.
- Fix: T1 cierra la puerta de entrada (nueva duplicación). T2 blinda la
  lectura para que un duplicado *ya presente* en la base (de antes del
  fix, o de una carrera no identificada) nunca vuelva a crashear un
  request — elige la fila `Miembro` más antigua por `creado_en`.

## Arquitectura
Sin cambios de arquitectura — ambos cambios son de validación/consulta
dentro de `src/services/miembro_service.py`, el mismo servicio que ya
posee toda la lógica de membresía (T2 de `casas-miembros`, extendido por
`usuarios-auth`).

## Data Model
Sin cambios de esquema. No se agrega una constraint UNIQUE de base de
datos en este fix — la validación vive en el service layer, consistente
con cómo ya se valida `identificacion` duplicada (vía `IntegrityError`
catch, no vía constraint explícita en el modelo). Ver Tradeoffs.

## Tradeoffs
- **Validación en service layer vs. constraint UNIQUE en Postgres**: se
  eligió service layer para no requerir una migración de esquema en un
  fix de severidad crítica que debe poder mergearse rápido, y porque
  T2 ya cubre el caso "duplicado ya existe en la base" sin depender de
  que la constraint exista. Una constraint UNIQUE `(casa_id, usuario_id)
  WHERE activo` queda como mejora de robustez futura (no bloqueante).
- **Orden estable por `Miembro.id` (T2) vs. agregar una columna de fecha
  de creación**: `Miembro` no tiene columna de timestamp hoy; agregar una
  solo para este caso defensivo (que tras T1 no debería volver a
  ocurrir) es una migración innecesaria para la severidad y urgencia de
  este fix. Un orden estable por `id` no arbitra intención de negocio,
  solo garantiza que el sistema nunca crashea y siempre responde igual.

## API/Data Contracts
- `POST /casas/{casa_id}/miembros`: sin cambio de forma en request ni
  response. Nuevo caso de error: 400 `"El usuario ya es miembro activo de
  esta casa."` cuando el Usuario objetivo ya tiene una fila `Miembro`
  activa en `casa_id`.
- Toda ruta que depende de `resolver_actor_en_casa` (`casas.py`,
  `gastos.py`, `tareas.py`, `dashboard.py`): sin cambio de forma; deja de
  poder devolver 500 por esta causa específica.
