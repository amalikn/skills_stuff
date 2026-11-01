---
Title: skill-knowledge-curator Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: Agents changing the skill-knowledge-curator pack (alias skill-kc)
Last reviewed: 2026-10-27
Summary: Layout, working rules and done checks for the Knowledge Curator pack; code follows skill-coder.
---

# AGENTS.md

Knowledge Curator pack. Entry point for users of the skill: [SKILL.md](SKILL.md). This file is for agents changing the pack.

## Layout

| Path                      | Role                                                                                                                                                                    |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SKILL.md`, `references/` | The skill and its consolidated rules (canonical)                                                                                                                        |
| `docs/`                   | Operator-supplied source documents, kept as supplied apart from front matter, Contents and one redrawn diagram; [docs/catalog.md](docs/catalog.md) records decisions and settled conflicts |
| `schemas/`                | JSON Schemas for agent input; `settings.py` vocabularies must match (tests/test_contract_seams.py)                                                                      |
| `scripts/`                | `knowledge_curator.py` front end, `knowledge_curator_lib/` package; catalogue in [scripts/readme.md](scripts/readme.md)                                                 |
| `tests/`                  | unittest suite and `fixtures/pilot` (synthetic, invented facts)                                                                                                         |

Venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-knowledge-curator/.venv` (built by `just bootstrap`), never inside this folder.

## Working rules

- **Aim** (operator, 2026-11-01): kc extracts knowledge and information out of data and avoids noise. Judge a change by noise removed first and recall second; a higher conflict count is not progress.
- **Triage** (operator, 2026-11-01): kc reports real conflicts, resolves what it can, questions the rest, and clears noise.
  Automatic resolution needs a source that states the answer (an explicit supersession, a dated replacement, a higher-authority document) and high confidence; each is logged with its evidence and reversible; P0, safety and security stay with the operator.
  Noise is dismissed with a reason and the record kept, identified by intelligent algorithms and tools. Until a blind sample of at least 40 automatic decisions is 95% right, they stay proposals the operator confirms in bulk. This narrows INV-007, only for what the rule allows.
- **Tools and models** (operator, 2026-11-01): build scripts that use purpose-built tools and models for this work, local first and an optional install, rather than relying on agents reading everything.
- **All code follows skill-coder** (operator, 2026-10-20): purpose header with run line and safety, Google docstrings, `--apply` gated in the writer (`ledger.py` is the only writer), timeouts on
  subprocesses, a seam module per third-party package, tests, measured runtime, two-space indent, ruff.
- Settle any conflict between the two source documents with the operator and record it in `docs/catalog.md`; never edit both sides speculatively.
- A new vocabulary value changes the schema and `settings.py` together.
- Keep `references/` and the code in step: a behaviour change updates the reference that describes it in the same change.

## Done checks

`just check` (ruff, tests, skill-coder helpers, doc freshness, file roles) passes; [references/evaluation.md](references/evaluation.md) status updated; changelog line added.

- Governed files: triage with `just docs <folder>` (one header line per file); run `just stale`; old CHANGELOG and SCRATCHPAD entries live in `docs/history/`, read only on need (`just history <term>`,
  `just history-show <stamp>`). Large Markdown: `just outline <file>`, then `just section <file> "<title>"` or a ranged Read.
