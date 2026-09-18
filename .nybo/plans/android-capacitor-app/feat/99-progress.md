# Progress — android-capacitor-app

## Checklist

### Tasks
- [ ] T1 — Base URL de API configurable (`VITE_API_BASE_URL`)
- [ ] T2 — CORS en el backend (`CORS_ALLOWED_ORIGINS`)
- [ ] T3 — Proyecto Android + Capacitor (`android/`)
- [ ] T4 — Documentación (`docs/android.md`) + verificación end-to-end

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — Sin la env var, rutas idénticas a hoy
- [ ] `[TC-002]` *[UNIT]* — Con la env var, rutas con prefijo absoluto
- [ ] `[TC-003]` *[INTEGRATION]* — Origen permitido recibe el header CORS
- [ ] `[TC-004]` *[INTEGRATION]* — Origen no permitido / sin Origin, sin cambios
- [ ] `[TC-005]` *[INTEGRATION]* — `cap sync` referencia appId/webDir correctos
- [ ] `[TC-006]` *[INTEGRATION]* — Cleartext permitido en la config de red

## History
| # | Date | Event | Verdict | Smoke | Summary |
|---|---|---|---|---|---|
| 1 | 2026-09-18 | plan | — | — | Spec creada — 4 tareas, 6 test cases. Empaquetar el frontend existente como app Android vía Capacitor, con base URL de API configurable y CORS en el backend; la compilación/corrida final en Android Studio queda como paso manual del usuario. |
