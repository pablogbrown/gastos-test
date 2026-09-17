# Progress — resumen-tarjeta-pago

## Checklist

### Tasks
- [ ] T1 — `ResumenTarjeta`; `Gasto.resumen_id`; migración `0019`
- [ ] T2 — Tracking de resúmenes; `pagar_resumen`; threading `resumen_id`
- [ ] T3 — Endpoints de resúmenes; 409 en importar duplicado
- [ ] T4 — UI de resúmenes en Tarjetas.tsx

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Importar un resumen crea ResumenTarjeta
- [ ] `[TC-002]` *[INTEGRATION]* — Importar duplicado se rechaza (409)
- [ ] `[TC-003]` *[INTEGRATION]* — Gastos creados quedan vinculados al resumen
- [ ] `[TC-004]` *[INTEGRATION]* — Pagar resumen marca todo como pagado
- [ ] `[TC-005]` *[INTEGRATION]* — Pagar resumen no afecta otros/doble pago
- [ ] `[TC-006]` *[INTEGRATION]* — Listar resúmenes de una tarjeta
- [ ] `[TC-007]` *[UNIT]* — UI muestra resúmenes + botón Pagar resumen
- [ ] `[TC-008]` *[UNIT]* — UI muestra error claro en importación duplicada

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-17 | plan | — | — | Spec creada — 4 tareas, 8 test cases. Reportado en vivo sobre `importar-resumen-tarjeta` ya shippeada: tracking de resúmenes + prevención de duplicados + pago masivo. |
