---
Title: skill-goal-guard (alias skill-gg)
Category: readme
Status: current
Authority: canonical
Scope: Root README.md of skill-goal-guard
Last reviewed: 2026-10-27
Summary: "Front door for people: what the project is, quick start, folder index and where the detail lives."
Review by: 2026-11-26
Budget: 200 lines, 25 KB
---

# skill-goal-guard (alias skill-gg)

Goal Guard: owner-approved MVP scope gate and solo portfolio focus for coding agents working in `project_stuff/`. Current status: [SKILL.md](SKILL.md) (Orient first, item 1).

## Folder index

- [SKILL.md](SKILL.md) — activation surface and routing table
- [AGENTS.md](AGENTS.md) — agent policy for this pack
- [references/](references/) — the consolidated rules, one topic per file
- [scripts/](scripts/readme.md), [tests/](tests/), [examples/](examples/) — the pilot tools (seven front ends over `goal_guard_lib`), their tests and fixtures
- [docs/goal-guard-flows/](docs/goal-guard-flows/) — flow diagrams: source in `parts/`, assembled `goal_guard_flows.yaml` and rendered `goal_guard_flows.drawio` (`just flows`)
- [AI_NAVIGATION.md](AI_NAVIGATION.md), [context-map.yaml](context-map.yaml) — agent entry point and routing map (skill-ai-it)
- [documents/](documents/) — verbatim captures from live systems (Vikunja OpenAPI)
- [SCRATCHPAD.md](SCRATCHPAD.md) — working state and next actions
- [docs/catalog.md](docs/catalog.md) — catalog of every file, decisions, where each source conflict is settled
- [docs/](docs/) — verbatim source documents (v1.7 handoff and kickoff, research pack, v0.1 skill)
- [changelog.md](changelog.md), [roadmap.md](roadmap.md) — history and next steps

## Quick start

```bash
just bootstrap   # once: builds the venv in skills-working-cache/skill-goal-guard and installs requirements.txt
just check       # ruff, tests, skill-coder helpers, governance checks, example fixture
just assess      # verdict for the example proposal against the example tasks
just next        # What's Next for the example project
```
