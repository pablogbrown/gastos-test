---
feature: mantenimiento-casa
schema: build-results/2
cycle: 1
updated: '2026-09-16T21:22:02.327Z'
exit: ready
verdict: verified
judgment:
  entries: 4
observations:
  entries: 2
tests:
  pytest:
    passed: 328
    failed: 0
    skipped: 1
  vitest:
    passed: 120
    failed: 0
build: pass
lint: pass
---
### Goal

Implementar mantenimiento-casa completa: T1 (modelo + migración 0017), T2 (mantenimiento_service: alta/materiales/completar/alerta), T3 (rutas + mantenimientoConAlerta en dashboard), T4 (pantalla Mantenimiento + banner Inicio + nav agrupada). TC-001 a TC-010 en verde.

### Judgment

- **J001** T1: `0017` confirmado como próximo número libre (último `0016`) antes de crearla.
- **J002** T2: `crear_item`/`completar_item` fuerzan la carga de `materiales` (`list(item.materiales)`) antes de retornar — `expire_on_commit=True` + cierre de sesión en `finally` causaba `DetachedInstanceError`; `listar_items` usa `selectinload`. No documentado antes — candidato a curate.
- **J003** No se instaló tooling de coverage nuevo (`pytest-cov`/`@vitest/coverage-v8` ausentes) — `new-dependency` siempre difiere a humano en L2; registrado en `decisions.yaml`. Compensado con 33 tests nuevos/actualizados cubriendo cada rama.
- **J004** T4: `AppShell.test.tsx` no necesitó cambios pese a la anticipación de la spec — ya lee `GRUPOS_DESKTOP` dinámicamente.

### Observations

- **[DOMAIN candidate — db.md]** Un modelo con `relationship(..., cascade="all, delete-orphan")` leído por el caller tras cerrar su sesión necesita eager-load explícito (`list(x.relacion)` o `selectinload`) — `SessionLocal` usa `expire_on_commit=True`. Primer caso: `ItemMantenimiento.materiales`.
- **[DOMAIN candidate — services.md]** El patrón recurrente+gate de `tarea_service` generaliza limpio a un segundo servicio independiente — confirma la convención de duplicar en vez de compartir código entre servicios.

### Verification

**Build**: `npm run build` — pass. **Tests**: `pytest tests/` 328 passed/1 skipped (pre-existente, requiere `DATABASE_URL` externo)/0 failed; `vitest run` 120 passed/0 failed. Cubre: 18 tests en `mantenimiento_service.test.py` (TC-001 a TC-008 + edge cases), assertions nuevas en `postgres_migrations.test.py`, 10 en `mantenimiento_routes.test.py` (TC-001-004/006/007 + dashboard + 401/403/404), 3 en `Mantenimiento.test.tsx` (TC-009 + completar/material), 2 en `InicioCasa.test.tsx` (TC-010). Fixtures pre-existentes de dashboard (`dashboard_service`/`dashboard_routes`/`balance_mensual`/`gasto_listar_mes`) actualizadas con migración `0017` + monkeypatch, mismo patrón que `0009`/`0011`.

**Coverage**: no medido (sin `pytest-cov`/`@vitest/coverage-v8` — `new-dependency` difiere, ver J003); compensado con cobertura exhaustiva manual.

**Test cases**: TC-001 a TC-010 resueltos por tests reales, sin `[E2E]`/`[MANUAL]`.

**Live evidence**: smoke en vivo contra `docker-compose` (Postgres real, backend `:8000`): alta de ítem recurrente con materiales → aparece en `mantenimientoConAlerta` a 5 días → completar antes de tiempo rechaza 409 → completar en fecha genera la siguiente instancia (+7 días) → esa nueva instancia rechaza completar el mismo día (409). Los 5 pasos observados como describe el Outcome/REQ-004. API-level (frontend cubierto por tests mockeados).

**Security**: sin secretos/dependencias nuevas; reutiliza `requiere_membresia_activa`, sin guard de rol (spec dice "un miembro puede...").

**Design principles**: entidad separada de `Tarea`, sin tabla/servicio compartido, por Design Rationale explícito de la spec.

**Wiki alignment**: [API-01] (alias camelCase solo en el contenedor) y convención de duplicación de `services.md` seguidos.

### Curation

Agregado [DBG-05] a db.md (force-load de relación to-many antes de cerrar sesión, o `DetachedInstanceError` — primer caso `ItemMantenimiento.materiales`). No se agregó entrada nueva a services.md por la confirmación del patrón recurrencia/gate — solo reconfirma SERVP-02 et al., sin instrucción nueva.
