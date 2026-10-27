---
Title: skill-knowledge-curator scripts
Category: catalog
Status: current
Authority: local-supplement; measured 2026-10-27
Scope: The kc front end and the knowledge_curator_lib modules: inputs, outputs, safety labels, exit codes and runtime
Last reviewed: 2026-10-27
Summary: >-
  One front end (knowledge_curator.py, alias kc) over a layered library; read-only unless --apply; ledger.py is the only writer; seams isolate
  markdown-it-py, jsonschema, RapidFuzz, PyYAML and the optional sentence-transformers.
---

# skill-knowledge-curator scripts

## Contents

- [Front end](#front-end)
- [Library modules](#library-modules)
- [Exit codes and runtime](#exit-codes-and-runtime)

## Front end

`knowledge_curator.py <command> --project <dir> [options]` (or `just kc <command> <dir> ...`). Prints JSON with `elapsed_s` (except `review`, which prints Markdown).

| Command        | Inputs                                               | Writes with --apply                                             | Safety                                                     |
| -------------- | ---------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------- |
| `init`         | -                                                    | `.kc/config.yaml`, `.kc/.gitignore`                             | never overwrites an existing config                        |
| `inventory`    | -                                                    | `.kc/sources.jsonl`, `sections.jsonl`, `reports/inventory.json` | reads sources; `git rev-parse` with a 10 s timeout         |
| `worksheet`    | `--batch N`                                          | -                                                               | read-only                                                  |
| `coverage`     | -                                                    | -                                                               | read-only                                                  |
| `claims`       | `--file` (.json/.jsonl)                              | `.kc/claims.jsonl`                                              | whole batch refused on any error                           |
| `candidates`   | -                                                    | -                                                               | read-only; in-memory FTS5                                  |
| `relate`       | `--file`                                             | `.kc/relations.jsonl`, `conflicts.jsonl`, `claims.jsonl`        | whole batch refused on any error                           |
| `review`       | -                                                    | `.kc/reports/review-queue.md`                                   | exit 2 while conflicts are open                            |
| `decide`       | conflict, action, `--reason`, action options         | `.kc/decisions.jsonl`, `conflicts.jsonl`, `claims.jsonl`        | re-checks evidence first (exit 5 on change)                |
| `render`       | `--check`                                            | `knowledge/*`, `.kc/proposals/*`                                | never overwrites a promoted page; refuses secret-like text |
| `promote`      | `--page`, `--approve-digest`, `--reason`, `--revoke` | promotion record, re-rendered pages                             | gates must pass; digest-bound                              |
| `archive-plan` | -                                                    | `.kc/archive-plans/<batch>.json`                                | never moves sources; rehearsal in a temp folder            |
| `query`        | text, `--limit`, `--history`                         | -                                                               | read-only                                                  |
| `intake`       | `--payload`                                          | -                                                               | read-only                                                  |
| `validate`     | -                                                    | -                                                               | read-only; exit 3 or 5 on errors                           |
| `report`       | -                                                    | -                                                               | read-only                                                  |

## Library modules

`scripts/knowledge_curator_lib/`, lowest layer first. Feature modules depend on the layers below, never on each other's private helpers.

| Module                                                        | Role                                                                                 |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `errors.py`                                                   | Error classes carrying exit codes                                                    |
| `settings.py`                                                 | Names, vocabularies (mirror the schemas), defaults, config loader                    |
| `ids.py`                                                      | Hashes, canonical JSON, content-derived IDs, normalisation                           |
| `yaml_io.py`, `schema.py`, `mdparse.py`, `fuzzy.py`, `nli.py` | Seams: PyYAML, jsonschema, markdown-it-py, RapidFuzz, optional sentence-transformers |
| `ledger.py`                                                   | The only writer: lock, append-only JSONL, atomic file replace, path containment      |
| `state.py`                                                    | Folds the ledgers into current state; effective disposition                          |
| `inventory.py`                                                | Discovery, fingerprints, renames, removals, sections                                 |
| `evidence.py`                                                 | Span verification and recheck                                                        |
| `claims.py`                                                   | Claim intake, coverage, worksheet                                                    |
| `candidates.py`                                               | Candidate pairs and signals                                                          |
| `relations.py`                                                | Relation intake and automatic dispositions                                           |
| `decisions.py`                                                | Review cards and decisions                                                           |
| `render.py`                                                   | Deterministic pages and index.json; secret scan                                      |
| `promote.py`                                                  | Gates and promotion records                                                          |
| `archive_plan.py`                                             | Candidates, referrers, restore rehearsal                                             |
| `query.py`, `intake.py`, `validate.py`, `report.py`           | Retrieval, caller intake, gates, status                                              |
| `commands.py`                                                 | One function per subcommand (keeps the front end small)                              |

## Exit codes and runtime

Exit codes: 0 ok, 1 bad input, 2 review needed, 3 validation failed, 4 conflict blocker, 5 source changed, 6 I/O, lock or restore failure.

Budget: under 2 s per kernel command on a 50-document project. Measured 2026-10-27 (M2 Max, Python 3.14.5): test suite 1.1-1.8 s; `inventory` dry run over 24 files and 213 sections 0.14 s. Promoted
from this session: every script here is reusable across projects by design; no one-off scripts were kept.

## Governance recipes (skill-ai-it)

- `just check`: the project's governance checks, then document freshness and file roles. Read-only; `safe`.
- `just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.
- `just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.
- `just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
- `just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.
- `just section <file.md> "<title>"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.
