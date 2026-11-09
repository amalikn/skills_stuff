@../../AGENTS.md

Title: skill-eval-manager Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: Repo-local agent behaviour for the skill-eval-manager package under skills_stuff/skills/
Last reviewed: 20260923_1222
Summary: Local policy for authoring, validating, and recording against the eval-management skill package.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)
- [Code changes](#code-changes)

---

This directory is the canonical source for the `skill-eval-manager` package. It is a **skill package**, not a consuming project: the evals it talks about live in other repositories. What lives here is
the method, the portable data contracts, the recordkeeping scripts, and the worked examples that prove those contracts still work.

## Working rules

- Treat [SKILL.md](SKILL.md) as the operational entry point and [references/](references/) as the method. Change the method in `references/`, not in prose scattered across other files.
- The package executes nothing. Do not add a scheduler, runner, retry policy, executor plugin system, or assertion DSL — that boundary is stated in [SKILL.md](SKILL.md) and is the reason the package
  is small.
- Keep the shipped scripts **stdlib-only**. `PyYAML` is an optional convenience for ordinary YAML, never a requirement; the template and examples are JSON-formatted YAML and must stay loadable without
  it.
- `examples/*/history.jsonl` is append-only. Correct a record by superseding it, never by editing or deleting a line.
- `examples/*/report.md` is **derived**. Never hand-edit one; regenerate it with `scripts/render_report.py` whenever its suite or history changes. `just check` fails when a report is older than its
  inputs.
- Fixtures under [examples/validation-failures/](examples/validation-failures/) are deliberately invalid and must keep failing validation. `just validate-negatives` asserts this; a fixture that starts
  passing is a validator regression, not a fixture to fix.
- When adding a validator rule, demonstrate a deliberate failure case before calling it done. This is stated in the [SKILL.md](SKILL.md) quality gate and applies to this repo's own scripts too.
- The package version is stated in four places — `SKILL.md` frontmatter, `README.md`, the top [CHANGELOG.md](CHANGELOG.md) heading, and the `package-version` pattern in
  `CONSTANT_SURFACES` in [scripts/check_governance.py](scripts/check_governance.py). A bump touches all four in one pass; `just check` fails on the first three until the fourth is
  bumped, and says only that a surface "no longer states it". Do not write the live version into any other file, `SCRATCHPAD.md` history included — the sync check rejects it.
- Time-bound documents use `<slug>-YYYYMMDD_hhmm.md`. Stable entrypoints keep their exact names.
- Install to client runtimes by **symlink**, never by copy — see [README.md](README.md). A copied skill drifts silently across the three agents.
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries live in `docs/history/`; do not read them by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one.

## Cross-project write-back trigger

Any project that invokes this skill and learns something about **evaluation method** — a validator gap, a falsifiability method the permitted six could not cover, a verdict the closed five could not
express honestly, an oracle that looked independent and was not, a layer vocabulary that generalizes — must write it back here before the session closes. This is the [SKILL.md](SKILL.md) standing
write-back contract in enforceable form. Concretely: `skill-slurp-chat` and `project-coherence`, run in any project that wrote or maintained an eval suite this session, must check for unpromoted
method knowledge before closing out. If either closes a session without this check, treat the closeout as incomplete.

**Closeout self-check:** did this session (a) find a suite that `scripts/validate_suite.py` judged wrongly in either direction, (b) need a falsifiability method, verdict, or contract element the
closed sets do not carry, or (c) hit a recordkeeping case the append-only/supersede/derive model handled badly? If any is yes, write it to the matching `references/` file in the same pass rather than
deferring it, and route a closed-set change through the owning `.archcore/` rule or spec.

**Then record the routing in [ledger.jsonl](ledger.jsonl) with `scripts/record_writeback.py`, or state why no row was needed.** The self-check above is three yes/no questions and names
no artifact, which is how the first write-back session answered them honestly and still left a finding in memory instead of in `references/` — the package shipped a fix and a regression
fixture, and the method knowledge behind them reached nobody who cloned the repo. A row is not a substitute for incorporating: `scripts/record_writeback.py` refuses a destination that does not exist,
and `just check` fails when a recorded destination later stops existing. A finding with nowhere to go yet is recorded `--open` and reported until it does.

**Lessons this package learns about itself do not go in the ledger, and do not stay in memory.** A tooling quirk, a surface a bump missed, a gate that misfired: write it in the
same session into the file that would have prevented it — usually a working rule above, a `references/` file, a script docstring, or a schema `description`. The ledger stays
reserved for consuming-project findings so its open rows remain few and each one means something. Memory backends are a capture cache that nothing obliges anyone to read; a lesson
recorded only there is lost. A lesson that belongs to another repository gets a tracked item in that repository before the session closes, not a note here.

**This pack's checker cannot see into another project.** `scripts/check_governance.py` verifies that every `references/*.md` file is routed from `SKILL.md`, which catches a reference added here and
left unrouted. It cannot detect knowledge that never left the consuming project — nothing will flag that gap from this side, which is why the trigger is a standing obligation rather than a check.

**What stays in the consuming project:** the suite itself, its thresholds, executor wiring, schedule, and results. Pulling those in would make this a platform, which
[.archcore/adr/skill-not-platform.adr.md](.archcore/adr/skill-not-platform.adr.md) rules out. The boundary is the point of the trigger, not an exception to it.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-07-snake-case-recipes-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile`
    exists.
12. Treat uncataloged scripts as `unknown` safety until inspected.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. Run defined audit/check commands before completing work. Where `scripts/check_governance.py` exists, that includes it — and when it fails, fix the project, not the check.
    Adding a new artifact class, generated output, or a constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions and `just check` gates on them. It is stdlib-only
and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file. It is cheap and it is the only thing standing between this project's
documents and silent decay.

### The checker grows with the project

The check count is a coverage signal, not a score. It is expected to rise as the project acquires structure. Extend it on these triggers:

| Change made | Required checker update |
|---|---|
| Add a document to a cataloged folder | None — the coverage check fails until the index links it. That is the intended workflow, not an error to route around |
| Add a script or task | Catalog it in `scripts/README.md` and the task runner; coverage fails until then |
| Add a new **class** of artifact (new folder, new document type) | Add a `CATALOGS` entry, plus a contract check if the class has a declared filename or frontmatter form |
| Add a generated artifact | Add a `DERIVED` entry; add a provenance check too if the generator can stamp its source into the output |
| State a threshold, rate, deadline, or canonical path in a new file | Register the file in `CONSTANT_SURFACES`; the sync check fails until it is registered |
| Change a constant's value | Update the owning rule first, then every registered surface, in one pass — the sync check verifies the pass was complete |
| Rename or move a file | Nothing — path resolution catches every stale reference automatically |
| Retire a check | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from one that never existed |

### Rules that are not negotiable

- **When a check fails, fix the project, not the check.** Broadening an ignore-list to silence a true positive, or exempting the file that failed, converts a real finding into a permanent blind spot
  that the next agent has no way to discover.
- **A new check must be able to fail.** Prove it by breaking the project deliberately and watching it go red. A check that scans an empty set is an assumption wearing a test's clothes.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the surrounding logic implements it — a script's output can state a rule its code no longer applies.
  Where a check must verify behavior, execute the behavior and assert on the result.
- **Do not enforce history.** Counts and states recorded as past facts are evidence, not live claims. Mark those lines `<!-- count:asat -->` rather than editing the record to satisfy the checker.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent repo policy: [../../AGENTS.md](../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime) and the session owes it a write-back.
