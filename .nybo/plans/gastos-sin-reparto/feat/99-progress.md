# Progress — Gastos sin reparto entre participantes

## Checklist

### Tasks
- [x] T1 — Elimina `GastoParticipante`; `gasto_service` deja de repartir
- [x] T2 — `balance_service`: total de la casa + aportes informativos
- [x] T3 — API/`dashboard_service` reflejan el nuevo contrato
- [x] T4 — `Gastos.tsx` sin selector; `Balance.tsx`/`InicioCasa.tsx` rediseñados

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Registrar un gasto ya no genera reparto
- [x] `[TC-002]` *[INTEGRATION]* — Tabla gasto_participantes eliminada
- [x] `[TC-003]` *[INTEGRATION]* — Total gastado de la casa por moneda
- [x] `[TC-004]` *[INTEGRATION]* — Aporte por miembro, sin correspondía/balance
- [x] `[TC-005]` *[UNIT]* — Sin transferencias sugeridas (control)
- [x] `[TC-006]` *[UNIT]* — Formulario sin selector de participantes
- [x] `[TC-007]` *[UNIT]* — Dashboard con el nuevo total de la casa
- [x] `[TC-008]` *[INTEGRATION]* — Cuotas siguen funcionando sin reparto (control de regresión)

## Completion Summary
Las 4 tareas se implementaron en un solo ciclo de BUILD: `GastoParticipante`
se eliminó por completo (modelo, tabla vía migración `0014`, y todo el
reparto en `gasto_service`); `balance_service.calcular_balance` se
reescribió con `BalanceCasa {totales, aportes}`; API/dashboard/frontend
reflejan el nuevo contrato sin ningún campo de deuda ni transferencia.
267 tests de pytest + 105 de vitest en verde, `npm run build`/`lint`
limpios, migración `0014` verificada contra Postgres real (docker) tanto
en una base nueva como en una que ya tenía `gasto_participantes` creada
de antes. Smoke en vivo contra ese mismo Postgres confirmó el flujo
completo (registro → login → casa → categoría → gasto → balance →
dashboard) y la regresión de cuotas (TC-008). Ver
`evidence/1/build-results.md` para el detalle completo.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-16 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Independiente de `prestamos-entre-miembros` (sin dependencia funcional ni overlap de archivos, salvo posible orden de build a elección). |
| 2 | 2026-09-16 | build | verified | pass | Ciclo único: T1-T4 implementadas, 267 pytest + 105 vitest en verde, build/lint limpios, migración 0014 verificada contra Postgres real (fresh + pre-existing), smoke en vivo end-to-end. |
