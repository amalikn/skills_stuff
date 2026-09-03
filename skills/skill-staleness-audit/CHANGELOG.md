# Changelog — skill-staleness-audit

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

## Contents

- [20260812_1400 — v1.0, initial release](#20260812_1400-v10-initial-release)
- [2026-08-12 — the inverse sweep was prose, and a run skipped it while the gate said PASSED](#2026-08-12-the-inverse-sweep-was-prose-and-a-run-skipped-it-while-the-gate-said-passed)
- [2026-08-12 (later) — snapshots were never cleaned up, and accumulated invisibly](#2026-08-12-later-snapshots-were-never-cleaned-up-and-accumulated-invisibly)
- [2026-08-12 (later still) — path claims inside source docstrings were never checked](#2026-08-12-later-still-path-claims-inside-source-docstrings-were-never-checked)

---

## 20260812_1400 — v1.0, initial release

### Added

- **`SKILL.md`** — nine phases (0–8), the standard (*"would a careful reader be misled?"*, not "does the suite pass"), the nine defect patterns, anti-patterns, and a completion checklist.
- **`patterns/`** — eight reference files: `defect-taxonomy`, `materiality-ranking`, `supersession-banners`, `per-artifact-reasoning`, `check-hardening`, `evidence-integrity`, `domain-adapters`,
  `coverage-manifest`, `completeness-verification`.
- **`templates/`** — defect register, supersession banners (seven forms), residual-risk register, audit report.
- **`scripts/`** — the enforcement layer: `snapshot_worktree.sh`, `audit_state.py`, `coverage_manifest.py`, `claim_scan.py`, `artifact_signals.py`, `verify_completeness.py`, plus a `justfile`.

### Design decisions worth recording

- **Scripts enforce, prose advises.** Phases written only as prose get skipped under time pressure and the audit is reported complete, because nothing can distinguish *"I did Phase 4"* from *"I said I
  did Phase 4"*. Each phase now writes a **receipt recording what it measured**, and `verify_completeness.py` does arithmetic on those receipts. A boolean would just be another claim.
- **Phases 2, 3, 5 and 6 are deliberately NOT automated.** Dependency order, "what in this file still stands", which invariant deserves a check, and what could not be settled are judgement. Automating
  them would mean pretending judgement had happened.
- **The exit gate states its own limits.** It reports anything it could not run — PyYAML absent, git absent — as **SKIPPED, not passed**, and prints explicitly that a passing gate does not establish
  that any claim about the external world is still true. An audit claiming more than it can prove is itself the defect.
- **`claim_scan.py` refuses to guess.** Without `--count-map` it reports counts as `NEEDS-MANUAL` rather than inventing a denominator.

### Built by testing against four project shapes, not one

Everything below was a real defect **in this skill's own scripts**, found by running them outside the project they were extracted from. Each is why a rule exists.

| Found | Fix |
|---|---|
| 19 immutable dated register captures classified as "config to parse" | Dated-stem regex — a timestamp in the **filename** is the general signal for a capture, and it survives any project's directory names |
| **120 false `BROKEN` path claims** — bare filenames in prose (`purchase-discipline.rule.md`) resolved only root- and sibling-relative | Repo-wide bare-filename resolution, plus `docs/NN` shorthand |
| **47 false `MISMATCH` counts** — "the three gate scripts" counted against `scripts/*.py` | Stop guessing project semantics; require `--count-map` to enable verification |
| Placeholder patterns (`<slug>-YYYYMMDD_hhmm.md`) treated as broken paths | Placeholder regex — those are naming conventions, not references |
| 29% of a financial repo and 19% of an Ansible repo landing in unclassified "other" | Added vendored trees, `node-compile-cache`, `.eml`/`.docx`/`.duckdb`, `.j2` templates, key material, licences, compressed bundles — **and made ≥5% unclassified exit 1**, because a rule list that silently absorbs a third of a repo is claiming coverage it does not have |
| `--json` output corrupted by a prose block appended after the JSON | Guarded on `--json`; machine output stays machine-readable |

Final unclassified rates: **0.0%** governance corpus · **0.0%** financial analysis (932 files) · **1.0%** Ansible/network (5,360 files) · **0.0%** Python tooling (41,025 files).

`.j2` templates earned their own class after the Ansible run: in infrastructure projects a renamed template variable still renders, still exits 0, and quietly produces the wrong config — the domain's
characteristic silent failure.

### Negative-tested

Per the skill's own rule that a check must be **proven able to fail**:

- Gate on an unstarted audit → 8 failures, one per missing phase receipt. ✓
- `artifacts_reasoned` 9 of 22 → caught. ✓
- `checks_negative_tested` 1 of 3 → caught. ✓
- Claim matrix summing to 1,162 against a stated 1,318 → caught. ✓
- All receipts reconciling → **GATE PASSED**, exit 0, with the external-world limitation printed. ✓

### Provenance

Extracted from a full-day audit of a vehicle-import project, August 2026, where the operator's standard was *thousands of dollars ride on these documents*. That run found two licence-application
documents stating a superseded profit gate, a class verdict never propagated from prose to the data layer, and a maximum-auction-bid figure solved against a floor the gate had outgrown — all while
**592 governance checks passed continuously**.

Several rules trace to mistakes made by the auditing agent rather than found in the project: a destructive `git checkout`, a systematic mis-citation, a warning that read the wrong cell and therefore
never fired, and a confidently-documented protection mechanism that did not exist. Those are in here deliberately — a skill written only from other people's mistakes would be missing half the failure
modes.

## 2026-08-12 — the inverse sweep was prose, and a run skipped it while the gate said PASSED

Found by the operator asking, of three defects a completed audit had missed: *why did the skill not pick it up?*

**Root cause: Phase 7's inverse sweep was the only mechanical step left as prose.** Every other part of the gate — receipts, coverage reconciliation, old-value hits, structured-config parsing, the
project suite — was enforced by `verify_completeness.py`. The sweep was an instruction in SKILL.md. So it was the step that got skipped, the gate reported PASSED, and three defects survived:

1. **ORPHAN-DIR** — a new top-level directory holding the project's most decision-relevant artefact never appeared in the repo README. Nothing compared the tree against any catalog.
2. **UNINDEXED-DIR** — three new subdirectories had no README while every sibling had one. "A directory has an index" is a structural property, not a claim, so the claim taxonomy could not see it.
3. **DISPLACED** — an index still listed its files by the bare names they carried before they moved into a subdirectory. **Every one of those references still resolved**, because `resolve_path()`
   searches bare filenames repo-wide. That permissiveness is correct and deliberate — requiring a directory produced 120 false positives on a real project — but it means a moved file never breaks its
   own index. The reference is not broken; it sends a reader to the wrong place.

### Added

- **`scripts/inverse_sweep.py`** — reports ORPHAN-DIR, UNINDEXED-DIR and DISPLACED; exit 1 on findings.
  - `UNINDEXED-DIR` fires only where a **sibling** directory has a README, so it reports an inconsistency with the project's own convention rather than imposing one.
  - `DISPLACED` is scoped hard to **a README citing a name that now lives in its own subtree**. The first version flagged every bare-name reference that resolved elsewhere and produced 52 findings,
    almost all prose — a CHANGELOG citing `cell_map.py`. **A check that reintroduces the false positives its own resolver was loosened to avoid is worse than no check, because it gets muted.**
  - Skipping is prefix-aware: the first run reported the audit's own `.staleness-audit-snapshot-<stamp>` directory back to itself.
- **`verify_completeness.py` now blocks on it**, and prints `inverse sweep : N item(s)` or `NOT RUN`. Absent script is reported SKIPPED, never passed.
- SKILL.md Phase 7 names the script; the completion checklist item now requires it green rather than asserting it.

### Negative-tested

Synthetic tree with one orphan directory, two unindexed directories and one displaced index entry: all three detectors fired, the gate blocked with `GATE FAILED`, and the real project went from 5
findings to clean once fixed.

### The lesson worth carrying

**A gate that enforces its easy checks and trusts its hard one is not a gate** — and the skill's own anti-pattern list already said "trusting a tool's own report of what it did". It had not been
applied to the tool itself.

## 2026-08-12 (later) — snapshots were never cleaned up, and accumulated invisibly

Found by the operator: *"previous audit folder was not deleted"*.

`snapshot_worktree.sh` copies the entire worktree before the audit touches anything — correct, and the safety net for a run that goes wrong. **Nothing ever removed them.** They are gitignored, so they
accumulate silently: a project audited three times carries three full copies of itself, every subsequent `rglob` walks all of them, and on the run that exposed this two had already piled up and were
being reported back to the repo's own scanners as unregistered gate surfaces until the skip lists were patched.

### Added

- **`cleanup_snapshots()` in `verify_completeness.py`**, called from the gate.
  - **Deletes on PASS only.** A FAILED gate is exactly when the pre-audit state is worth having — deleting it on failure removes the evidence at the moment it becomes useful. On failure the gate now
    prints which snapshots it kept, and why.
  - `--keep-snapshot` opts out of deletion entirely.
  - Scoped to the literal `.staleness-audit-snapshot-*` prefix the skill creates, refuses anything that is not a directory, and never touches `.staleness-audit/`, which holds the receipts.

Verified on a real project: two accumulated snapshots removed on PASS; on the preceding FAILED run of the same gate both were listed as kept.

**The receipts directory goes too, and leaving it was a bug rather than caution.** `.staleness-audit/state.json` is per-run scratch — it exists so the Phase 7 gate can do arithmetic on what each phase
measured, and once the gate has passed and the run is in the project's change log it has served its whole purpose. Leaving it behind **breaks the next run**: `audit_state.py init` refuses to start
while a previous state file exists, so the second audit of the same project failed with *"audit already in progress"* and had to be forced. Scratch that blocks the next run is not a safety net. The
`.gitignore` entries stay, because they are correct for the run after this one.

## 2026-08-12 (later still) — path claims inside source docstrings were never checked

A second audit round of the same project found a broken path citation **inside `check_governance.py`'s own docstring** — it named the wrong spec filename it exists to catch, as the example, and the
backticks made prose read as a live path claim.

The generalisable point is not the citation. It is that the project's checker scanned `*.md` only, while its scripts carry their reasoning in docstrings that cite authorities by path with exactly the
same failure mode. **Measure the noise cost before widening**: the sweep found precisely one pre-existing item across every script, so extending coverage was free. It would not always be.
