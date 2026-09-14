# Build Results — Cycle 1 — dockerize-local-env

## Summary
All 4 tasks (T1–T4) implemented and verified with a real Docker daemon
(available in this build environment, contrary to the initial assumption
in the dispatch brief). TC-001, TC-002, TC-003, TC-004, TC-006 are
genuinely green, executed against real Docker/Postgres, not just
statically reviewed. TC-005 is green for its HTTP proxy leg (frontend
Vite dev server → backend, via real HTTP through the dockerized proxy);
the actual browser-driven UI flow (open http://localhost:5173, fill the
"Crear casa" form, see it reflected on Inicio) was not driven by an
automated browser in this session — see Observations.

## Judgment Log

1. **T2 — extracted proxy-target logic into its own module instead of
   inline in `vite.config.ts`.** `run-plan.json` listed only
   `Dockerfile.frontend`/`vite.config.ts` as T2's touched files. Importing
   `vite.config.ts` directly from the new regression test
   (`tests/unit/frontend/vite-proxy-config.test.tsx`) broke esbuild under
   vitest with `Invariant violation: "new TextEncoder().encode("")
   instanceof Uint8Array" is incorrectly false` (esbuild loaded through
   vite.config.ts's own `vite`/`@vitejs/plugin-react` imports). Fix:
   moved the logic to `src/frontend/config/apiProxyTarget.ts`, imported
   by both `vite.config.ts` and the test. Deviation stays inside T2's
   scope (frontend proxy config); one extra file, no behavior change.
2. **T2 — avoided adding `@types/node` for typing `process`.** TypeScript
   flagged `process` as undeclared (project has no `@types/node`). Adding
   it would be a new-dependency decision, which is never settleable at
   any trust level (per `resolveDecisionAuthority()`). Used a minimal
   local ambient declaration
   (`declare const process: { env: Record<string, string | undefined> }`)
   in `apiProxyTarget.ts` instead — zero new dependencies, same effect.
3. **T3 — hardened the `db` healthcheck to force TCP
   (`pg_isready -h 127.0.0.1 ...`) instead of the plan's plain
   `pg_isready -U ... -d ...`.** The postgres image's own entrypoint runs
   a temporary, Unix-socket-only Postgres instance during first-boot init
   before starting the final instance (which serves both the Unix socket
   and TCP). `pg_isready` without `-h` connects via the Unix socket by
   default and can report "accepting connections" against that temporary
   instance before the final instance (and its TCP listener, which is
   what `backend` actually connects through) is really up. Forcing `-h
   127.0.0.1` makes the healthcheck test the exact same TCP path
   `backend`'s `depends_on: condition: service_healthy` is meant to
   guarantee. Kept `retries: 30` (up from the plan's 20) for margin.
   Spec-deviation, within L2's settleable authority (infra
   robustness, no behavior change to the app).
4. **T3 — retry loops in `docker_compose_up.test.sh`.** Initial versions
   asserted TC-002/TC-005 on a single attempt right after the first
   successful `/health`. Wrapped both assertions (not just the readiness
   probe) in short retry loops (up to ~15s) for defensiveness. In this
   specific build session, the failures this caught during development
   turned out to be caused by a stray non-Docker process already bound to
   host ports 8000/5173 from outside this session (see Observations) —
   the retry loops are still good, cheap defensive practice for a
   container-orchestration integration test independent of that specific
   cause, so kept.

## Observations (for curate)

- **This sandbox had stray native (non-Docker) processes already bound
  to ports 8000 and 5173** (`uvicorn src.api.main:app --host 127.0.0.1
  --port 8000` and a `vite --port 5173` from the main worktree,
  unrelated to this build) at various points during this session. They
  silently intercepted `curl`/browser requests meant for the dockerized
  services on the same ports, producing confusing, hard-to-diagnose
  failures (a POST that looked successful but never persisted to the
  real dockerized Postgres). Cost significant debugging time. Worth a
  convention: before trusting `docker compose` port-published behavior
  in this environment, check `lsof -i :<port>` for stray host processes
  holding the same ports first.
- Confirmed (independently of the above) a real, separate Docker Desktop
  networking quirk in this sandbox: connecting to a published port via
  the IPv6 loopback (`::1`) did not reliably reach the container's Vite
  dev server proxy, while IPv4 (`127.0.0.1`) did. All new test scripts
  use `127.0.0.1` explicitly rather than `localhost` for this reason.
- `src/db/types.py`'s `GUID` (CHAR(36)) and the standard SQLAlchemy
  `Enum` columns (`RolEnum`, `EstadoTareaEnum`, `TipoActividadEnum`) are
  genuinely portable to PostgreSQL — no dialect issues found; all 4
  migrations create their tables/enum types cleanly on a real Postgres
  16, confirmed via `tests/integration/db/postgres_migrations.test.py`.
