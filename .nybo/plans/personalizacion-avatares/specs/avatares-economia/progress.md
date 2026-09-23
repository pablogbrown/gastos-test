# Avatares y economía de créditos - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Ledger de créditos + hook en `completar_tarea`
- [x] T2 — Catálogo `AvatarPersonaje` + seed
- [x] T3 — Desbloqueo por nivel + selección + endpoints
- [x] T4 — Componente `LottieAvatar` + `avatarClient.ts`

### Verify
- [x] Verificación (spec-level, una sola pasada tras completar T1–T4)

### Curate
- [ ] Curación de hallazgos post-verify

#### Test Cases
- [x] `[TC-001]` *[INTEGRATION]* — completar una tarea crea una `CreditoTransaccion` por el mismo importe que los puntos.
- [x] `[TC-002]` *[INTEGRATION]* — recompletar una tarea ya completada no crea créditos adicionales.
- [x] `[TC-003]` *[UNIT]* — el catálogo expone especie/nombre/nivel/rareza/asset por raza.
- [x] `[TC-004]` *[UNIT]* — una raza fuera de ventana no aparece salvo que ya esté seleccionada.
- [x] `[TC-005]` *[INTEGRATION]* — un miembro Novato no puede seleccionar una raza de nivel Activo.
- [x] `[TC-006]` *[INTEGRATION]* — un miembro Activo puede seleccionar una raza de nivel Novato o Activo.
- [x] `[TC-007]` *[UNIT]* — sin selección previa, el avatar es `null`.
- [x] `[TC-008]` *[INTEGRATION]* — cambiar de raza reemplaza la selección anterior.
- [x] `[TC-009]` *[UNIT]* — `LottieAvatar` reproduce la URL recibida por props.

#### Outcome Smoke Test
`observed` — las 5 pasos de spec.md corridos en vivo contra un `uvicorn` real de esta rama (Postgres no alcanzable desde este sandbox; SQLite del fallback por defecto, migraciones reales, cero fixtures). Detalle completo en `evidence/1/build-results.md`'s Verification.
- API: `observed` — créditos suben junto con los puntos, avatares-disponibles refleja el nivel actual en tiempo real (sin caché), selección persiste, ambos 403 (nivel insuficiente / no-self-service) confirmados.
- screen: `n/a` — el Outcome de esta spec es 100% observable vía API (spec.md's propio Outcome Smoke Test no incluye ningún paso de UI); la integración visual es scope de `perfil-avatar-ui`.

## Decisions
- [x] `[D001]` — Agregar `lottie-react` (nueva dependencia, D-01 pre-aprobada) — resuelto.

## Suggestions
- [ ] `[S001]` *(tech-debt)* — Reemplazar los `lottie_url` placeholder de T2 por assets reales verificados de LottieFiles.
- [x] `[S002]` *(question)* — La API real de `lottie-react` difiere de la descripción de D-01; avisar a `perfil-avatar-ui`. *(resuelto por `personalizacion-avatares/specs/perfil-avatar-ui`, build cycle 1 — consumió `LottieAvatar` tal como quedó implementado, no como D-01 lo describía.)*
- [ ] `[S003]` *(tech-debt)* — Varios fixtures de test pre-existentes dependen silenciosamente del orden de recolección de la suite completa.
- [ ] `[S004]` *(tech-debt)* — Correr un `nybo doctor --fix` acotado para regenerar `nybo-services.md`/`nybo-db.md` (revertido en este build por tocar specs no relacionadas).

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| 1 | 2026-09-23 | T1–T4 implementados; verify en verde (413 backend + 183 frontend, build/lint limpios); Outcome Smoke Test corrido en vivo end-to-end. | verified |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 4 tasks, 9 test cases. |
| 2 | 2026-09-23 | build | verified | observed | T1–T4 implementados y verificados en un solo ciclo — 413 tests backend + 183 frontend, build/lint limpios, Outcome Smoke Test corrido en vivo. 1 decisión (D001, lottie-react) y 3 sugerencias registradas. |
