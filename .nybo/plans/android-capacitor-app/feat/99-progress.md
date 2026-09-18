# Progress — android-capacitor-app

## Checklist

### Tasks
- [x] T1 — Base URL de API configurable (`VITE_API_BASE_URL`)
- [x] T2 — CORS en el backend (`CORS_ALLOWED_ORIGINS`)
- [x] T3 — Proyecto Android + Capacitor (`android/`)
- [x] T4 — Documentación (`docs/android.md`) + verificación end-to-end

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes — deliberadamente NO
      corrida en este ciclo (instrucción explícita del usuario)

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Sin la env var, rutas idénticas a hoy
- [x] `[TC-002]` *[UNIT]* — Con la env var, rutas con prefijo absoluto
- [x] `[TC-003]` *[INTEGRATION]* — Origen permitido recibe el header CORS
- [x] `[TC-004]` *[INTEGRATION]* — Origen no permitido / sin Origin, sin cambios
- [x] `[TC-005]` *[INTEGRATION]* — `cap sync` referencia appId/webDir correctos
- [x] `[TC-006]` *[INTEGRATION]* — Cleartext permitido en la config de red

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-18 | plan | — | — | Spec creada — 4 tareas, 6 test cases. Empaquetar el frontend existente como app Android vía Capacitor, con base URL de API configurable y CORS en el backend; la compilación/corrida final en Android Studio queda como paso manual del usuario. |
| 2 | 2026-09-18 | build | ready | pass | T1-T4 implementadas via TDD. Backend 367 passed (docker), frontend 139 passed (host), T3 estructural 5 passed (host, fuera del volumen del backend docker). Build/lint sin errores. Smoke combinado T1+T2 confirmado con un login real cross-origin (dist servido en :4173, backend standalone en :8001) via browser real — preflight CORS + login + /casas/mias, los 3 en 200. Curate/ship NO corridos por instrucción explícita del usuario. |
