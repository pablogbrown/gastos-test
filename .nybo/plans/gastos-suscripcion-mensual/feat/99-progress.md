# Progress — Suscripciones mensuales de gastos

## Checklist

### Tasks
- [x] T1 — Modelo `Suscripcion` + FK en `Gasto`
- [x] T2 — Servicio de suscripciones + generación perezosa
- [x] T3 — Rutas HTTP de suscripciones
- [x] T4 — Pantalla "Suscripciones" + creación desde Gastos

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Crear suscripción genera el gasto del mes actual
- [x] `[TC-002]` *[INTEGRATION]* — Listar gastos genera el mes pendiente
- [x] `[TC-003]` *[INTEGRATION]* — No duplica el gasto del mes ya generado
- [x] `[TC-004]` *[INTEGRATION]* — Cancelar detiene la generación futura sin tocar lo ya generado
- [x] `[TC-005]` *[INTEGRATION]* — Un member no puede crear ni cancelar
- [x] `[TC-006]` *[UNIT]* — Pantalla Suscripciones lista y ofrece cancelar solo lo activo
- [x] `[TC-007]` *[UNIT]* — El formulario de Gastos crea una suscripción en el modo correspondiente

## Completion Summary
T1-T4 implementados y verificados en un solo ciclo BUILD. 179 pytest
passed / 1 skipped (180/0 dentro del contenedor Docker contra Postgres
real), 79 vitest passed, `tsc --noEmit && vite build` sin errores, `npm
run lint` limpio. Smoke manual en vivo contra docker-compose confirmado
end-to-end (crear suscripción -> gasto generado de inmediato -> listada
activa en Suscripciones -> cancelar -> gasto intacto, suscripción
inactiva). Dos gotchas reales de Postgres descubiertos y corregidos
durante el smoke (ver `evidence/1/build-results.md` Judgment J001/J002,
curados a `.nybo/memory/domains/db.md` como DBG-02/DBG-03). PR #22
actualizado (draft → sigue en draft, listo para promoción por el
humano vía `/nybo-pr`).

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 4 tasks, 7 test cases. Depende de `balance-mensual` (build en ese orden); independiente de `gastos-en-cuotas` salvo que ambas tocan `Gastos.tsx`/`registrar_gasto`. |
| 2 | 2026-09-15 | build | verified | pass | Ciclo 1: T1-T4 implementados, 179 pytest + 79 vitest verdes (180/0 en Docker/Postgres real), build/lint limpios, smoke en vivo confirmado. 2 gotchas de Postgres encontrados y corregidos (FK a nivel de modelo rompe orden de migraciones; ALTER TABLE necesita CHAR(36), no UUID nativo). PR #22 actualizado. |
