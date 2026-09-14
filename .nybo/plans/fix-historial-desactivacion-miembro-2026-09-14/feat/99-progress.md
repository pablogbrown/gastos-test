# Progress — Altas y bajas de miembro no quedan en el Historial

## Checklist

### Tasks
- [ ] T1 — Registrar actividad en alta y baja de miembro
- [ ] T2 — Frontend reconoce `miembro_desactivado`

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Agregar miembro registra `miembro_agregado`
- [ ] `[TC-002]` *[INTEGRATION]* — Desactivar miembro registra `miembro_desactivado`
- [ ] `[TC-003]` *[INTEGRATION]* — Una operación fallida no agrega actividad
- [ ] `[TC-004]` *[UNIT]* — Frontend renderiza `miembro_desactivado` con ícono/etiqueta propios

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 2 tasks, 4 test cases. Ampliado en planning: también cubre `miembro_agregado`, que existía como enum muerto sin invocar. |
