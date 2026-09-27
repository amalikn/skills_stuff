---
name: skill-staleness-audit
description: "Repo-wide audit for stale facts, superseded figures, checks that can't fail."
---

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

# skill-staleness-audit

## Contents

- [Use when](#use-when)
- [What makes this different](#what-makes-this-different)
- [The standard](#the-standard)
- [Phase 0 — Snapshot before touching anything](#phase-0--snapshot-before-touching-anything)
- [Phase 1 — Defect register, materiality-ranked](#phase-1--defect-register-materiality-ranked)
- [Phase 2 — Fix in dependency order](#phase-2--fix-in-dependency-order)
- [Phase 3 — Make supersession visible in-file](#phase-3--make-supersession-visible-in-file)
- [Phase 4 — Per-artifact reasoning](#phase-4--per-artifact-reasoning)
- [Phase 5 — Convert findings into checks that can fail](#phase-5--convert-findings-into-checks-that-can-fail)
- [Phase 6 — Residual-risk register](#phase-6--residual-risk-register)
- [Phase 7 — Completeness verification (the exit gate)](#phase-7--completeness-verification-the-exit-gate)
- [Phase 8 — Persist and close](#phase-8--persist-and-close)
- [Defect patterns worth grepping for first](#defect-patterns-worth-grepping-for-first)
- [Claim-versus-claim: the class this audit structurally misses](#claim-versus-claim-the-class-this-audit-structurally-misses)
- [Anti-patterns](#anti-patterns)
- [Tool hazards](#tool-hazards)
- [Skill package layout](#skill-package-layout)
- [Completion checklist](#completion-checklist)

---

## Use when

- Nothing specific has changed, but the project has accumulated history and may have drifted.
- Figures, thresholds, verdicts, statuses or prices are **restated across many surfaces**.
- The project keeps an append-only record, where old material keeps reading as current by design.
- Before anything with money, legal, safety or public exposure: a purchase, a filing, a deploy, a publication, a client deliverable.
- After a long run of sessions, when "the checks pass" has started to feel like evidence of correctness.

**Domain-independent.** This works on codebases, research corpora, financial models, network and infrastructure repos, business process documentation, and data/ML pipelines. The *phases* below never
change; only the **surfaces you inventory** do. **Read `patterns/domain-adapters.md` before Phase 1** — it maps the six underlying claim types onto each domain's real file types, names each domain's
characteristic silent-failure mode, and gives its one-sentence band-M test.

**Do not use** to propagate one known change — that is `skill-project-coherence`. Do not use to create governance from scratch — that is `skill-ai-it`. Do not use for a typo or cosmetic pass.

## What makes this different

`skill-project-coherence` starts from a known change and pushes it outward. **This skill starts from nothing and asks what has quietly stopped being true.**

That difference is the whole point, because the defects it finds are precisely the ones a coherence pass cannot see: **every document agreed with every other document about a wrong number.** A
consistency check validates that the copies match. It has nothing to say about whether the original was right, and a mature project will mistake one for the other unless something forces the question.

Worked example from the run this skill was extracted from: 592 governance checks passed continuously while two documents filed with a licensing authority stated a superseded profit gate, a class
verdict in the data layer still read `RECOMMENDED` after the prose had been reversed, and a max-auction-bid figure was solved against a floor the gate had outgrown.

## The standard

**"Would a careful reader be misled?"** — not "does the suite pass".

State this to the operator at the start and hold to it. The suite passing is the *null hypothesis* of this exercise, not its goal. If a green run were sufficient, there would be nothing to audit.

Where money, licences or legal exposure are involved, say so explicitly and raise the bar: **an unverified input is a defect even when the arithmetic on top of it is perfect.**

## Phase 0 — Snapshot before touching anything

Before the first edit — **run the script, do not hand-roll this**:

```bash
bash <skill>/scripts/snapshot_worktree.sh          # verifies its own output is non-empty
python3 <skill>/scripts/audit_state.py init --scope "whole project" --since last-audit
python3 <skill>/scripts/audit_state.py record --phase 0 \
    --key snapshot_path --value <path> --key files_snapshotted --value <n>
```

**`--since` is focus, not scope.** `last-audit` (the commit that added the newest `staleness-audit-*.md`) or any commit. The scanners then flag `CHANGED` files and list them first; coverage, claim
totals and the Phase 4 denominator stay whole-project, so a focused run still has to account for everything.

`audit_state.py` opens the receipt trail. **Every phase records what it measured, and the Phase 7 gate does arithmetic on those receipts** — so a skipped phase is detectable rather than a matter of
trust.

Three rules learned the hard way:

- **`git ls-files` is cwd-relative; `git status --porcelain` and `git diff --name-only` are repo-root-relative.** If the project is a subdirectory of its git repo, mixing them silently copies nothing
  and reports success. Verify the file count.
- **In a repo with a large uncommitted working tree, `git checkout --` is a destructive operation, not an undo.** Check what is uncommitted at that path first.
- **Before any programmatic edit to a governed JSON/YAML file, run a round-trip fidelity probe**: re-encode the parsed structure with the candidate settings and require byte-identity with the file
  *before* applying any change. A one-field edit that produces a 161-line diff means the encoder is wrong, not the file.

## Phase 1 — Defect register, materiality-ranked

Write the register to a scratch file before fixing anything. One row per finding:

| # | Materiality | File:line | Defect | Evidence |
|---|---|---|---|---|

**Materiality, in this order:**

- **M — could cost money or mislead a filing.** A gate, price, verdict, bid ceiling, or anything in a document sent to a third party.
- **H — enforcement hole.** A check that cannot fail, or a guard with a blind spot.
- **G — governance drift.** Stale counts, dates, indexes, routing.

**Rank before fixing.** Working in file order buries the expensive findings behind cosmetic ones, and the register is what lets you report honestly when you run out of time.

Every row cites evidence — a path, a line, a command output. A row that cannot cite is a suspicion, and belongs in Phase 6 instead.

### Coverage first, defects second

```bash
python3 <skill>/scripts/coverage_manifest.py --record        # every file classified
python3 <skill>/scripts/claim_scan.py --record \
        --count-map 'doc=docs/*.md'                          # every checkable claim
```

`coverage_manifest.py` **exits 1** when ≥5% of files are unclassified — a rule list that silently absorbs a third of a repo into "other" is claiming coverage it does not have. Extend its rules rather
than ignoring the exit code.

Before hunting anything, **classify every file under the audit root** into examined / exempt-with-reason / out-of-scope-stated, and reconcile the three counts against the total. Full class table,
including how to audit files a text sweep cannot open, is in `patterns/coverage-manifest.md`.

This ordering is not bureaucratic. A sweep that greps `*.md` and `*.py` will report clean while never opening the `.parquet` that every query reads, the `.xlsx` that *is* the financial model, or the
`.json` presets every tool loads — and **those are usually the most decision-relevant files in the project**. Binary and tabular files need provenance, schema and freshness-against-source questions
instead of pattern matching.

Governance, routing, decisions, knowledge base, process, code, task runners, config, tabular data, generated context, evidence, correspondence, locks, notebooks and IaC each have their own staleness
signature. Do not assume a class is clean because it is unfamiliar; assign it a verdict or an exemption, and say which in the report.

**Systems of record are in coverage too, though no file scan reaches them.** If the project writes prose into a live system — Nautobot descriptions and custom fields, a CMDB, a database, a ticketing
system — that prose goes stale like any document. For each such system, list the objects changed since the last audit (Nautobot: `?last_updated__gte=<date>` or the object-changes log) and read back
their free-text fields against current facts. Record it; the gate blocks without it, and `0` is an answer only after you asked:

```bash
python3 <skill>/scripts/audit_state.py record --phase 1 --key systems_of_record --value 1 \
    --key sor_objects_changed --value <n> --key sor_objects_read --value <n>    # read >= min(changed, 50)
```

Classifying live data as "RESIDUAL, not verifiable from inside the project" is the wrong answer when you can read it: residual is for what cannot be checked, not for what is not a file.

`claim_scan.py` reads the project's own `SIBLING_ROOTS`, `SIBLING_BRANCHES` and `CONDITIONAL_PATHS` from `scripts/check_governance.py` and splits unresolved paths into `ON-BOX` (a system path on a
managed host), `CONDITIONAL` ("when present", gitignored, or declared) and `BROKEN`, so the residual bucket says what it holds. Claims under a dated heading are marked historical automatically.

## Phase 2 — Fix in dependency order

Fix **upstream of the dependency arrows**, so nothing ever points at a fact that has not landed yet:

1. **The owner** — wherever the value is authoritatively defined. One place. If there is more than one, that is itself a finding.
2. **Implementations** — the code, config or formulas that enforce it. Keep every implementation at the same value in the same pass; two that disagree is worse than one that is wrong, because the
   disagreement is invisible until someone compares outputs.
3. **Documentation and narrative** — what humans read.
4. **Data and machine-readable surfaces** — YAML, JSON, registries, presets. This is the tier most often missed, because prose corrections *feel* like completion.
5. **Routing, indexes and navigation** — last among the sources.
6. **Derived artifacts** — regenerate after everything above, never before.

**Never let a routing or index file claim new truth before the thing it points at is updated.** The intermediate state is what a parallel session reads.

Regenerate every derived artifact at the end and confirm the diff contains only what you intended. A generated file whose *generator* still emits the old model is not fixed — it is fixed until the
next rebuild.

## Phase 3 — Make supersession visible in-file

The core defect class wherever a project keeps history: **the superseded document still reads like a live instruction.** A supersession recorded only in a spec, a change log or a routing table does
not reach the person — usually an agent — who opened the superseded file.

Each superseded section gets an in-place banner stating:

1. **What changed, when, and who owns the replacement.**
2. **What in this file still stands.** Without this, a banner reads as "ignore this document" and takes correct content down with the incorrect. Most superseded documents are mostly still right.
3. **A pointer, not a restatement**, wherever a threshold is involved — restating adds another surface to keep in sync.

Watch for chains that run **against** whatever ordering heuristic the project uses. If a document is superseded by a *rule* rather than by a higher-numbered document, "later wins" will never find it.
Register those explicitly and say so in the agent-facing guidance.

Full contract, placement rules and templates: `patterns/supersession-banners.md`.

**Templates that get copied are not history.** A stale gate in a copy-me-per-item template is a live operating instruction. Fix it at the point of use, and reconcile copies already taken.

## Phase 4 — Per-artifact reasoning

**A grep finds a stale string. It cannot find a stale assumption.** This phase is not discharged by Phase 1's greps, and collapsing it into them is the observed failure mode.

List every script, generator and data file. Write **one line each** on whether the change affects what it *computes, asserts, or prints*. Skipping an artifact is fine; skipping the question is not.

Three prompts that catch the class:

- Does it print or compute anything whose **meaning** changed, though its wording did not?
- Does it assume **continuity, completeness, or availability** that is no longer true?
- Does it **enumerate a live inventory** (an API list, a database, an inventory file) whose population changed since the last audit? Then its reach changed with no line of code changing. Name the
  population today and whether every member is meant — especially where it writes, installs or connects (`REACH?` in the worksheet).

**Code that did not change still gets all three.** A change in data is a change. The third prompt exists because a package-install script that walks every Nautobot Location went from four boxes to
thirteen when nine Locations were seeded, with its code byte-identical; nothing in the first two prompts pointed there.

The first two found both of the most expensive findings in the originating run, and neither had a string to search for: a max-bid back-solved against a floor the gate had outgrown, and a projection
whose verdict line encoded a superseded gate shape.

## Phase 5 — Convert findings into checks that can fail

A fix that is not enforced is a fix until the next session.

- **Derive, never author.** A count claim should be computed from the thing it counts. If a file says "56 checks", the checker reads the list length.
- **Negative-test in both directions, through the recorder.** Break the project deliberately, then run the check through `audit_state.py negtest red`; restore, then `negtest green`. The recorder runs
  the check itself and keeps an output excerpt and hash. Red must exit non-zero **and** print `--expect` (a failure-specific string); green must exit 0 **without** it. `checks_negative_tested` is
  derived from that evidence and cannot be typed:

  ```bash
  python3 <skill>/scripts/audit_state.py negtest red --check docs-indexed \
      --expect "FAIL check_docs_indexed" --cmd "python3 scripts/check_governance.py"
  python3 <skill>/scripts/audit_state.py negtest green --check docs-indexed     # reuses red's --cmd and --expect
  ```

A check that never fires breaks nothing and passes forever. On 2026-09-27 a negative test **passed while the project was broken**, and the typed count still claimed it.
- **Scan everything, not a hand-listed few.** A hand-maintained registry has the same drift problem as the claim it polices. Prefer a repo-wide scan with explicit, reasoned exemptions.
- **Guard every word order and every phrasing**, not the one you happened to write. A guard matching only the author's phrasing reports clean while the defect sits in the filed document.
- **Assert on the property that silence hides.** Byte-equality for immutable evidence; duplicate-key detection for YAML that parses fine but discards a block; provenance labels on inputs.
- **Exempt history by marker, never by rewriting it.** A dated record of what was true then is evidence. Rewriting it to satisfy a linter is the failure the exemption exists for.

## Phase 6 — Residual-risk register

Write, in the project's session-anchor file, what the audit did **not** resolve. A clean run must never be mistaken for a verified one.

Include: unverified inputs still in use; anything reconstructed rather than recovered, labelled as such **in the file itself**; parameters still unset; known structural limitations; and evidence that
is too thin to carry the weight placed on it.

**Own your own errors in the same register.** Mis-citations introduced during the audit, work destroyed and partially recovered, claims that turned out to be wrong. An audit that reports only other
people's mistakes is not an audit.

## Phase 7 — Completeness verification (the exit gate)

**Phases 0–6 find and fix. This phase proves nothing was left.** Without it the audit ends on an assertion, and assertions nobody checked are how the defects got there.

Enumerate every **checkable claim** — counts, dates, paths, thresholds, verdicts, derivations, provenance statements, capability claims, and uniqueness claims ("the only one that…", which falsify
silently when a second instance appears). Each ends in exactly one state, and the three must reconcile against the total:

| State | Meaning |
|---|---|
| **VERIFIED** | Checked against its source this run, with the check recorded |
| **MARKED-HISTORICAL** | A dated record of what was true then, exempted by marker |
| **RESIDUAL** | Not verifiable from inside the project; named in the residual-risk register |

Then run the **inverse sweep** — not "does the catalog name something that vanished" but "**does anything exist that no catalog names**". Only the second grows while you are not looking.

```bash
python3 <skill>/scripts/inverse_sweep.py --record      # ORPHAN-DIR / UNINDEXED-DIR / DISPLACED / EMPTY-INDEX / UNLISTED
```

An index that **exists but lists nothing** is the same defect as no index: `EMPTY-INDEX` and `UNLISTED` compare each folder's `readme.md` with the folder's contents. A folder index that describes
rather than lists declares it: `<!-- inverse-sweep:describes-only reason="..." -->`.

**This was prose until 2026-08-12 and nothing implemented it**, so a run in which the sweep never happened still reached GATE PASSED — three defects walked through that hole on a real project. It is
now a script, and `verify_completeness.py` blocks on it. `DISPLACED` is the state a permissive path resolver structurally cannot express: an index listing files by the bare names they carried before
they moved into a subdirectory. Every reference still resolves; every one of them sends a reader to the wrong place.

**The guarantee this earns, stated exactly:** every checkable claim is verified, marked historical, or listed as unverifiable. **It does not promise that a claim about the external world is true** — a
market price, a regulation, a vendor's terms cannot be settled by reading the project. There the guarantee is narrower and still worth having: every such claim carries its provenance and its as-at
date, so a reader knows what to re-check.

Say that distinction out loud in the report. **An audit claiming more than it can prove is itself the defect.**

**Write the report BEFORE the gate.** The gate deletes `.staleness-audit/` on PASS, and the defect register and Phase 4 worksheet in it are the audit's main evidence:

```bash
python3 <skill>/scripts/audit_report.py            # --out-dir <audit folder> the first time; later runs find it
# fill the narrative, index the report in its folder readme, then:
python3 <skill>/scripts/verify_completeness.py \
        --old-value '<superseded value>' --suite '<project check command>'
```

`audit_report.py` writes `staleness-audit-<YYYYMMDD_hhmm>.md` into the project's audit folder: the narrative skeleton plus a managed evidence block holding the receipts, every negative-test excerpt,
and each filled working file verbatim. Re-running it replaces only that block.

**On PASS the gate writes its result into the report, then removes the Phase 0 snapshots AND `.staleness-audit/`**; on FAIL it keeps them and names them. It **refuses to delete** — and fails — while
the report is missing, stale against the scratch, or still holds template placeholders. `--keep-snapshot` opts out of the snapshot deletion. Never copy the register out by hand instead: the gate
cannot tell a hand copy from a current one.

**This blocks.** It fails on a missing phase receipt **or a missing required key in one**, a coverage or claim matrix that does not reconcile, `artifacts_reasoned < artifacts_total`, negative-test
evidence short of `checks_added`, a system-of-record sample short of the changed objects, a surviving old value, a structured-config parse failure or duplicate key, modified evidence, a failing
project suite, or no current report. Anything it cannot run — PyYAML absent, git absent — it reports as **SKIPPED, not passed**.

Full method, claim taxonomy and exit criteria: `patterns/completeness-verification.md`.

## Phase 8 — Persist and close

The report already exists (Phase 7) and carries the gate's result. Append to the change log — never rewrite entries. Record the reasoning, not just the diff: *why* a defect survived is the reusable
part.

Persist to the project's memory backends, update the session-anchor file, regenerate generated context, and re-run full validation. Report the check count before and after; a rise is the audit's own
additions.

## Defect patterns worth grepping for first

Ordered by how often they have been the expensive one:

1. **A threshold restated across surfaces**, where one moved and the others did not.
2. **A verdict in prose that never reached the data layer** — YAML, JSON presets, generated tables.
3. **A superseded figure inside a template that gets copied.**
4. **A back-solve or ceiling computed against a floor that has since changed.**
5. **Counts and dates**: file counts, check counts, "last reviewed", snapshot dates.
6. **A machine-readable routing map with a misplaced key** — structurally valid, semantically wrong.
7. **Generated files whose generator still emits the old model**, including wrap/format governance.
8. **Immutable evidence silently reformatted** by a hook or formatter.
9. **Inputs with no provenance label**, especially ones feeding a headline figure.
10. **A protected or pinned block that contradicts current state** — `KEEP` blocks, "do not edit" regions, frozen sections. See below; this one is invisible to a ground-truth scan by construction.

## Claim-versus-claim: the class this audit structurally misses

Every check above compares a claim to **ground truth** — does this path exist, does this figure match the model, is this count right. A claim about *another document* has no ground truth to compare
against, so it lands in the manual-review bucket and quietly dies there.

**The 2026-08-12 case.** A `SCRATCHPAD.md` block marked `KEEP` asserted "skill-jdm is NOT ready — 3 of 6 deployment-gate conditions unmet" while the same project's `ROADMAP.md` carried a ticked
milestone recording it built **and** installed. It survived a full run of this audit and two runs of `skill-project-coherence`. Neither tool failed: coherence is instructed to treat `KEEP` as
protected, and this audit had nothing to check the assertion against.

**Two things follow, and both are cheap:**

- **`KEEP` and equivalent protected blocks are IN SCOPE.** `KEEP` means durable, not immutable. Never delete one — supersede it in place with a dated banner, the same treatment an append-only doc
  gets. A protection marker is not an exemption from being true.
- **Contradiction becomes mechanically decidable wherever the project has a completion surface.** A ROADMAP with `- [x]` milestones, a readiness command, a status table: any of these turns "X is
  unbuilt" from unverifiable prose into a checkable claim. Extract the identifiers from the *completion* side — they are usually marked up there — and look for them as plain text in the blocker
  assertion. Scanning the blocker side for backticked names finds nothing, because prose asserting a failure rarely bothers to format the name.

Where such a surface exists, write the check (Phase 5). Where none exists, say so in the residual-risk register (Phase 6) rather than reporting the area clean.

## Anti-patterns

- **Reporting a clean grep as a completed audit.** It proves the old strings are gone, nothing more.
- **Fixing the check instead of the project.** Broadening an ignore-list converts a real finding into a permanent blind spot.
- **Accepting "expected failures" as a steady state.** A validator that always fails is one nobody reads, and the next real failure goes unnoticed with it. Either fix the cause or make the exemption
  explicit and machine-honoured.
- **Deleting superseded reasoning.** Mark it; the reasoning is usually the useful part.
- **Trusting a tool's own report of what it did.** Verify against the artifact.
- **Running a destructive tool against the live tree to see what it does.** Copy the project and run it there — one `rsync` is the difference between finding out and losing the file.
- **Calling live data residual because it is not a file.** If you can read it, read it (Phase 1, systems of record).
- **Typing a count the tools derive.** `checks_negative_tested` comes from `negtest`; claim and coverage counts come from `--record`.

## Tool hazards

Both hit this skill's own runs on 2026-09-27; details in the markdown governance guide.

- **The markdown rewrap tool rebuilds any `## Contents` section as a table of contents.** Never put a folder index or file list under `## Contents`; use `## Index`. A list written there is erased.
- **An unquoted heredoc (`<<EOF`) runs every backticked word as a command.** Write markdown with `<<'EOF'`, or with the Write tool, and read the result back.

## Skill package layout

`SKILL.md` is the orchestrator. Depth lives in `patterns/`, boilerplate in `templates/`, and the two mechanical steps in `scripts/`. Load a pattern file when you reach the phase that needs it — do not
read the whole package up front.

```text
skill-staleness-audit/
├── SKILL.md                              # this file — phases, standard, anti-patterns
├── README.md                             # what it is, install, siblings, when NOT to use
├── CHANGELOG.md                          # version history and provenance
├── patterns/
│   ├── completeness-verification.md      # THE EXIT GATE — claim inventory, verification matrix, honest limits
│   ├── coverage-manifest.md              # every file classified — examined / exempt / out-of-scope, incl. binary + tabular
│   ├── domain-adapters.md                # the six claim types mapped onto code, research, finance, network, ops, ML
│   ├── defect-taxonomy.md                # the nine patterns: signature, detection, real instance, fix
│   ├── materiality-ranking.md            # M/H/G, and why ranking before fixing changes the outcome
│   ├── supersession-banners.md           # the in-place banner contract, chains that run backwards
│   ├── per-artifact-reasoning.md         # Phase 4 in full — what a grep structurally cannot find
│   ├── check-hardening.md                # writing a check that can fail; negative-testing protocol
│   └── evidence-integrity.md             # provenance labels, population matching, record counts
├── templates/
│   ├── defect-register.md                # Phase 1 register
│   ├── supersession-banner.md            # Phase 3 banner boilerplate
│   ├── residual-risk-register.md         # Phase 6 closing register
│   └── audit-report.md                   # final report shape
├── justfile                              # just audit-start / audit-status / audit-verify
└── scripts/                              # THE ENFORCEMENT LAYER — not optional helpers
    ├── README.md                         # catalog, deps, safety labels
    ├── snapshot_worktree.sh              # Phase 0 — snapshot, verifies its own output
    ├── audit_state.py                    # receipts + reconciliation across all phases
    ├── coverage_manifest.py              # Phase 1 — classify every file; fails on blind spots
    ├── claim_scan.py                     # Phase 1/7 — enumerate and verify checkable claims
    ├── artifact_signals.py               # Phase 4 — per-artifact worksheet + gate denominator
    ├── inverse_sweep.py                  # Phase 7 — what exists that no catalog or index names
    ├── audit_report.py                   # Phase 7 — the report, with the evidence embedded, before cleanup
    ├── verify_completeness.py            # Phase 7 — THE GATE; blocks on anything checkable
    └── tests/                            # fixture tests: python3 -m unittest discover -s scripts/tests
```

**Precedence.** Files in `patterns/` and `templates/` are the source; the summaries in this file are pointers. Where the two disagree, the pattern file wins and this file is stale — fix it.

**The scripts enforce; they do not replace judgement.** They make coverage, claim accounting and phase completion *mechanical*, so those cannot be skipped or asserted. Phases 2, 3, 5 and 6 are
deliberately not automated — dependency order, "what still stands", which invariant is worth a check, and what you could not settle are all judgement, and automating them would mean pretending
judgement had happened.

## Completion checklist

Work through every item explicitly; this is a blocking gate, not a post-hoc review.

- [ ] Snapshot taken **and its file count verified non-zero**
- [ ] **Coverage accounting reconciles** — examined + exempt + out-of-scope = total files; every exemption has a stated reason
- [ ] **Systems of record read back** — objects changed since the last audit, free-text fields compared with current facts; `systems_of_record` recorded even when 0
- [ ] Binary and tabular files (`.xlsx`, `.parquet`, `.csv`) audited by provenance/schema/freshness, not skipped for being ungreppable
- [ ] Defect register written, every row citing evidence, ranked by materiality
- [ ] Fixed in dependency order; no routing file claims truth ahead of its source
- [ ] Every superseded section carries an in-place banner naming what replaced it **and what still stands**
- [ ] Supersession chains that run against the ordering heuristic are registered explicitly
- [ ] Templates and already-taken copies reconciled
- [ ] **Every script, generator and data file reasoned about individually** — one line each, all three prompts, including "does it enumerate a live inventory whose population changed?"
- [ ] Generators checked, not just their output
- [ ] Each finding has a check that **was proven able to fail**, in both directions, recorded with `negtest red` then `negtest green`
- [ ] Counts derived from the thing counted, never authored
- [ ] History exempted by marker, never rewritten
- [ ] Derived artifacts regenerated; diffs are only what was intended
- [ ] Residual-risk register written, **including your own errors**
- [ ] Change log appended with the reasoning; both memory backends written; context pack rebuilt
- [ ] **Claim matrix reconciles** — verified + marked-historical + residual = total checkable claims
- [ ] **Inverse sweep clean** — `inverse_sweep.py` run and green: no orphan or unindexed directory, no displaced, empty or incomplete index
- [ ] **Report written before the gate** — `audit_report.py`, narrative filled, indexed in its folder readme
- [ ] Uniqueness claims ("the only one that…") re-enumerated and recounted
- [ ] The report states **what could not be verified from inside the project**
- [ ] Full validation run, check count reported before and after
- [ ] **Scratch cleared** — on PASS the gate writes its result into the report, then deletes both `.staleness-audit-snapshot-*` and `.staleness-audit/`. On FAIL it keeps and names them: a failed gate
  is exactly when the pre-audit state and the receipts are worth having. Leaving the receipts behind blocks the NEXT run, which refuses to start while a state file exists
