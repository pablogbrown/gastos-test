# Progress — Autenticación Backend

## Checklist

### Tasks
- [x] T1 — Data Layer: Usuario y FK Miembro.usuario_id
- [x] T2 — Service Layer: registro, login, hashing y JWT
- [x] T3 — API Routes: /auth/* y migración de las 4 rutas existentes
- [x] T4 — crear_casa/agregar_miembro vinculan al Usuario real

### Verify
- [x] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [x] `[TC-001]` *[UNIT]* — Registro crea Usuario con contraseña hasheada
- [x] `[TC-002]` *[UNIT]* — Email duplicado es rechazado
- [x] `[TC-003]` *[UNIT]* — Login con credenciales correctas devuelve JWT
- [x] `[TC-004]` *[UNIT]* — Credenciales incorrectas responden 401 sin distinguir causa
- [x] `[TC-005]` *[INTEGRATION]* — Request sin JWT válido responde 401
- [x] `[TC-006]` *[INTEGRATION]* — JWT válido resuelve el actor correctamente en rutas migradas
- [x] `[TC-007]` *[INTEGRATION]* — Un Usuario en 2 casas tiene 2 Miembros con el mismo usuario_id
- [x] `[TC-008]` *[UNIT]* — Agregar miembro por email vincula al Usuario existente
- [x] `[TC-009]` *[INTEGRATION]* — Usuario no-miembro de una Casa recibe 403
- [x] `[TC-010]` *[UNIT]* — GET /casas/mias devuelve exactamente las casas del usuario

## Completion Summary
Las 4 tasks implementadas end-to-end con TDD (Usuario, JWT, migración de
las 4 rutas existentes de `X-Usuario-Id` a `Authorization: Bearer`, y
vínculo real Usuario↔Miembro). Las 10 test cases de la spec están en
verde, más una batería adicional de regresión sobre las 4 specs ya
shippeadas de `gestion-domestica` (casas-miembros, gastos, tareas-puntos,
dashboard-actividad), cuyas 000+ suites de test tuvieron que actualizarse
porque este es un breaking change intencional (ver Judgment). Suite
completa: 127 tests en verde (`pytest tests/ --ignore=tests/unit/frontend`).
Recorrido end-to-end manual (registro→login→crear casa→agregar miembro
por email→GET /casas/mias→403 sin membresía) validado tanto en tests
automatizados (`tests/integration/api/auth_migration.test.py`) como con
un smoke test directo contra `src.api.main.app` vía `TestClient`.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 10 test cases. |
| 2 | 2026-09-11 | execute | T1 | TC-* (schema) | Usuario model, Miembro.usuario_id FK, migration 0005 (create+ALTER fallback), pyjwt/bcrypt added to requirements.txt. |
| 3 | 2026-09-11 | execute | T2 | TC-001..TC-005 | auth_service: registrar_usuario, autenticar_usuario, emitir_token, decodificar_token. InvalidCredentialsError added. |
| 4 | 2026-09-11 | execute | T3 | TC-005, TC-006, TC-009 | auth router (/auth/registro, /auth/login), src/api/dependencies.py (get_current_usuario, resolver_actor_en_casa), migrated casas/gastos/tareas/dashboard routers off X-Usuario-Id. |
| 5 | 2026-09-11 | execute | T4 | TC-007, TC-008, TC-010 | crear_casa decouples Miembro.id from usuario_id; agregar_miembro requires email_usuario (404 if unknown); listar_casas_de_usuario + GET /casas/mias. |
| 6 | 2026-09-11 | verify | — | 127/127 | Full pytest suite green (backend); end-to-end JWT flow validated via TestClient against the real app; ALTER TABLE fallback path in migration 0005 validated against a simulated pre-existing DB. |
