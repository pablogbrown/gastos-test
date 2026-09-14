# Progress — Ranking y dashboard muestran UUIDs crudos

## Checklist

### Tasks
- [x] T1 — `Ranking`/`InicioCasa` resuelven nombre de miembro

### Verify
- [x] Verificación end-to-end de la spec
- [x] **Outcome smoke test**

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Ranking muestra el nombre del miembro
- [x] `[TC-002]` *[UNIT]* — Ranking usa fallback al id si el miembro no está en la lista
- [x] `[TC-003]` *[UNIT]* — InicioCasa muestra el nombre en tareas completadas recientes

#### Outcome Smoke Test
**Latest:** observed — screen: observed · API: n/a — outcome not an API fact — registrado + login, casa existente, tarea creada/completada, Ranking e Inicio ambos muestran "Administrador" (no UUID), incluida la tarjeta "Ranking" propia de Inicio (fix agregado por deviation, ver Judgment J001).

## Decisions
- [ ] `[D001]` — Sin coverage tool ni suite de integración configurados en este proyecto. Recomendación: `/nybo-brownfield-bootstrap --quality`.

## Completion Summary
T1 implementado (TDD): `Ranking.tsx`/`InicioCasa.tsx` reciben `miembros` y resuelven nombre por id (fallback al UUID crudo), igual patrón que `Gastos.tsx`/`Balance.tsx`. Deviation en el mismo pase: la tarjeta "Ranking" propia de `InicioCasa` (no nombrada en el spec) tenía el mismo bug — se corrigió con el mismo helper. Verify: build/tests en verde (61/61), smoke visual en vivo confirmado (docker `make up`) sobre las 3 ubicaciones. Coverage/integración no configurados en el proyecto (no bloqueante).

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 1 task, 3 test cases. |
| 2 | 2026-09-14 | verify | verified | observed | Build/tests green (61/61); live smoke on Ranking + Inicio (both cards) confirmed via docker `make up`; 1 non-blocking decision (D001, quality tools). |
