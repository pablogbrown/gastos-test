# Tienda de accesorios - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Catálogo `AccesorioAvatar` + seed + filtro por especie/ventana
- [x] T2 — Inventario + compra (gasta créditos)
- [x] T3 — Equipar/desequipar por slot + endpoints

### Verify
- [x] Verificación (spec-level, una sola pasada tras completar T1–T3)

### Curate
- [x] Curación de hallazgos post-verify

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — el catálogo expone slot/rareza/precio/especie/asset por ítem.
- [x] `[TC-002]` *[UNIT]* — un ítem incompatible de especie no aparece para el avatar actual del miembro.
- [x] `[TC-003]` *[INTEGRATION]* — comprar con saldo suficiente descuenta créditos y agrega al inventario.
- [x] `[TC-004]` *[INTEGRATION]* — comprar sin saldo suficiente se rechaza sin descontar nada.
- [x] `[TC-005]` *[INTEGRATION]* — comprar un ítem ya en el inventario se rechaza sin doble descuento.
- [x] `[TC-006]` *[INTEGRATION]* — equipar un ítem comprado y compatible lo activa en su slot.
- [x] `[TC-007]` *[INTEGRATION]* — equipar un ítem no comprado se rechaza.
- [x] `[TC-008]` *[INTEGRATION]* — equipar un segundo ítem del mismo slot reemplaza al primero.
- [x] `[TC-009]` *[UNIT]* — un ítem fuera de ventana no aparece en el catálogo de compra.
- [x] `[TC-010]` *[UNIT]* — un ítem ya comprado sigue visible/equipable aunque esté fuera de ventana.

#### Outcome Smoke Test
`observed` — los 5 pasos de spec.md corridos en vivo contra un `uvicorn` real de esta rama (SQLite fallback por defecto, migraciones reales 0001-0026, cero fixtures), más los 3 códigos de error del contrato. Detalle completo en `evidence/1/build-results.md`'s Verification.
- API: `observed` — el catálogo excluye "solo-gato" para un avatar "perro" seleccionado; comprar un accesorio descuenta el saldo exactamente su precio (80→60); equiparlo lo activa en su slot; comprar+equipar un segundo ítem del mismo slot reemplaza al primero (ambos siguen en inventario); 402/409/403/204 confirmados en vivo.
- screen: `n/a` — el Outcome de esta spec es 100% observable vía API (spec.md's propio Outcome Smoke Test no incluye ningún paso de UI); la integración visual es scope de `perfil-avatar-ui`.

## Suggestions
- [ ] `[S001]` *(tech-debt)* — Reemplazar los `asset_overlay_url` placeholder del seed de T1 por assets reales verificados.
- [x] `[S002]` *(question)* — Confirmar con `perfil-avatar-ui` las rutas reales (anidadas bajo `/casas/{casa_id}/miembros/{miembro_id}/accesorios/...`, catálogo en `.../catalogo`), distintas del contrato literal de spec.md. *(resuelto por `personalizacion-avatares/specs/perfil-avatar-ui`, build cycle 1 — leyó `tienda.py` directamente.)*
- [x] `[S003]` *(follow-up)* — Exponer `tienda_service.listar_equipados` (ya implementada) vía una ruta `GET .../accesorios/equipados` antes de que `perfil-avatar-ui` necesite renderizar el estado equipado por slot. *(resuelto por `personalizacion-avatares/specs/perfil-avatar-ui`, build cycle 1 — ver su Judgment J001.)*

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| 1 | 2026-09-23 | T1–T3 implementados; verify en verde (437 backend + 183 frontend, build/lint limpios); Outcome Smoke Test corrido en vivo end-to-end. | verified |

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 3 tasks, 10 test cases. |
| 2 | 2026-09-23 | build | verified | observed | T1–T3 implementados y verificados en un solo ciclo — 437 tests backend (413 base + 24 nuevos) + 183 frontend, build/lint limpios, Outcome Smoke Test corrido en vivo. 0 decisiones bloqueantes; 3 sugerencias registradas. Construido sobre `feat/personalizacion-avatares--avatares-economia` (PR #53, aún no mergeado). |
