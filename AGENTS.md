<!-- NYBO: Start -->
Extends: @AGENTS.md (universal hard rules, approach check, end-to-end checklist).

## CORE.md

@.nybo/memory/CORE.md

This project uses nybo to run its SDLC through specs — `/nybo-plan`, then `/nybo-build`, then `/nybo-ship`. A multi-spec feature is coordinated with `/nybo-orchestrate`. nybo curates its memory under `.nybo/foundation/` and `.nybo/memory/` as features complete. Run `/nybo-explain` for the full lifecycle, trust model, and capability index.
<!-- NYBO: End -->

## Quick Reference

```bash
# Dev
npm run dev
# Build
npm run build
# Test
npm run test
# Lint
npm run lint
```

## Project Conventions

<!-- Seeded at init. `nybo curate` will add more after feedback sessions. Do not edit manually. -->
- Follow project conventions
- Keep generated files under 500 lines
- Use Mermaid for flow/sequence diagrams in specs

## Project Memory & Conventions

- **Conventions**: `.nybo/foundation/conventions.yaml`
- **Domain map**: `.nybo/foundation/domains.yaml` (per-domain detail: `.nybo/memory/domains/<name>.md`)
- **Architectural decisions**: `.nybo/foundation/adrs/`
