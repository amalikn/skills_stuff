---
title: Archcore index — skill-coder
status: accepted
tags: [index]
---

Durable index of the decisions and rules recorded for skill-coder. Accepted documents are the highest-authority statement of what the pack has decided; supersede one in place with a dated note naming
its replacement rather than deleting it. All nine record operator decisions or stated rules of 2026-10-19, each from a source it names. Two (the runtime ADR and the code-map rule) were first written
outside skill-ai-it's `promote` mode and held as `proposed`; the operator approved their promotion the same day, after a review that also corrected four entries (2026-10-19, CHANGELOG).

## adr/

| Document                                    | Status   |
| ------------------------------------------- | -------- |
| [default-activation-waits-for-testing.adr.md](adr/default-activation-waits-for-testing.adr.md) | accepted |
| [helpers-run-in-target-environment.adr.md](adr/helpers-run-in-target-environment.adr.md) | accepted |
| [naming-mapping-is-data.adr.md](adr/naming-mapping-is-data.adr.md) | accepted |

## rules/

| Document                                    | Status   |
| ------------------------------------------- | -------- |
| [code-map-holds-decisions-only.rule.md](rules/code-map-holds-decisions-only.rule.md) | accepted |
| [cross-project-write-back.rule.md](rules/cross-project-write-back.rule.md) | accepted |
| [helpers-are-portable-and-catalogued.rule.md](rules/helpers-are-portable-and-catalogued.rule.md) | accepted |
| [pack-text-stays-generic.rule.md](rules/pack-text-stays-generic.rule.md) | accepted |
| [rule-precedence.rule.md](rules/rule-precedence.rule.md) | accepted |
| [rules-cite-sources.rule.md](rules/rules-cite-sources.rule.md) | accepted |

## Never promoted, and why

| Candidate area                                                                                               | Reason                                                                                |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| specs/ — claim ledger and code-map schemas                                                                   | Specified executably by `tests/test_package_contract.py` and `scripts/code_map.py`    |
| Rules from the global policy, governance `coding-guide.md` and project code designs                          | Governed at their source; the pack cites them                                         |
| The programming rules in `references/` and `languages/` (naming convention, layering, timeouts, write gates) | Pack content, governed in its reference files with claims in `sources.yaml`; an       |
|                                                                                                              |   Archcore copy would drift                                                           |
| Research sources verbatim under `documents/`; docstrings with Args and Returns; no inline linter suppression | Global policy and operator feedback rules, inherited                                  |
| "Fix the project, not the check" and the other governance-checker rules                                      | skill-ai-it's managed governance block in `AGENTS.md`, owned upstream                 |
| Package version only in the `CHANGELOG.md` release heading                                                   | A one-line file convention in `AGENTS.md`, not a decision; no check enforces it       |
| `SCRATCHPAD.md` open items (adopt helpers in another project, Ansible module limit, shell limits UNVERIFIED) | Unresolved; promote once decided                                                      |
