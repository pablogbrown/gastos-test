# Run report — usuarios-auth

- **Run ID**: usuarios-auth-2026-09-11T213818Z
- **Feature branch**: feat/usuarios-auth (PR #8, open, not draft)
- **Started**: 2026-09-11T21:38:18Z
- **Completed**: 2026-09-14T13:10:00Z

## Layers

| Layer | Sub-specs | Outcome | PR | Collisions |
|---|---|---|---|---|
| 0 | auth-backend | verified | #10 (merged into feat/usuarios-auth) | none |
| 1 | auth-frontend | verified | #11 (open, mergeable) | none |

## Verification

Both sub-specs verified independently against their own branch (new commits + `status.yaml` advanced past `in-progress`) — never taken on the dispatched builder's own report alone. Both had a real gap the builder's own sandbox couldn't close, closed by the coordinator directly:
- `auth-backend`: manual JWT smoke test (registro/login/crear casa/401/GET casas/mias) against a real running backend.
- `auth-frontend`: full TC-007 E2E scenario against a real backend + frontend + Chrome (the builder's sandbox had no live browser).

## Incidents

- **Cross-feature integration bug, found between layers**: before dispatching layer 1, the coordinator merged `main` (containing the already-merged `ui-modernization` and `dockerize-local-env`, plus a standalone bugfix PR #9) into `feat/usuarios-auth`, since `auth-frontend` needs `ui-modernization`'s theme/shell. That merge surfaced a real bug invisible to any single feature's own build: migration `0001_casas_miembros.py` created `miembros` with a FK to `usuarios` before that table existed, which SQLite tolerates but PostgreSQL rejects at `CREATE TABLE` time. Fixed directly on `feat/usuarios-auth` (commit `1059ec4`), verified against a real, fresh `docker compose` Postgres — not just SQLite.
- **PR merges required human action**: `gh pr merge` is blocked by this environment's safety classifier for every PR in this run (#6, #7, #9, #10), same as the `gestion-domestica` run before it. The human merged each one manually.

## Ship-eligibility

**`usuarios-auth` is now ship-eligible**: both sub-specs `verified`, `auth-backend`'s PR #10 merged into `feat/usuarios-auth`. `auth-frontend`'s PR #11 is open and mergeable — merge it into `feat/usuarios-auth`, then merge the feature's own PR #8 into `main`, then `/nybo-ship usuarios-auth`.

**The orchestrator does not invoke `/nybo-ship`** — that remains the human's own final decision, batched together with `dockerize-local-env` and `ui-modernization` per the user's own request to ship all 3 initiatives at once.

## Cleanup

Once each sub-spec's PR is merged, remove its worktree:
```
git worktree remove .claude/worktrees/feat-usuarios-auth--auth-backend
git worktree remove .claude/worktrees/feat-usuarios-auth--auth-frontend
```
