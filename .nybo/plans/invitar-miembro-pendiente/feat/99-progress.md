# Progress — Invitar a un miembro que todavía no tiene cuenta

## Checklist

### Tasks
- [x] T1 — `Miembro` guarda el email invitado
- [x] T2 — `agregar_miembro` crea una membresía pendiente
- [x] T3 — `registrar_usuario` vincula las membresías pendientes
- [x] T4 — `Miembros.tsx` muestra "Pendiente"

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [x] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — Alta con email no registrado crea membresía pendiente
- [x] `[TC-002]` *[INTEGRATION]* — Alta con email ya registrado sigue vinculando de inmediato
- [x] `[TC-003]` *[INTEGRATION]* — Registro vincula una membresía pendiente
- [x] `[TC-004]` *[INTEGRATION]* — Registro vincula pendientes en varias casas
- [x] `[TC-005]` *[UNIT]* — Registro sin pendientes no cambia de comportamiento
- [x] `[TC-006]` *[INTEGRATION]* — Doble invitación pendiente al mismo email es rechazada
- [x] `[TC-007]` *[UNIT]* — UI muestra "Pendiente" sin acción Desactivar
- [x] `[TC-008]` *[UNIT]* — UI sigue mostrando Activo/Inactivo normalmente

#### Outcome Smoke Test
Observado en vivo contra el entorno dockerizado real (ciclo 1, ver
`evidence/1/build-results.md` § Live evidence): como Administrador, se
invitó un email nunca registrado (`POST /casas/{id}/miembros` → 201,
`usuario_id: null`) y se confirmó en la UI real (browser) que la fila
muestra el Chip "Pendiente" sin acción "Desactivar". Se registró luego
ese mismo email (`POST /auth/registro`) y se confirmó, refrescando la
misma pantalla, que la fila pasa a "Activo" con "Desactivar" visible —
vinculación automática sin ninguna acción manual adicional. `## Outcome`
observado: **sí**.

## Suggestions
- [ ] `[S001]` — No hay herramienta de coverage configurada en el proyecto
- [ ] `[S002]` — `nybo results write`/`set` sobrescribe el body completo de build-results.md en vez de solo su propia sección

## Completion Summary
Las 4 tareas se implementaron en un solo ciclo BUILD (T1-T4, TDD por
tarea). Suite completa en verde: 144 tests backend (pytest, excluyendo
el test de Postgres real vía Docker, no ejecutado en esta pasada) + 69
tests frontend (vitest), build y lint sin errores. Smoke manual en vivo
contra el entorno dockerizado real: se invitó un email nunca registrado
como Administrador (201, `usuario_id: null`, chip "Pendiente" sin acción
Desactivar en la UI real) y luego se registró ese mismo email,
confirmando la vinculación automática (pasa a "Activo" con
"Desactivar" visible) — replica exactamente el bug report original.
Cobertura no medible: no hay herramienta de coverage configurada en el
proyecto (`stack.yaml` `quality_tools.coverage.tool: null`).

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-15 | plan | — | — | Spec created — 4 tasks, 8 test cases. Originado en feedback del usuario sobre la pantalla Miembros (captura + pregunta de aclaración: alta pendiente + auto-vinculación, sin envío de emails). |
| 2 | 2026-09-15 | build | verified | pass | Ciclo 1: T1-T4 implementadas, 144 pytest + 69 vitest en verde, build/lint sin errores. Smoke manual en vivo en docker confirma invitación pendiente + auto-vinculación al registrarse, sin crash (bug original resuelto). 3 tests de regresión preexistentes actualizados para reflejar el nuevo contrato (email sin Usuario ya no es 404). Coverage no medible (sin tool configurado). |
