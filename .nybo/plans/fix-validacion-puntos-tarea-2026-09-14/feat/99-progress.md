# Progress — Crear tarea sin puntos crea una tarea de 0 puntos

## Checklist

### Tasks
- [x] T1 — Enviar Puntos como ausente cuando el campo está vacío

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Puntos vacío dispara el error de negocio, no crea tarea
- [x] `[TC-002]` *[UNIT]* — Puntos con valor sigue creando la tarea normalmente

## Completion Summary
T1 implemented via TDD (red→green): `CrearTareaInput.puntos` relaxed to
`number | undefined`, `Tareas.tsx`'s `handleCrear` sends `undefined`
instead of `Number("")` when Puntos is empty. TC-001/TC-002 added and
green. Full suite (59/59), `npm run build`, `npm run lint` all clean.
One convention captured in `.nybo/memory/domains/frontend.md` (empty
numeric field → `undefined`, not `Number("")`, when the backend treats
absence as the validation trigger). No open decisions.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 1 task, 2 test cases. |
| 2 | 2026-09-14 | implement T1 | pass | — | TDD red→green: added TC-001/TC-002 to Tareas.test.tsx (red), fixed `CrearTareaInput.puntos` to `number \| undefined` and `handleCrear` to send `undefined` when Puntos is empty (green). Full suite 59/59 green, `npm run build` and `npm run lint` clean. |
| 3 | 2026-09-14 | verify | pass | n/a (manual docker smoke not run; AUTO gates authoritative) | Spec-level verify: full suite 59/59, build clean, lint clean, TC-001/TC-002 confirmed covering REQ-001/REQ-002 including direct request-body inspection. |
| 4 | 2026-09-14 | curate | — | — | Added one Gotchas entry to `.nybo/memory/domains/frontend.md` on empty-string→`undefined` (not `Number("")`) for optional numeric fields backed by an absence-triggered backend validation. |
