# Perfil con avatar - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Avatar+accesorios en Miembros/Ranking
- [x] T2 — Pantalla "Mi Avatar" + navegación

### Verify
- [x] Verificación (spec-level, una sola pasada tras completar T1–T2)

### Curate
- [x] Curación de hallazgos post-verify

**Cycle 1** (2026-09-23): Curated 8 findings: 4 conventions/patterns, 0 gotchas, 0 stale-reference fixes, 0 foundation-deviation reconciliations, 0 patches, 0 skill candidates, 0 deprecations, 0 architecture-fact writes, 0 Observations notes, 1 decisions.yaml entry, 3 no-action (reason given).
- Applied: `api.md` `[API-02]` (casa_id URL-nesting, confirmed 3/3 specs), `api.md` `[APIP-03]` (consuming-spec-exposes-missing-endpoint pattern — resolves this spec's own `[S001]`), `frontend.md` Gotchas (lottie-react v3.1.2 real API vs. spec.md D-01), `frontend.md` `[FRONP-07]` (fetch-mock-by-URL for per-row-fetch screens), `infra.md` (isolated docker-compose verify stack against a shared/already-running dev environment).
- Applied cross-spec: ticked `avatares-economia`'s `[S002]` and `tienda-accesorios`'s `[S002]`/`[S003]` as `done` (resolved by this build).
- Decision: `evidence/decisions.yaml` `D001` — no coverage tool configured project-wide (bounded discovery found none); recommends `/nybo-brownfield-bootstrap --quality`, non-blocking.
- No action: seed-data placeholder Lottie/overlay URLs (already tracked as tech-debt in 3 suggestions.yaml files, not a domain convention); J004/J005 (screen-local UI decisions, not generalizable patterns); architecture.md (this feature fits entirely inside already-documented architecture — no core change).

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Miembros muestra `LottieAvatar` con accesorios equipados.
- [x] `[TC-002]` *[UNIT]* — sin avatar seleccionado, se muestra el `Avatar` con inicial como respaldo.
- [x] `[TC-003]` *[UNIT]* — Ranking también muestra el avatar del miembro.
- [x] `[TC-004]` *[UNIT]* — "Mi Avatar" muestra razas desbloqueadas y bloqueadas con su nivel requerido.
- [x] `[TC-005]` *[INTEGRATION]* — seleccionar una raza desbloqueada la aplica de inmediato.
- [x] `[TC-006]` *[INTEGRATION]* — comprar/equipar un accesorio actualiza el saldo sin recargar.
- [x] `[TC-007]` *[UNIT]* — "Mi Avatar" vive dentro del grupo "Casa"; el bottom nav sigue con 4 ítems.

#### Outcome Smoke Test
`observed` — los 5 pasos de spec.md corridos en vivo contra un stack docker-compose aislado de este worktree (proyecto `perfilavatarui-verify`, derribado al terminar). Detalle completo en `evidence/1/build-results.md`'s Verification.
- API: `observed` — completar una tarea sube el saldo de créditos (50); `avatares-catalogo` devuelve las 10 razas (incluyendo Comprometido/Campeón bloqueadas) mientras `avatares-disponibles` solo las 6 desbloqueadas por el nivel "Activo" alcanzado; seleccionar Beagle, comprar "Gorro de lana" (saldo 50→30) y equiparlo confirmados; `accesorios/equipados` devuelve el ítem con su `asset_overlay_url`.
- screen: `observed` — 3 capturas vía `/nybo-ui-evidence` (`evidence/1/screenshots/`): Miembros/Ranking ya no muestran el círculo con inicial (reemplazado por el contenedor Lottie+overlay), y "Mi Avatar" muestra el saldo, la raza activa, las razas bloqueadas con su nivel, y el accesorio equipado. Único hallazgo: el ícono/animación no se ve porque el seed usa URLs placeholder no resolubles (`[S002]`, no bloqueante — la estructura es la esperada).

## Suggestions
- [x] `[S001]` *(question)* — Confirmar como convención de proyecto: una spec consumidora expone ella misma un endpoint prerrequisito que otra spec dejó sin ruta, en el mismo ciclo. *(resuelto por curate, build cycle 1 — ver `api.md`'s `[APIP-03]`.)*
- [ ] `[S002]` *(tech-debt)* — Reemplazar las URLs placeholder de `lottie_url`/`asset_overlay_url` (avatares-economia S001, tienda-accesorios S001) por assets reales — confirmado visualmente en este ciclo.
- [ ] `[S003]` *(question)* — Configurar una herramienta de coverage (`stack.yaml`'s `quality_tools.coverage.tool` es `null`) vía `/nybo-brownfield-bootstrap --quality`.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| 1 | 2026-09-23 | 2 endpoints prerrequisito agregados fuera de run-plan.json: `GET .../accesorios/equipados` ([S003] de tienda-accesorios) y `GET .../avatares-catalogo` (ver evidence/1/build-results.md J001/J002). | resolved |
| 2 | 2026-09-23 | Assets Lottie/overlay sembrados con URLs placeholder no resolubles (403/bloqueado) — animación no se ve, estructura sí es la correcta (J007). | observation, non-blocking |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 2 tasks, 7 test cases. |
| 2 | 2026-09-23 | build | verified | ran | T1+T2 implementados (2 endpoints prerrequisito agregados), verify spec-level en verde: 442 backend + 193 frontend tests, build/lint limpios, 7/7 TC resueltas, live evidence (API + 3 capturas) contra stack docker aislado. |
