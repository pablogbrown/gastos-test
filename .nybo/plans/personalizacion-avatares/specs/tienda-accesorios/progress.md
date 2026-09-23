# Tienda de accesorios - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [ ] T1 — Catálogo `AccesorioAvatar` + seed + filtro por especie/ventana
- [ ] T2 — Inventario + compra (gasta créditos)
- [ ] T3 — Equipar/desequipar por slot + endpoints

### Verify
- [ ] Verificación (spec-level, una sola pasada tras completar T1–T3)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — el catálogo expone slot/rareza/precio/especie/asset por ítem.
- [ ] `[TC-002]` *[UNIT]* — un ítem incompatible de especie no aparece para el avatar actual del miembro.
- [ ] `[TC-003]` *[INTEGRATION]* — comprar con saldo suficiente descuenta créditos y agrega al inventario.
- [ ] `[TC-004]` *[INTEGRATION]* — comprar sin saldo suficiente se rechaza sin descontar nada.
- [ ] `[TC-005]` *[INTEGRATION]* — comprar un ítem ya en el inventario se rechaza sin doble descuento.
- [ ] `[TC-006]` *[INTEGRATION]* — equipar un ítem comprado y compatible lo activa en su slot.
- [ ] `[TC-007]` *[INTEGRATION]* — equipar un ítem no comprado se rechaza.
- [ ] `[TC-008]` *[INTEGRATION]* — equipar un segundo ítem del mismo slot reemplaza al primero.
- [ ] `[TC-009]` *[UNIT]* — un ítem fuera de ventana no aparece en el catálogo de compra.
- [ ] `[TC-010]` *[UNIT]* — un ítem ya comprado sigue visible/equipable aunque esté fuera de ventana.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| — | — | Not yet started. | not started |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 3 tasks, 10 test cases. |
