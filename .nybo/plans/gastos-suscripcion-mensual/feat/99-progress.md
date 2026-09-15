# Progress — Suscripciones mensuales de gastos

## Checklist

### Tasks
- [ ] T1 — Modelo `Suscripcion` + FK en `Gasto`
- [ ] T2 — Servicio de suscripciones + generación perezosa
- [ ] T3 — Rutas HTTP de suscripciones
- [ ] T4 — Pantalla "Suscripciones" + creación desde Gastos

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[INTEGRATION]* — Crear suscripción genera el gasto del mes actual
- [ ] `[TC-002]` *[INTEGRATION]* — Listar gastos genera el mes pendiente
- [ ] `[TC-003]` *[INTEGRATION]* — No duplica el gasto del mes ya generado
- [ ] `[TC-004]` *[INTEGRATION]* — Cancelar detiene la generación futura sin tocar lo ya generado
- [ ] `[TC-005]` *[INTEGRATION]* — Un member no puede crear ni cancelar
- [ ] `[TC-006]` *[UNIT]* — Pantalla Suscripciones lista y ofrece cancelar solo lo activo
- [ ] `[TC-007]` *[UNIT]* — El formulario de Gastos crea una suscripción en el modo correspondiente

## Completion Summary
Not yet started.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 4 tasks, 7 test cases. Depende de `balance-mensual` (build en ese orden); independiente de `gastos-en-cuotas` salvo que ambas tocan `Gastos.tsx`/`registrar_gasto`. |
