# Verify — Invitar a un miembro que todavía no tiene cuenta

## T1 — Columna `email_invitacion`

### Test Scenarios
- La migración corre limpia contra Postgres real y es idempotente (correrla dos veces no falla).
- `Miembro` acepta `email_invitacion=None` (fila existente/normal) y con valor (fila pendiente).

### Gate Criteria
- `[AUTO]` Suite completa en verde con el modelo actualizado.
- `[AUTO]` Test de migración contra Postgres real (mismo patrón que `postgres_migrations.test.py`, usando una base temporal — nunca la real, per el fix `fix-test-migraciones-borra-tabla-real`).

## T2 — Alta pendiente

### Test Scenarios
- Email sin Usuario registrado → 201, `usuario_id: null` (TC-001).
- Email con Usuario ya registrado → sigue vinculando de inmediato (TC-002).
- Mismo email invitado dos veces a la misma casa → segunda es 400 (TC-006).

### Gate Criteria
- `[AUTO]` TC-001, TC-002, TC-006 en verde.

## T3 — Vinculación al registrarse

### Test Scenarios
- Registro con email que tiene 1 pendiente → se vincula (TC-003).
- Registro con email que tiene pendientes en 2 casas → ambas se vinculan (TC-004).
- Registro con email sin pendientes → sin cambios, comportamiento actual intacto (TC-005).

### Gate Criteria
- `[AUTO]` TC-003, TC-004, TC-005 en verde.

## T4 — Frontend "Pendiente"

### Test Scenarios
- Fila con `usuario_id: null` → Chip "Pendiente", sin botón Desactivar (TC-007).
- Fila ya vinculada → Activo/Inactivo y Desactivar sin cambios (TC-008).

### Gate Criteria
- `[AUTO]` TC-007, TC-008 en verde.
- `[AUTO]` `npm run build` sin errores de tipos.

## End-to-End Verification
1. `pytest tests/` y `npm run test -- --run` en verde.
2. Smoke manual contra el docker-compose local: un Administrador agrega
   un miembro con un email nunca antes visto → aparece "Pendiente" en la
   tabla. Esa persona se registra con ese mismo email → sin ninguna
   acción extra, al volver a mirar Miembros esa fila ya dice "Activo".
3. Repetir el intento de invitar el mismo email pendiente dos veces →
   segunda vez, error 400 visible en la UI.

## Failure Triage

| If TC-XXX fails | Check first | Root cause pattern |
|---|---|---|
| TC-001 | ¿La rama `usuario is None` todavía lanza `NotFoundError`? | El `if usuario is None: raise ...` no se reemplazó, solo se agregó código muerto al lado |
| TC-003/004 | ¿`vincular_membresias_pendientes` normaliza el email (`.strip().lower()`) antes de comparar? | Comparación case-sensitive o con espacios contra `email_invitacion` guardado normalizado |
| TC-006 | ¿La query de duplicado pendiente filtra por `usuario_id.is_(None)`? | Sin ese filtro, chocaría también contra membresías ya activas de otras personas con `email_invitacion` residual |
| TC-007 | ¿El `Chip` de estado revisa `usuario_id` antes que `activo`? | Orden de condiciones invertido — una fila pendiente también tiene `activo=True` en la base, por diseño |
