# Domain: auth

auth domain

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-14 | feature: usuarios-auth (auth-backend) | confidence: high | verified: 2026-09-14 -->
- Backend identity resolution is centralized in `src/api/dependencies.py`:
  `get_current_usuario` (decodes the `Authorization: Bearer <jwt>` header
  via `auth_service.decodificar_token`, 401 on missing/invalid/expired)
  and `resolver_actor_en_casa` (maps the authenticated `Usuario` to their
  `Miembro` row for a given `casa_id`, 403 if not a member). Every
  protected route depends on these via FastAPI `Depends(...)` — no route
  reads `X-Usuario-Id` or any other identity header directly anymore.
  `Usuario.id` (global) and `Miembro.id` (per-casa) are deliberately
  different values since a Usuario can belong to more than one Casa; a
  new route needs the `Miembro`, not the `Usuario`, resolve it via
  `resolver_actor_en_casa`, never assume they're the same id.

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- added: 2026-09-14 | feature: usuarios-auth (auth-frontend) | confidence: high | verified: 2026-09-14 -->
- Frontend session/JWT handling is centralized in one module,
  `src/frontend/api/authClient.ts` — `guardarSesion`/`obtenerToken`/
  `cerrarSesion` (localStorage), `login`/`registrar` (calls to
  `/auth/login`/`/auth/registro`), and `fetchAutenticado` (a `fetch`
  wrapper every other API client uses instead of calling `fetch`
  directly — adds `Authorization: Bearer <jwt>` and triggers
  `cerrarSesion()` on any 401). Cross-cutting "session just ended"
  notification (both an explicit logout and an automatic 401 logout) is
  a tiny pub-sub, `suscribirseACierreSesion(listener)`, so `App.tsx` can
  react without every API client needing to know about React state.
  Any new frontend API client should call `fetchAutenticado` from this
  module, never send its own `Authorization`/`X-Usuario-Id` header, and
  never read `localStorage` directly.

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-14 | feature: usuarios-auth (auth-frontend) | confidence: medium | verified: 2026-09-14 -->
- `src/frontend/pages/Tareas.tsx`'s `puedeCompletar()` compares the
  authenticated Usuario's id against `tarea.responsableId`, which is
  actually a Miembro id (per-casa), not a Usuario id (global) — the same
  global-identity-vs-per-casa-identity conflation this domain's backend
  side already has (`resolver_actor_en_casa` bridges it server-side; no
  equivalent exists on the frontend yet). "Marcar completada" visibility
  for an assigned task is therefore not reliable against real data
  today — see `evidence/suggestions.yaml` in the `auth-frontend`
  sub-spec for the proposed follow-up.
