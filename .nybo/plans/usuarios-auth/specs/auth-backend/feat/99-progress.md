# Progress — Autenticación Backend

## Checklist

### Tasks
- [ ] T1 — Data Layer: Usuario y FK Miembro.usuario_id
- [ ] T2 — Service Layer: registro, login, hashing y JWT
- [ ] T3 — API Routes: /auth/* y migración de las 4 rutas existentes
- [ ] T4 — crear_casa/agregar_miembro vinculan al Usuario real

### Verify
- [ ] Verificación end-to-end de la spec

### Curate
- [ ] Extracción de convenciones/aprendizajes

#### Test Cases
- [ ] `[TC-001]` *[UNIT]* — Registro crea Usuario con contraseña hasheada
- [ ] `[TC-002]` *[UNIT]* — Email duplicado es rechazado
- [ ] `[TC-003]` *[UNIT]* — Login con credenciales correctas devuelve JWT
- [ ] `[TC-004]` *[UNIT]* — Credenciales incorrectas responden 401 sin distinguir causa
- [ ] `[TC-005]` *[INTEGRATION]* — Request sin JWT válido responde 401
- [ ] `[TC-006]` *[INTEGRATION]* — JWT válido resuelve el actor correctamente en rutas migradas
- [ ] `[TC-007]` *[INTEGRATION]* — Un Usuario en 2 casas tiene 2 Miembros con el mismo usuario_id
- [ ] `[TC-008]` *[UNIT]* — Agregar miembro por email vincula al Usuario existente
- [ ] `[TC-009]` *[INTEGRATION]* — Usuario no-miembro de una Casa recibe 403
- [ ] `[TC-010]` *[UNIT]* — GET /casas/mias devuelve exactamente las casas del usuario

## Completion Summary
Not yet started.

## History
| # | Date | Event | Task | Test | Note |
|---|---|---|---|---|---|
| 1 | 2026-09-11 | plan | — | — | Spec created — 4 tasks, 10 test cases. |
