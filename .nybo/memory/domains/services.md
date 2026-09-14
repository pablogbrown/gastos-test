# Domain: services

services domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-14 | feature: fix-historial-desactivacion-miembro | confidence: high | verified: 2026-09-14 -->
- [SERV-01] `registrar_actividad` (activity-log hook, `actividad_service.py`)
  is called only AFTER the triggering business operation's own `commit`
  succeeds, never before and never on a failure/exception path — so an
  activity entry never describes something that ultimately didn't happen.
  Established by `gasto_service.registrar_gasto`/`tarea_service.crear_tarea`/
  `completar_tarea`; `miembro_service.agregar_miembro`/`desactivar_miembro`
  now follow the same shape. Any new service action that should appear in
  the Historial de actividad calls this hook the same way, right after its
  own commit.

## Patterns
<!-- Reusable patterns specific to this domain -->

## Gotchas
<!-- Things that tripped us up -->
