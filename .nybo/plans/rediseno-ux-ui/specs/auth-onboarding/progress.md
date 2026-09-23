# Auth y onboarding - Progress

| | |
| --- | --- |
| Spec | [spec.md](spec.md) |

## Checklist

### Tasks
- [x] T1 — Login + Registro
- [x] T2 — Selector de casas + Crear casa

### Verify
- [x] Verificación (spec-level, una sola pasada tras completar T1–T2)

### Curate
- [x] Curación de hallazgos post-verify

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Login muestra una tarjeta centrada con "taskia" como encabezado.
- [x] `[TC-002]` *[INTEGRATION]* — un error de login muestra el mismo mensaje que antes del restyle.
- [x] `[TC-003]` *[UNIT]* — cada casa en el Selector es una tarjeta seleccionable consistente con Login/Registro.
- [x] `[TC-004]` *[INTEGRATION]* — los test suites existentes pasan sin modificar sus queries.

#### Evidence Results
| # | Date | Finding | Status |
| --- | --- | --- | --- |
| 1 | 2026-09-23 | Build/lint/tests en verde (166/166). Coverage no disponible (sin proveedor instalado, ver decisions.yaml D001). Live evidence capturada (Login/Registro/Selector con 2 casas, desktop+mobile). | resolved |

#### Outcome Smoke Test
Observado en vivo (cycle 1): registro → login → selector vacío → crear
"Casa del centro" → 2da casa creada vía API con el JWT real de la
sesión → reload → Selector de casas con 2 tarjetas seleccionables.
Confirmado en desktop y mobile: tarjeta centrada con "taskia" como
encabezado en Login/Registro/Crear casa, paleta cálida consistente. Ver
capturas en `evidence/1/build-results.md` (sección Verification).

## Decisions
- [ ] `[D001]` Sin proveedor de cobertura instalado (`@vitest/coverage-v8` ausente) — decision class `new-dependency`, siempre difiere a un humano. Remedio: `/nybo-brownfield-bootstrap --quality`.

## Suggestions
- [ ] `[S001]` No coverage tool configured for the frontend (aún sin resolver) — mismo gap ya reportado por `sistema-visual`.
- [ ] `[S002]` Un usuario no tiene forma de crear una 2da casa desde dentro del shell — solo desde SelectorCasas antes de elegir una (preexistente, fuera de scope).

## History

| # | Date | Event | Verdict | Smoke | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-23 | plan | — | — | Spec created — 2 tasks, 4 test cases. |
| 2 | 2026-09-23 | build | ready | pass | Cycle 1: T1+T2 completos, verify en verde (166/166), curate aplicado. |
