---
Title: skill-knowledge-curator (alias skill-kc)
Category: readme
Status: current
Authority: canonical
Scope: Root README.md of skill-knowledge-curator
Last reviewed: 2026-10-27
Summary: "Front door for people: what the pack is, quick start, folder index and where the detail lives."
Review by: 2026-11-26
Budget: 200 lines, 25 KB
---

# skill-knowledge-curator

Knowledge Curator (alias skill-kc) turns a project's Markdown into evidence-linked claims, finds duplicates and conflicts, asks the operator targeted questions, renders derived knowledge pages,
promotes a page to authoritative behind gates, and plans (never performs) archiving of absorbed sources. Status: v1 kernel, tested on a synthetic fixture (2026-10-27).

## Quick start

```bash
just bootstrap                                  # venv in skills-working-cache
just check                                      # lint, tests, skill-coder and governance checks
just kc inventory /path/to/project              # read-only; add --apply to record
just kc worksheet /path/to/project              # pending sections for the agent to extract claims from
```

## Folders

| Path                        | What it holds                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [SKILL.md](SKILL.md)        | The skill: activation, workflow, standing rules                                                                 |
| [references/](references/)  | Workflow, claim model, conflicts, promotion, archive safety, invocation contract, evaluation, feature inventory |
| [scripts/](scripts/)        | `knowledge_curator.py` (kc) and `knowledge_curator_lib/`; catalogue in [scripts/readme.md](scripts/readme.md)   |
| [schemas/](schemas/)        | JSON Schemas for agent input                                                                                    |
| [tests/](tests/)            | unittest suite and the synthetic `fixtures/pilot`                                                               |
| [docs/](docs/)              | The two source documents and [docs/catalog.md](docs/catalog.md) (decisions, settled conflicts)                  |
| [SCRATCHPAD.md](SCRATCHPAD.md), [changelog.md](changelog.md) | Working state and change record                                                                                 |
