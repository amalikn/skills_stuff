# skill-eval-manager

## Contents

- [Purpose](#purpose)
- [Package map](#package-map)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Source limitations](#source-limitations)
- [Governance pointers](#governance-pointers)

## Purpose

`skill-eval-manager` is a discipline and small-recordkeeping layer for evaluation suites over operational systems. It defines what an eval must prove and records what an external executor or human
observed. It does not run checks.

The package contains no non-OSI-licensed runtime dependency. The scripts use Python's standard library for JSON and JSONL. They also accept ordinary YAML when `PyYAML` is installed; JSON-formatted
documents with a `.yaml` extension remain valid YAML and work without it.

Last reviewed: 2026-09-23 AEST. Version: 0.1.2.

## Package map

`SKILL.md` is the operational entry point. `references/` contains the method. `schemas/` define the portable data contracts. `templates/` is a copyable suite. `scripts/` validate, append history, and
render reports. `examples/` contains network-controller and financial-reconciliation suites plus deliberately invalid fixtures. `evidence/` contains reproducible validation transcripts generated for
this release.

## Quick start

```bash
python3 scripts/validate_suite.py --suite templates/evals.yaml
python3 scripts/record_result.py --suite templates/evals.yaml --history history.jsonl --eval-id example.durable-state --slice-id all --verdict pass --measured-value '{"checked": 4, "expected": 4}' --evidence-ref docs/run-001.md
python3 scripts/render_report.py --suite templates/evals.yaml --history history.jsonl --output evaluation-report.md
```

The second command records an externally produced result; it does not run the executor the suite names (`checks/verify_state.py` in the template) <!-- path:example -->.

## Installation

After reviewing and unpacking this archive into the canonical authoring tree, an operator may install by symlink (not copy):

```bash
ln -s /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-eval-manager ~/.codex/skills/skill-eval-manager
ln -s /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-eval-manager ~/.claude/skills/skill-eval-manager
ln -s /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-eval-manager ~/.hermes/skills/skill-eval-manager
```

Do not run these commands until the destination locations and any existing links have been checked.

## Source limitations

The package was authored from the supplied prompt and read-only controller planning documents. The controller plan explicitly says it is not a record of implemented work, so its example has
synthetic/no-result history and does not claim live controller verification. No source file was modified.

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Script and task catalog: [scripts/README.md](scripts/README.md) and `just --list`
- Working notes and open operator decisions: [SCRATCHPAD.md](SCRATCHPAD.md)
- Change and governance history: [CHANGELOG.md](CHANGELOG.md)
- Design rationale: [BRIEF.md](BRIEF.md)
- Parent repo policy: [../../AGENTS.md](../../AGENTS.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

Runtimes are pinned in `.mise.toml` and the venv lives outside this repo, in the working-cache peer. Build it with `just bootstrap`; confirm it with `just runtimes`. Before calling package work
complete, run `just validate-all` and `just check`.
