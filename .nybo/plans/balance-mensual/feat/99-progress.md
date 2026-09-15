# Progress — Balance filtrable por mes

## Checklist

### Tasks
- [ ] T1 — `calcular_balance` filtra por mes
- [ ] T2 — Ruta y cliente HTTP exponen `mes`
- [ ] T3 — `Balance.tsx` agrega el selector de mes

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Sin mes explícito usa el mes actual
- [ ] `[TC-002]` *[INTEGRATION]* — Con mes explícito filtra correctamente
- [ ] `[TC-003]` *[INTEGRATION]* — Mes con formato inválido es rechazado (400)
- [ ] `[TC-004]` *[UNIT]* — Selector de mes preseleccionado en el actual
- [ ] `[TC-005]` *[UNIT]* — Cambiar el mes dispara una nueva consulta

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 3 tasks, 5 test cases. Foundation requerida para que "gastos-en-cuotas"/"gastos-suscripcion-mensual" tengan sentido semántico (deuda futura no debe sumar hoy). |
