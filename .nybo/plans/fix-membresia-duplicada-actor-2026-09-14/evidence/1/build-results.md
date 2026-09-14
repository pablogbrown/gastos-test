---
feature: fix-membresia-duplicada-actor-2026-09-14
schema: build-results/2
cycle: 1
updated: '2026-09-14T16:31:30.354Z'
exit: in-progress
verdict: pending
judgment:
  entries: 1
---
### Goal

T1: agregar_miembro rechaza una segunda fila Miembro activa para el mismo (casa_id, usuario_id) en la misma casa (REQ-001). T2: resolver_actor_en_casa reemplaza .one_or_none() por .order_by(Miembro.id).first() para nunca crashear con MultipleResultsFound ante duplicados preexistentes (REQ-002).

### Judgment

- T1 implementado con .one_or_none() (antes del fix nunca puede existir >1 fila activa para el mismo (casa_id, usuario_id), por diseño — la validación recién se agrega). T2 implementado exactamente como especifica 01-plan-02-endurecer-resolver-actor.md: order_by(Miembro.id).first() en vez de .one_or_none(), sin agregar columna de timestamp (Miembro no la tiene) — orden estable por id, no arbitra cuál membresía es la 'correcta', solo elimina el 500. No hubo desviaciones del run-plan.json ni decisiones fuera de la autoridad de trust semi-autonomous (spec-deviation): ambos cambios siguen el contrato tal cual estaba escrito.
