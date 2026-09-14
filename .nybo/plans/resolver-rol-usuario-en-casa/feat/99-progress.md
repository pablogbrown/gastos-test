# Progress — Resolver el rol real del Usuario en la casa

## Checklist

### Tasks
- [x] T1 — `MiembroOut` expone `usuario_id`
- [x] T2 — `App.tsx` resuelve el rol real del Usuario
- [x] T3 — `Tareas.tsx` compara el `Miembro.id` propio, no el `Usuario.id` global

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — `MiembroOut` incluye `usuario_id`
- [x] `[TC-002]` *[UNIT]* — Rol `member` oculta altas/bajas en Miembros
- [x] `[TC-003]` *[UNIT]* — Rol `admin` muestra los controles correspondientes
- [x] `[TC-004]` *[UNIT]* — Sin match de `usuario_id` el fallback es `"member"`, nunca `"admin"`
- [x] `[TC-005]` *[UNIT]* — "Marcar completada" visible para el responsable asignado (Miembro.id correcto)
- [x] `[TC-006]` *[UNIT]* — "Marcar completada" oculto para un member no-responsable

#### Outcome Smoke Test
Observado en vivo (docker-compose local, ya levantado, no reiniciado) —
cycle 1: se registraron 2 Usuarios reales, se creó una Casa real y se
agregó un member real vía la API en ejecución (sin fixtures/mocks).
Logueado como member: "Agregar miembro"/"Desactivar" NO se muestran en
Miembros; "Marcar completada" aparece solo en la tarea propia, no en la
del admin. Logueado como admin: ambos controles se muestran. El
`## Outcome` de `spec.md` ("un usuario `member` deja de ver
Agregar miembro/Desactivar, y Marcar completada aparece exactamente para
quien corresponde") quedó confirmado end-to-end, no solo por unit tests.
Ver `evidence/1/build-results.md` (sección Verification) para el detalle
y las 3 capturas.

## Completion Summary
Los 3 tasks implementados en un solo pase (T2/T3 comparten la misma
edición de `App.tsx` — ver Judgment). Backend: `MiembroOut.usuario_id`
aditivo. Frontend: `App.tsx` resuelve `rolUsuarioActual`/`miMiembro` una
sola vez y lo pasa a `Miembros`/`Tareas`; `Tareas.tsx` renombró
`usuarioId` -> `miembroIdActual` y corrigió `puedeCompletar`. 131 tests
backend + 60 tests frontend en verde, `npm run build`/`lint` limpios.

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-14 | plan | — | — | Spec created — 3 tasks, 6 test cases. Escalado desde un finding de bug (rolUsuarioActual hardcodeado) a `/nybo-plan create` por requerir una decisión real de contrato backend, no un one-line fix. |
| 2 | 2026-09-14 | build | verified | passed | T1-T3 implementados vía TDD; pytest (131) y vitest (60) en verde; build/lint limpios. Smoke live contra docker-compose local (ya levantado): TC-001/002/003/005/006 confirmados con usuarios/casa/tareas reales, sin fixtures. |
| 3 | 2026-09-14 | curate | — | — | Pattern nuevo en auth.md ("Frontend identity resolution"); Gotcha de usuarios-auth marcada resuelta. Cycle 1 -> ready. |
