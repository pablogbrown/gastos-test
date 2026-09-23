# Perfil con avatar - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Avatar+accesorios en Miembros/Ranking
- [ ] T2 — Pantalla "Mi Avatar" + navegación

### Verify
- [ ] Verificación (spec-level, una sola pasada tras completar T1–T2)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Miembros muestra `LottieAvatar` con accesorios equipados.
- [x] `[TC-002]` *[UNIT]* — sin avatar seleccionado, se muestra el `Avatar` con inicial como respaldo.
- [x] `[TC-003]` *[UNIT]* — Ranking también muestra el avatar del miembro.
- [ ] `[TC-004]` *[UNIT]* — "Mi Avatar" muestra razas desbloqueadas y bloqueadas con su nivel requerido.
- [ ] `[TC-005]` *[INTEGRATION]* — seleccionar una raza desbloqueada la aplica de inmediato.
- [ ] `[TC-006]` *[INTEGRATION]* — comprar/equipar un accesorio actualiza el saldo sin recargar.
- [ ] `[TC-007]` *[UNIT]* — "Mi Avatar" vive dentro del grupo "Casa"; el bottom nav sigue con 4 ítems.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| — | — | Not yet started. | not started |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 2 tasks, 7 test cases. |
