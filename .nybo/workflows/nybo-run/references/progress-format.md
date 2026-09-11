# progress.md format

**Location:** `.nybo/plans/<feature-name>/feat/99-progress.md`

**Purpose:** Task checklist for the spec. One line per task; checkboxes show done vs pending.

**Format:**

- Use Markdown checkboxes: `- [ ]` for not done, `- [x]` for done.
- One task per line. Optional short note after the task text (e.g. `- [x] Add auth middleware (auth.middleware.ts)`).
- You may group tasks under headings (e.g. `## Backend`, `## Frontend`, `## Tests`).
- For blocked tasks, append a note: `— BLOCKED: <reason>` and keep the checkbox unchecked.

**Example:**

```markdown
# Progress: user-auth

## Backend
- [x] Add login endpoint and validation (auth.controller.ts)
- [x] Add token refresh (auth.service.ts)
- [ ] Add rate limiting — BLOCKED: waiting on config

## Frontend
- [ ] Login form and error handling
- [ ] Store token and attach to API client
```

## Test Cases, Decisions and Suggestions sections

Beyond the task checklist, this file carries three id-keyed rosters so the feature's
whole state reads from one place:

- `#### Test Cases` (under `## Checklist` → `### Verify`) — one row per `TC-xxx` in
  `spec.md`'s Test Cases section: `- [x] \`[TC-001]\` *[UNIT]* — <one-line restatement>`.
  `[x]` = proven. `[E2E]`/`[MANUAL]` rows stay `[ ]` and never gate the pass. The roster
  is checked against `spec.md` in both directions; the tick is not machine-checkable and
  is never flagged. A missing section is a warning, a wrong roster an error.

The other two mirror the verify pass's own evidence queues:

- `## Decisions` — one row per `evidence/decisions.yaml` entry: `- [x] \`[D001]\` — <summary>`.
  `[x]` iff that entry's `status: resolved`. `nybo validate --phase build` reports a row
  whose tick contradicts the queue, a queue entry with no row, and a row whose id is not
  in the queue.
- `## Suggestions` — one row per `evidence/suggestions.yaml` entry:
  `- [ ] \`[S001]\` *(quick-win)* — <title>`. `[x]` iff that entry's `status: done`
  (absent reads as `open`). Roster and tick are both checked, same as decisions.

**The three rosters are section-exclusive — never merged, never duplicated across
each other.** `#### Test Cases` holds `TC-xxx` rows and nothing else; `## Decisions`
holds `D0xx` rows and nothing else; `## Suggestions` holds `S0xx` rows and nothing
else. A `[D0xx]`/`[S0xx]` row appearing a second time under `#### Test Cases` (or a
`[TC-xxx]` row appearing under `## Decisions`/`## Suggestions`) is corruption, not a
cross-reference — each id lives in exactly one roster, in the one section that
mirrors its own source (`spec.md`'s Test Cases for `TC-xxx`, `decisions.yaml` for
`D0xx`, `suggestions.yaml` for `S0xx`). Never copy a roster's rows into another
roster's section for visibility or convenience.

- `#### Outcome Smoke Test` (same place) — the verify pass's live-evidence result for
  `spec.md`'s `## Outcome`: a headline `observed` / `not observed` / `skipped — <reason>`,
  then **one status per level** — `screen:` and `API:`, each `observed` / `not observed —
  <reason>` / `unavailable — <reason>` / `n/a` — plus the route actually driven. Two levels,
  two statuses: a single collapsed "observed at API level" is how a screen half nobody
  looked at gets read as done. The headline is `observed` only when every applicable level
  was; a level that was reachable and never driven is `not observed`, never `n/a`. Not a
  roster — nothing to enumerate, and no machine source for "observed" — so validate only
  warns when the section is missing entirely.
- `## History` (last section in the file) — add-only lifecycle log, newest first:
  `| # | Date | Event | Verdict | Smoke | Summary |`. **Row 1 is always the plan's own
  creation.** `Event` is `plan` (spec created), `replan` (spec edited and BUILD
  re-entered — the Summary carries *why*), `verify` (one execution), or `fix`
  (a `/nybo-fix` batch landed against this feature post-BUILD — the Summary names
  what the batch fixed). `Verdict`/`Smoke` are `—` on a `plan`/`replan`/`fix` row.
  A failed run gets a row like any other; past rows are never rewritten. A `replan`
  row is the only durable record of a revision's reason — `status.yaml` keeps just
  `last_revision`, which the next revision overwrites. A `fix` row is likewise the
  only durable record that a fix batch touched this feature at all outside its own
  PR — **every `/nybo-fix` pass that lands against an in-flight feature (this
  skill's "feature-branch case") adds one, the moment its combined verify goes
  green** — and when that batch resolved a `## Decisions` or `## Suggestions` entry,
  the same pass ticks that entry's row too (see those sections above): a fix that's
  real in the code but still `open`/unticked in these rosters is how something gets
  fixed twice.

**Section order is deliberate: Decisions and Suggestions come BEFORE the Checklist**,
because they are the two sections a reader has to act on. History goes last.

**Neither Decisions nor Suggestions exists until a verify pass writes its first entry**
— before that there is nothing to mirror, and validate requires nothing.

Update this file after each task during nybo-run execution.
