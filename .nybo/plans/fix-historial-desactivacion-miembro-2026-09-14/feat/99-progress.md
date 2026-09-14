# Progress — Altas y bajas de miembro no quedan en el Historial

## Checklist

### Tasks
- [x] T1 — Registrar actividad en alta y baja de miembro
- [x] T2 — Frontend reconoce `miembro_desactivado`

### Verify
- [x] Verificación end-to-end de la spec
- [x] **Outcome smoke test**

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Agregar miembro registra `miembro_agregado`
- [x] `[TC-002]` *[INTEGRATION]* — Desactivar miembro registra `miembro_desactivado`
- [x] `[TC-003]` *[INTEGRATION]* — Una operación fallida no agrega actividad
- [x] `[TC-004]` *[UNIT]* — Frontend renderiza `miembro_desactivado` con ícono/etiqueta propios

#### Outcome Smoke Test
**Latest:** observed — screen: observed · API: observed — alta y baja de un miembro contra el docker-compose ya levantado (backend `localhost:8000`, frontend `localhost:5173`, Postgres real): registro de 2 usuarios, casa nueva, `POST /casas/{id}/miembros` (TC-001), `PATCH /casas/{id}/miembros/{id}` (TC-002), `GET /casas/{id}/actividad` confirmando ambas entradas, y la pantalla "Actividad" renderizando ambas con ícono/etiqueta propios y orden cronológico correcto, sin errores de consola. El primer intento de baja encontró un bug real de entorno (enum nativo de Postgres desactualizado en el volumen persistente) — corregido con la migración `0006` antes de re-observar con éxito (ver Judgment en `evidence/1/build-results.md`).

## Completion Summary
T1 y T2 implementados vía TDD (RED→GREEN por tarea). Backend: nuevo
`TipoActividadEnum.MIEMBRO_DESACTIVADO`, `agregar_miembro`/
`desactivar_miembro` ahora llaman `registrar_actividad` tras su propio
`commit` exitoso, nunca en un path de error. Frontend: `TipoActividad`
incluye `"miembro_desactivado"`; `ETIQUETAS_TIPO`/`ICONOS_TIPO` (con
`PersonRemoveIcon`) lo reconocen. Efecto colateral corregido: dos
fixtures de test existentes (`miembro_service.test.py`,
`casas_routes.test.py`) no migraban `historial_actividad` ni
monkeypatcheaban `actividad_service.get_session` — ahora sí, porque
`agregar_miembro` pasó a escribir en esa tabla.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 2 tasks, 4 test cases. Ampliado en planning: también cubre `miembro_agregado`, que existía como enum muerto sin invocar. |
| 2 | 2026-09-14 | execute | — | — | T1+T2 implementados, TDD por tarea. Backend 134/134 verde, frontend 58/58 verde, build+lint limpios. |
| 3 | 2026-09-14 | verify | verified | observed | Build/tests/coverage-gate/test-cases/live-evidence todos verdes. Smoke en vivo encontró un enum de Postgres desactualizado en el docker-compose ya levantado (bug real de entorno, no del código nuevo) — corregido con migración `0006` + test de regresión; re-observado con éxito. 193/193 tests. |
