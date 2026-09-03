# Scripts — skill-staleness-audit

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

The enforcement layer. **These are not optional helpers left to the agent's judgement** — the phases they implement produce receipts, and `verify_completeness.py` refuses to pass an audit whose
receipts are missing or do not reconcile.

## Contents

- [Why scripts and not prose](#why-scripts-and-not-prose)
- [Catalog](#catalog)
- [Task safety labels](#task-safety-labels)
- [Typical run](#typical-run)
- [What is deliberately NOT automated](#what-is-deliberately-not-automated)
- [Dependencies and portability](#dependencies-and-portability)

---

## Why scripts and not prose

A phase written as prose is advisory. Under time pressure the expensive ones — per-artifact reasoning, negative-testing — get skipped and the audit is reported complete, because **nothing can tell the
difference between "I did Phase 4" and "I said I did Phase 4"**.

Each phase therefore writes a receipt recording what was *measured* — file counts, claim counts, artifacts reasoned about, checks negative-tested. The gate does arithmetic on those receipts. A boolean
would just be another claim, and this skill exists because of claims nobody checked.

## Catalog

| Script | Phase | Purpose | Safety | Idempotent |
|---|---|---|---|---|
| `snapshot_worktree.sh` | 0 | Snapshot modified + untracked files before any edit. **Verifies its own output is non-empty** and exits 1 if not | `safe`, `modifies-files` (writes only to the snapshot dir) | yes — new dir per run |
| `audit_state.py` | all | Receipts and reconciliation. `init` / `record` / `note` / `status` / `require` / `reset` | `safe`, `modifies-files` (`.staleness-audit/` only) | yes |
| `coverage_manifest.py` | 1 | Classify every file: examined / exempt / out-of-scope. Names files a text sweep cannot open. **Fails when ≥5% is unclassified** | `safe`, read-only (`--record` writes state) | yes |
| `claim_scan.py` | 1, 7 | Enumerate checkable claims — counts, dates, paths, uniqueness — and verify what is mechanically verifiable | `safe`, read-only (`--record` writes state) | yes |
| `artifact_signals.py` | 4 | Per-artifact worksheet with signal flags. Its row count becomes the gate's denominator | `safe`, read-only (`--out` writes a worksheet) | yes |
| `inverse_sweep.py` | **Phase 7 — what exists that no catalog names.** Reports ORPHAN-DIR (a directory no catalog mentions), UNINDEXED-DIR (documents but no README where siblings have one) and DISPLACED (a README listing names that moved into its own subtree — resolves fine, sends the reader to the wrong place). Exit 1 on findings; `verify_completeness.py` blocks on it. Was prose until 2026-08-12, which is how a completed audit passed with three of these outstanding. | stdlib | safe (read-only; `--record` writes only the audit receipts) |
| `verify_completeness.py` | 7 | **The exit gate.** Receipts, reconciliation, coverage, old-value sweep, structured-config parse, duplicate keys, evidence byte-compare, optional project suite | `safe`, read-only | yes |

Exit codes are uniform: **0** ok · **1** attention required / gate failed · **2** usage or state error.

## Task safety labels

Per the estate convention, and none of these are `destructive`:

- `safe` — every script here. None deletes or overwrites project content.
- `modifies-files` — `snapshot_worktree.sh` (snapshot dir), `audit_state.py` (`.staleness-audit/`), and `--out`/`--record` flags. Nothing else writes.
- `read-only` — the default mode of the three scanners.

`.staleness-audit/` is working state, added to `.gitignore` on `init`. Delete it when the audit closes.

## Typical run

```bash
SKILL=/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-staleness-audit
cd <project>

# Phase 0 — ALWAYS FIRST
bash "$SKILL/scripts/snapshot_worktree.sh"
python3 "$SKILL/scripts/audit_state.py" init --scope "whole project"
python3 "$SKILL/scripts/audit_state.py" record --phase 0 \
    --key snapshot_path --value <path> --key files_snapshotted --value <n>

# Phase 1
python3 "$SKILL/scripts/coverage_manifest.py" --record
python3 "$SKILL/scripts/claim_scan.py" --record --count-map 'doc=docs/*.md'

# Phase 4
python3 "$SKILL/scripts/artifact_signals.py" --record --signal 2500 --signal RECOMMENDED \
    --out .staleness-audit/phase4-worksheet.md

# Phases 2, 3, 5, 6 — judgement. Record receipts as you complete them.
python3 "$SKILL/scripts/audit_state.py" record --phase 5 \
    --key checks_added --value 3 --key checks_negative_tested --value 3

# Phase 7 — the gate
python3 "$SKILL/scripts/verify_completeness.py" --old-value '$2,500 profit gate' --suite "just check"
```

Or use the bundled `justfile`: `just audit-start`, then `just audit-status` / `just audit-verify`.

## What is deliberately NOT automated

Automating these would mean pretending judgement had happened:

- **Phase 2 (fixing)** — dependency order depends on what the project's owners actually are.
- **Phase 3 (banners)** — "what in this file still stands" cannot be inferred.
- **Phase 4 (reasoning)** — the scripts flag *candidates*. Five of nine defect patterns have no string to match; a signal flag is a prioritisation hint, never a verdict.
- **Phase 5 (writing checks)** — a check must encode an invariant the project has actually stated. Manufacturing governance nobody agreed to is worse than leaving a gap.
- **Phase 6 (residual risk)** — knowing what you could not settle is the judgement.

`claim_scan.py` refuses to guess in the same spirit: without `--count-map` it reports counts as `NEEDS-MANUAL` rather than inventing a denominator. An earlier version guessed and produced 47
mismatches, nearly all false — **a scanner with a 50% false-positive rate is worse than none, because people stop reading the true positives too.**

## Dependencies and portability

**Python 3.9+ stdlib only.** PyYAML is used opportunistically by `verify_completeness.py` for duplicate-key detection; when absent the gate reports that check as **SKIPPED, not passed**.

`git` is used opportunistically for file listing and evidence comparison, with an `rglob` fallback. Without git, `snapshot_worktree.sh` exits 2 and tells you Phase 0 is mandatory by hand — because a
project with no version control is the one that most needs a snapshot.

Verified against four project shapes: a governance corpus, a financial-analysis repo, an Ansible/network repo (5,360 files) and a Python tooling repo (41,025 files). Unclassified rates: 0.0%, 0.0%,
1.0%, 0.0%.
