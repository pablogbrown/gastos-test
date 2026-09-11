# suggestions.yaml format

**Location:** `.nybo/plans/<feature-name>/evidence/suggestions.yaml`

**Purpose:** Post-implementation suggestions for the human: quick wins, future work, tech debt, and open questions. Suggestions outlive their feature and are read across features, so the id is data, not formatting — YAML makes it structural.

**Written by:** the executor at BUILD exit. Read by the dashboard's Suggestions tab and, directly, by a live agent session (`nybo suggestions` — the CLI command that used to read this file — is retired; nybo-phase-cli-consolidation).

**Format:**

```yaml
feature: <feature-name>
suggestions:
  - id: S001
    category: quick-win        # quick-win | enhancement | tech-debt | question
    title: One-line summary
    detail: >-
      Optional longer explanation — why it matters, what it touches.
    scope: out-of-spec         # optional: out-of-spec | follow-up | deferred
    status: open               # optional: open (default) | done
```

**Rules:**

- Sequential ids: `S001`, `S002`, … Unique within the feature; they survive edits and can be referenced from a follow-up spec or a commit message.
- `id`, `category` and `title` are required. An entry missing `id` or `title` is skipped.
- An unrecognised `category` reads as `other` rather than failing — the file is advisory and never gates.
- Generate it after all tasks complete. Omit the file entirely when there are no suggestions; an empty `suggestions:` list is equally fine.

**`status` — has the work happened?**

- `open` (the default) or `done`. **Absent reads as `open`**, so every file written before this field existed reads as a fully-open backlog — the correct interpretation, since nothing was ever recorded as done. No migration needed.
- **Set `status: done` the moment the suggestion is actually addressed in-session** — someone fixed it while the feature was still in flight, whether that was verify's own in-session fixing or a `/nybo-fix` pass the human asked for at BUILD's checkpoint. Never set it speculatively, and never for work merely planned.
- **`status` is not `scope`.** `scope` says whether the work *should* happen now; `status` says whether it *has* happened. `scope: follow-up, status: done` is a normal combination — filed as later work, then someone did it anyway.
- **There is no `declined`.** A suggestion nobody intends to do stays `open`: it is still an unaddressed idea, and that is honest. A deliberate decision *not* to do it belongs in `evidence/decisions.yaml`, the artifact that exists to record exactly that kind of call.
- `feat/99-progress.md`'s `## Suggestions` roster mirrors this field — `[x]` iff `status: done` — and `nybo validate --phase build` reports any disagreement between the two, in both directions.

**Superseded:** this replaces the old markdown `suggestions.md` with its `## Quick Wins` / `- **[S001]**` shape. That format had two divergent parsers — one required the bold-bracket form and returned nothing otherwise, the other accepted bare bullets and generated `<spec>-N` ids — so the same file yielded different counts and different identifiers depending on the caller.
