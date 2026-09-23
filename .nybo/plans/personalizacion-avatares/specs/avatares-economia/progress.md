# Avatares y economía de créditos - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [ ] T1 — Ledger de créditos + hook en `completar_tarea`
- [ ] T2 — Catálogo `AvatarPersonaje` + seed
- [ ] T3 — Desbloqueo por nivel + selección + endpoints
- [ ] T4 — Componente `LottieAvatar` + `avatarClient.ts`

### Verify
- [ ] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — completar una tarea crea una `CreditoTransaccion` por el mismo importe que los puntos.
- [ ] `[TC-002]` *[INTEGRATION]* — recompletar una tarea ya completada no crea créditos adicionales.
- [ ] `[TC-003]` *[UNIT]* — el catálogo expone especie/nombre/nivel/rareza/asset por raza.
- [ ] `[TC-004]` *[UNIT]* — una raza fuera de ventana no aparece salvo que ya esté seleccionada.
- [ ] `[TC-005]` *[INTEGRATION]* — un miembro Novato no puede seleccionar una raza de nivel Activo.
- [ ] `[TC-006]` *[INTEGRATION]* — un miembro Activo puede seleccionar una raza de nivel Novato o Activo.
- [ ] `[TC-007]` *[UNIT]* — sin selección previa, el avatar es `null`.
- [ ] `[TC-008]` *[INTEGRATION]* — cambiar de raza reemplaza la selección anterior.
- [ ] `[TC-009]` *[UNIT]* — `LottieAvatar` reproduce la URL recibida por props.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| — | — | Not yet started. | not started |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 9 test cases. |
