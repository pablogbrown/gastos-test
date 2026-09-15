# Progress — Balance filtrable por mes

## Checklist

### Tasks
- [x] T1 — `calcular_balance` filtra por mes
- [x] T2 — Ruta y cliente HTTP exponen `mes`
- [x] T3 — `Balance.tsx` agrega el selector de mes

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Sin mes explícito usa el mes actual
- [x] `[TC-002]` *[INTEGRATION]* — Con mes explícito filtra correctamente
- [x] `[TC-003]` *[INTEGRATION]* — Mes con formato inválido es rechazado (400)
- [x] `[TC-004]` *[UNIT]* — Selector de mes preseleccionado en el actual
- [x] `[TC-005]` *[UNIT]* — Cambiar el mes dispara una nueva consulta

## Completion Summary
T1-T3 implementadas vía TDD. 147 pytest + 70 vitest en verde (140+67
baseline + 5 nuevos backend T1 + 2 nuevos backend T2 + 3 nuevos frontend
T3). `npm run build`/`npm run lint` limpios. Smoke en vivo contra
docker-compose local confirmó las 5 test cases, incluyendo el selector
de mes de `Balance.tsx` refetcheando en el navegador real.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 3 tasks, 5 test cases. Foundation requerida para que "gastos-en-cuotas"/"gastos-suscripcion-mensual" tengan sentido semántico (deuda futura no debe sumar hoy). |
| 2 | 2026-09-15 | build (cycle 1) | verified | live-confirmed | T1-T3 implemented via TDD; 147 pytest + 70 vitest green; live smoke on docker confirmed TC-001..005 (API + browser). |
