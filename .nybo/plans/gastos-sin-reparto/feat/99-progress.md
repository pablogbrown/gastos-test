# Progress — Gastos sin reparto entre participantes

## Checklist

### Tasks
- [ ] T1 — Elimina `GastoParticipante`; `gasto_service` deja de repartir
- [ ] T2 — `balance_service`: total de la casa + aportes informativos
- [ ] T3 — API/`dashboard_service` reflejan el nuevo contrato
- [ ] T4 — `Gastos.tsx` sin selector; `Balance.tsx`/`InicioCasa.tsx` rediseñados

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Registrar un gasto ya no genera reparto
- [ ] `[TC-002]` *[INTEGRATION]* — Tabla gasto_participantes eliminada
- [ ] `[TC-003]` *[INTEGRATION]* — Total gastado de la casa por moneda
- [ ] `[TC-004]` *[INTEGRATION]* — Aporte por miembro, sin correspondía/balance
- [ ] `[TC-005]` *[UNIT]* — Sin transferencias sugeridas (control)
- [ ] `[TC-006]` *[UNIT]* — Formulario sin selector de participantes
- [ ] `[TC-007]` *[UNIT]* — Dashboard con el nuevo total de la casa
- [ ] `[TC-008]` *[INTEGRATION]* — Cuotas siguen funcionando sin reparto (control de regresión)

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Independiente de `prestamos-entre-miembros` (sin dependencia funcional ni overlap de archivos, salvo posible orden de build a elección). |
