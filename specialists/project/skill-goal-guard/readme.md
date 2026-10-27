# skill-goal-guard (alias skill-gg)

GoalGuard: owner-approved MVP scope gate and solo portfolio focus for coding agents working in `project_stuff/`. Current status: [SKILL.md](SKILL.md) (Orient first, item 1).

## Folder index

- [SKILL.md](SKILL.md) — activation surface and routing table
- [AGENTS.md](AGENTS.md) — agent policy for this pack
- [references/](references/) — the consolidated rules, one topic per file
- [scripts/](scripts/readme.md), [tests/](tests/), [examples/](examples/) — v0.1 prototype CLI, its tests and fixtures
- [documents/](documents/) — verbatim captures from live systems (Vikunja OpenAPI)
- [SCRATCHPAD.md](SCRATCHPAD.md) — working state and next actions
- [docs/catalog.md](docs/catalog.md) — catalog of every file, decisions, where each source conflict is settled
- [docs/](docs/) — verbatim source documents (v1.7 handoff and kickoff, research pack, v0.1 skill)
- [changelog.md](changelog.md), [roadmap.md](roadmap.md) — history and next steps

## Run

```bash
just bootstrap   # once: builds the venv in skills-working-cache/skill-goal-guard
just check       # tests and example validation
just next examples/portfolio.json 2026-10-27
```
