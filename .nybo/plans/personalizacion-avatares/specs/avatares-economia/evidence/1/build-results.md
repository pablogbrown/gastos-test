---
feature: personalizacion-avatares/specs/avatares-economia
schema: build-results/2
cycle: 1
updated: '2026-09-23T19:07:04.880Z'
exit: ready
verdict: verified
judgment:
  entries: 3
observations:
  entries: 3
tests:
  backend:
    passed: 413
    failed: 0
    skipped: 1
  frontend:
    passed: 183
    failed: 0
build: passed
lint: passed
coverage: unavailable - not configured
---
### Goal

Implementar la spec fundacional `avatares-economia` (4 tasks): ledger de créditos + hook en `completar_tarea` (T1), catálogo `AvatarPersonaje` + seed curado (T2), desbloqueo por nivel + selección + endpoints (T3), y componente `LottieAvatar` + `avatarClient.ts` (T4). Fundación de la que dependen `tienda-accesorios` y `perfil-avatar-ui` — la estabilidad de sus interfaces exportadas importa especialmente.

### Judgment

- **J001** (spec-deviation, settled — L2): routes nested as `/casas/{casa_id}/miembros/{miembro_id}/...`, not spec.md's literal bare `/miembros/{miembro_id}/...` — matches every other authenticated route (`resolver_actor_en_casa` requires `casa_id`; Vite's dev proxy only forwards `/casas`/`/auth`). PUT is self-service only (actor must equal miembro_id, 403 otherwise) — REQ-003/004 name no Administrador-on-behalf, unlike `completar_tarea`. The 3 GETs stay casa-wide readable (Ranking/Historial precedent).
- **J002**: avatar_service functions open their own session (`fn(miembro_id)`), not run-plan.json's literal `fn(session, miembro_id)` — matches this project's convention ([SERVP-01]: explicit session only for a function called from within another service's own transaction). All 7 functions are called directly from routes.
- **J003** (new-dependency, always defers; plus environment-blocker on seed content): `lottie-react` per pre-approved D-01. Installed real v3.1.2 — a full API rewrite from D-01's v2-era description (named `Lottie` export, `src` prop not `animationData`); implemented against the real API. T2's seed uses 10 placeholder `lottie_url` values (no CDN-fetch access in this env, anticipated by the human) — documented in migration 0022's docstring + suggestions.yaml S001. Model/mechanics/live smoke test are 100% real.

### Observations

- [DOMAIN candidate, services — promoted, see Curation] `completar_tarea`'s 3 post-commit hooks (actividad/logros/now credits) each need their own service mocked+migrated in every calling test fixture — several pre-existing fixtures were silently relying on full-suite collection-order luck rather than doing this; fixed in this spec's own new files. See `[SERVG-03]`.
- [DOMAIN candidate, db — promoted, see Curation] `src/db/models/__init__.py` eagerly imports `Miembro` (not `Usuario`) — any ORM query anywhere then needs `Usuario` already imported somewhere in-chain, even with no real Usuario row. See `[DBG-06]`.
- [QUESTION for the human, see suggestions.yaml S002] lottie-react's real v3.1.2 API (named `Lottie`, `src` prop) differs from D-01's v2-era rationale text (`animationData`, default export) — no risk here, but flag it before `perfil-avatar-ui` reads D-01 at face value.

### Verification

**Build**: `npm run build` — green. **Backend**: `pytest tests/` — 413 passed, 1 skipped (pre-existing, unrelated). **Frontend**: `npm run test -- --run` — 183 passed. **Lint**: clean. **Coverage**: `unavailable — not configured` (stack.yaml's `quality_tools.coverage.tool: null`, predates this spec; remedy `/nybo-brownfield-bootstrap --quality`).

**Test cases — all 9 resolved, none deferred** (`[E2E]`/`[MANUAL]`: none in this spec): TC-001/002 `creditos.test.py`; TC-003 + TC-004-first-half `avatar_catalogo.test.py`; TC-004-second-half/005/006/007/008 `avatar_seleccion.test.py`; TC-009 `LottieAvatar.test.tsx`.

**Live evidence (Outcome Smoke Test, spec.md's 5 steps, driven live end-to-end)**: real Postgres unreachable from this sandbox (this worktree's own `docker-compose` would collide on host ports with the main worktree's already-running stack, which runs the WRONG code for this branch). Ran a real `uvicorn src.api.main:app` from this worktree instead (SQLite fallback, real migrations, real HTTP, zero fixtures) on a free port. Confirmed live: (1) créditos start at 0; (2) completing a 15-pt task raises créditos to 15, matching puntos exactly; (3) Novato Ana sees only the 3 Novato razas; (4) completing a 2nd task to 55 puntos live-unlocks Activo razas with no cache lag; (5) PUT selects an Activo raza (200, GET echoes it), and both 403 paths (nivel insuficiente; non-self PUT) confirmed live too.

**Security**: PUT self-service-only; avatar_personaje_id server-validated against `listar_avatares_disponibles`; no new secrets. **Design/wiki alignment**: ledger-not-counter (SERV-01-adjacent), NIVELES/`_nivel_de` reused with zero duplication (REQ-003), LottieAvatar has no `src/frontend/api/*` import (REQ-005), `ranking_service.py`/gamificacion-puntos untouched (`git diff` confirms).

### Curation

Promoted 2 Observations to permanent domain memory (severity-gated — real, project-wide conventions): `services.md` `[SERVG-03]` (every `completar_tarea` test fixture must mock+migrate ALL its hooks' own services, not just the feature under test's); `db.md` `[DBG-06]` (`src/db/models/__init__.py`'s eager `Miembro` import needs `Usuario` imported somewhere in-chain for any ORM query, even sans a real Usuario row). Did NOT run `nybo doctor --fix` to regenerate the derived `.claude/rules/*` summaries — it touched unrelated specs/files repo-wide (other features' evidence-folder layout, global config, unrelated domain indices) with no way to scope it to just this spec's two new entries; reverted that attempt and left the regeneration as a human follow-up instead (see suggestions.yaml S004). Left suggestions.yaml-only (not domain-memory-worthy): S001 (placeholder Lottie assets — data/content, not a convention), S002 (lottie-react v3-vs-D-01 mismatch — spec-specific advisory for `perfil-avatar-ui`).
