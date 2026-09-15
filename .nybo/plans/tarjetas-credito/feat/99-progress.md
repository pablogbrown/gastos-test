# Progress — Gestión de tarjetas de crédito y alerta de vencimiento

## Checklist

### Tasks
- [x] T1 — Modelo `TarjetaCredito` + migración
- [x] T2 — `tarjeta_service` (CRUD + cálculo de alerta)
- [x] T3 — Rutas de tarjetas; dashboard expone alertas
- [ ] T4 — Pantalla "Tarjetas"; banner en Inicio

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Alta de tarjeta con datos válidos
- [ ] `[TC-002]` *[INTEGRATION]* — Alta sin banco rechazada con 400
- [ ] `[TC-003]` *[INTEGRATION]* — Edición de vencimiento persiste
- [ ] `[TC-004]` *[INTEGRATION]* — Baja saca la tarjeta del listado activo
- [ ] `[TC-005]` *[UNIT]* — Vence en 3 días → aparece en alerta
- [ ] `[TC-006]` *[UNIT]* — Ya vencida → aparece marcada como vencida
- [ ] `[TC-007]` *[UNIT]* — Vence en 20 días → no aparece en alerta
- [ ] `[TC-008]` *[UNIT]* — Banner se renderiza en Inicio
- [ ] `[TC-009]` *[UNIT]* — Alta desde el formulario de la pantalla Tarjetas

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec creada — 4 tareas, 9 test cases. Independiente de `gastos-multi-moneda`; dependencia de `importar-resumen-tarjeta` (build en ese orden). |
