# Progress — Invitar a un miembro que todavía no tiene cuenta

## Checklist

### Tasks
- [ ] T1 — `Miembro` guarda el email invitado
- [ ] T2 — `agregar_miembro` crea una membresía pendiente
- [ ] T3 — `registrar_usuario` vincula las membresías pendientes
- [ ] T4 — `Miembros.tsx` muestra "Pendiente"

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Alta con email no registrado crea membresía pendiente
- [ ] `[TC-002]` *[INTEGRATION]* — Alta con email ya registrado sigue vinculando de inmediato
- [ ] `[TC-003]` *[INTEGRATION]* — Registro vincula una membresía pendiente
- [ ] `[TC-004]` *[INTEGRATION]* — Registro vincula pendientes en varias casas
- [ ] `[TC-005]` *[UNIT]* — Registro sin pendientes no cambia de comportamiento
- [ ] `[TC-006]` *[INTEGRATION]* — Doble invitación pendiente al mismo email es rechazada
- [ ] `[TC-007]` *[UNIT]* — UI muestra "Pendiente" sin acción Desactivar
- [ ] `[TC-008]` *[UNIT]* — UI sigue mostrando Activo/Inactivo normalmente

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 4 tasks, 8 test cases. Originado en feedback del usuario sobre la pantalla Miembros (captura + pregunta de aclaración: alta pendiente + auto-vinculación, sin envío de emails). |
