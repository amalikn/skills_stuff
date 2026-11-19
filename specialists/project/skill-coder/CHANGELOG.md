---
Title: skill-coder changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-coder pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Summary: Release history and governance changes of skill-coder; the release heading holds the version of record.
Last rotated: 20261119_1601
---

# Changelog

## Contents

- [Unreleased](#unreleased)
- [20261119_1631 — Periodic review; 90-day review window](#20261119_1631--periodic-review-90-day-review-window)
- [20261119_1601 — deterministic navigation-control upgrade](#20261119_1601--deterministic-navigation-control-upgrade)
- [20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records](#20261102_1347--learned-exit-trap-exit-code-ruff-through-a-symlink-tracker-from-records)
- [20261102_1132 — Learned: one write frame for many fields](#20261102_1132--learned-one-write-frame-for-many-fields)
- [20261101_2353 — Learned: guard first and dry-run a gate that hides records](#20261101_2353--learned-guard-first-and-dry-run-a-gate-that-hides-records)

---

## Unreleased

- 2026-11-19: logged late (no line existed): references/design-patterns.md Learned 2026-11-05, model judgement call and MCP pilot chaining (two entries).
- 2026-11-19: logged late: references/errors-and-timeouts.md Learned 2026-11-10, stopping the process that holds an `flock`.
- 2026-11-19: logged late: references/generated-artifacts.md Learned 2026-11-12, a second easier-to-read format of a data file (JSON source, YAML view).
- 2026-11-19: logged late: references/security.md Learned 2026-11-09, release digest before unpacking and disposable config for a CLI with a cloud default (two entries).
- 2026-11-19: write-back headers repaired to the ledger format (no words changed): languages/rust.md, references/design-patterns.md (6), design-principles.md, tooling-and-runtime.md.
## 20261119_1631 — Periodic review; 90-day review window

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19; references, Summaries and Scopes fixed, body rules aligned with their Learned entries. Review window now 90 days (`--window-days 90` in the justfile).

## 20261119_1601 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md

## 20261102_1347 — Learned: EXIT trap exit code, ruff through a symlink, tracker from records

`languages/shell.md`, `languages/python.md`, `references/design-patterns.md` P-49, from ansible-wifi (2026-11-02).

## 20261102_1132 — Learned: one write frame for many fields

`references/design-patterns.md` P-48, from ansible-wifi (2026-11-02).

## 20261101_2353 — Learned: guard first and dry-run a gate that hides records

`references/testing.md`, from skill-knowledge-curator (2026-11-01).
