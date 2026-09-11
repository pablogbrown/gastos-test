# Progress — Autenticación Frontend

## Checklist

### Tasks
- [ ] T1 — Pantallas Login y Registro
- [ ] T2 — Sesión JWT: guardar, enviar, logout automático en 401
- [ ] T3 — Selector de casas y gate del shell existente
- [ ] T4 — Adaptar tests existentes y documentación

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — Sin JWT guardado se muestra Login
- [ ] `[TC-002]` *[UNIT]* — Registro válido llama a la API y termina en Login
- [ ] `[TC-003]` *[UNIT]* — Requests posteriores al login incluyen Authorization Bearer
- [ ] `[TC-004]` *[UNIT]* — Un 401 dispara logout automático
- [ ] `[TC-005]` *[UNIT]* — Usuario con 2 casas ve el selector
- [ ] `[TC-006]` *[UNIT]* — Cerrar sesión borra el JWT y vuelve a Login
- [ ] `[TC-007]` *[E2E]* — Flujo completo registro→login→crear casa→navegar shell

## Completion Summary
Not yet started.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 7 test cases. |
