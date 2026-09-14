# Domain: infra

Local dev environment orchestration (Docker, docker-compose, Makefile) —
not the production deploy path (see `.nybo/foundation/stack.yaml`).

## Conventions
<!-- Each convention has metadata as an HTML comment -->
<!-- added: YYYY-MM-DD | feature: feature-name | confidence: high|medium|low | verified: YYYY-MM-DD -->

<!-- added: 2026-09-11 | feature: dockerize-local-env | confidence: high | verified: 2026-09-11 -->
- `Dockerfile.backend`/`Dockerfile.frontend` live at repo root (not
  `docker/` or `infra/`); `docker-compose.yml` references them via
  `build.dockerfile`. `DATABASE_URL` is injected only inside
  `docker-compose.yml`'s `backend` service — `src/db/base.py`'s
  `sqlite:///:memory:` fallback (used by the whole test suite and plain
  `uvicorn --reload` without Docker) is never touched by Docker wiring.
- `Makefile` at repo root is the single documented entrypoint for the
  dockerized local env (`up`, `down`, `build`, `logs`, `test`,
  `migrate`) — wraps `docker compose` so nobody needs to memorize its
  flags. `make test`/`make migrate` assume the stack is already up
  (`docker compose exec backend ...`), they don't bring it up themselves.
- Frontend env-driven config (e.g. Vite's dev-server proxy target) that
  needs to be both testable and used by `vite.config.ts` should live in
  its own small module (e.g. `src/frontend/config/*.ts`) rather than
  inline in `vite.config.ts` — importing `vite.config.ts` directly from
  a vitest test can break esbuild (observed:
  `Invariant violation: "new TextEncoder().encode("") instanceof
  Uint8Array" is incorrectly false`, triggered by vite.config.ts's own
  `vite`/`@vitejs/plugin-react` imports loading through vite-node).

## Patterns
<!-- Reusable patterns specific to this domain -->

<!-- added: 2026-09-11 | feature: dockerize-local-env | confidence: high | verified: 2026-09-11 -->
- Postgres service healthcheck: use
  `pg_isready -h 127.0.0.1 -U <user> -d <db>` (explicit `-h`, forcing
  TCP), not bare `pg_isready -U ... -d ...`. The official `postgres`
  image's entrypoint runs a temporary, Unix-socket-only server during
  first-boot init before starting the final server (which serves TCP
  too, same data dir). `pg_isready` without `-h` connects via the Unix
  socket by default and can report "healthy" against that temporary
  instance, before the final instance's TCP listener (the one any other
  service actually connects through via `depends_on`) is really up.
- Docker-compose readiness scripts in this repo poll `127.0.0.1`
  explicitly, never `localhost` — see Gotchas.

## Gotchas
<!-- Things that tripped us up -->

<!-- added: 2026-09-11 | feature: dockerize-local-env | confidence: medium | verified: 2026-09-11 -->
- In this dev sandbox, connecting to a docker-compose published port via
  the IPv6 loopback (`::1`, what `curl http://localhost:PORT` can
  resolve to first) did not reliably reach the container, while IPv4
  (`127.0.0.1`) did. Always use `127.0.0.1` explicitly (not `localhost`)
  in scripts that probe published ports.
- Before trusting any "it's not working" result against a
  docker-compose-published port in a shared/long-lived dev sandbox,
  check `lsof -i :<port>` for a stray *non-Docker* process already bound
  to that same host port from an unrelated earlier session — it can
  silently intercept requests meant for the container and produce very
  confusing, hard-to-diagnose failures (e.g. a POST that looks
  successful but never reaches the real dockerized database).
