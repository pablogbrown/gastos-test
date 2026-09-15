# Progress — Importar resumen de tarjeta en PDF

## Checklist

### Tasks
- [x] T1 — `pdf_resumen_parser` (puro); `Gasto.tarjeta_id`; dependencia `pdfplumber`
- [x] T2 — `resumen_importer_service`; helpers de cuotas/suscripción detectada
- [x] T3 — Endpoint de subida de PDF
- [x] T4 — Botón "Importar resumen" en Tarjetas

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Importar actualiza cierre/vencimiento/saldo de la tarjeta
- [x] `[TC-002]` *[INTEGRATION]* — Consumo en pesos crea gasto en ARS
- [x] `[TC-003]` *[INTEGRATION]* — Consumo en dólares crea gasto en USD
- [x] `[TC-004]` *[INTEGRATION]* — "C.04/06" crea solo las cuotas restantes
- [x] `[TC-005]` *[INTEGRATION]* — Comercio reconocido crea Suscripcion nueva (Administrador)
- [x] `[TC-006]` *[INTEGRATION]* — Comercio reconocido reutiliza Suscripcion existente
- [x] `[TC-007]` *[INTEGRATION]* — Comercio reconocido sin permiso cae a gasto suelto
- [x] `[TC-008]` *[INTEGRATION]* — Líneas de impuestos/cargos nunca generan gastos
- [x] `[TC-009]` *[INTEGRATION]* — PDF no reconocible rechazado, cero gastos creados (cubierto a nivel de parser en T1; integración completa en T2)
- [x] `[TC-010]` *[UNIT]* — Botón "Importar resumen" sube y muestra el resumen sin confirmación

## Completion Summary
_Pendiente — se completa al finalizar el build._

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec creada — 4 tareas, 10 test cases. Depende de `gastos-multi-moneda` y `tarjetas-credito` (build en ese orden). Nueva dependencia de backend: `pdfplumber` (confirmada con el usuario). |
