# Progress — Casas y Miembros

## Checklist

### Tasks
- [ ] T1 — Data Layer: Casa y Miembro
- [ ] T2 — Service Layer: Casas, Miembros y Roles
- [ ] T3 — API Routes: Casas y Miembros
- [ ] T4 — UI: Creación de Casa y Gestión de Miembros

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — Crear casa con nombre válido asigna admin al creador
- [ ] `[TC-002]` *[UNIT]* — Crear casa sin nombre es rechazado
- [ ] `[TC-003]` *[UNIT]* — Admin agrega miembro válido
- [ ] `[TC-004]` *[UNIT]* — Identificación duplicada dentro de la misma casa es rechazada
- [ ] `[TC-005]` *[INTEGRATION]* — Desactivar miembro preserva su historial
- [ ] `[TC-006]` *[UNIT]* — Miembro sin rol admin no puede agregar miembros
- [ ] `[TC-007]` *[UNIT]* — Admin consulta todos los gastos sin restricción
- [ ] `[TC-008]` *[INTEGRATION]* — Usuario sin casa no puede registrar gasto
- [ ] `[TC-009]` *[INTEGRATION]* — Dos casas mantienen datos independientes

## Completion Summary
Not yet started.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 9 test cases. |
