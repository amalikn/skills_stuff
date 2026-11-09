---
Title: skill-coder Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-coder pack — canonical, cross-project source of reusable programming practice
Last reviewed: 2026-10-19
Summary: >-
  Agent guidance for maintaining and using skill-coder: artifact roles, the runtime rule for its helpers, the code map, the write-back obligation
  and the gates to run before calling work complete.
---

@../../../AGENTS.md

# AGENTS.md

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## AI navigation and context preflight

Before answering, planning or editing, read [AI_NAVIGATION.md](AI_NAVIGATION.md) first: it routes everything else (read order, source priority, task routing, scripts, checks, compaction recovery).
Read [context-map.yaml](context-map.yaml) only when changing routing or companion files.

- Sources disagree: stop and report, never guess. `SCRATCHPAD.md` is not durable truth unless marked `KEEP`; generated output never is.
- Run catalogued tasks only (`just --list`, `scripts/README.md`); an uncatalogued script is unknown safety. A new or changed script updates `scripts/README.md`.
- Before calling work done: `just check` (fix the project, not the check), and a `CHANGELOG.md` entry for any governance or navigation change.
- Preserve user content outside managed blocks.

<!-- END MANAGED: skill-ai-it:navigation -->

## Contents

- [Working rules](#working-rules)
- [Runtime rule for the helpers](#runtime-rule-for-the-helpers)
- [Package contract](#package-contract)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)

---

## Working rules

- [SKILL.md](SKILL.md) is the activation surface and must route every file in `references/` and `languages/`; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors it.
- Core rules in `references/` are language-agnostic. A language file may tighten a rule, loosen it only with a stated reason, or map it to that
  language's tools. A project's own rules (its `AGENTS.md`, code design, `code-map.toml`) outrank both; say so when they differ.
- Every rule says why in one clause and cites its source in [sources.yaml](sources.yaml): operator rules as `USER_STATED`, external facts with a
  primary source and retrieval date. Unverified material is labelled `UNVERIFIED`, never stated as fact.
- No customer names, hostnames, private addresses, tokens or production domains in pack files; a governed project is named only as a rule's source.
- `scripts/` holds stdlib-only helpers with tests in `tests/test_helpers.py`; a new helper is catalogued in [scripts/README.md](scripts/README.md)
  and gets a recipe in the same pass. The pack is held to its own rules by `just self-check` (inside `just check`).
- The package version lives only in the [CHANGELOG.md](CHANGELOG.md) release heading.
- Research sources go verbatim under `documents/` with a `readme.md` index; downloads never go to `/tmp` or a scratchpad.
- Triage before opening: `just docs <folder>`; run `just stale` before editing; old records via `just history <term>`. <!-- path:example -->

## Runtime rule for the helpers

Operator, 2026-10-19 (assessed against the alternative of a separate skill runtime): the logic is applied inside the target project's own
environment with that project's own tooling. The helpers are stdlib-only, declare `REQUIRES_PYTHON = (3, 11)`, read code as files, and run with
the project's pinned interpreter by path. Only when a project has no Python 3.11+ does an agent run them through this pack's recipes
(`just -f <pack>/justfile <recipe> --project-root <project>`), which is safe because they only read. Nothing is ever installed into a project for
the pack's sake. `just test-matrix` proves the helpers on every installed Python from 3.11.

## Package contract

`tests/test_package_contract.py` is the pack's executable contract: every reference and language file is routed from `SKILL.md`; claims follow the
ledger schema; every Learned or Disputed entry has a CHANGELOG line naming the file and date; every helper is tested, stdlib-only, declares
`REQUIRES_PYTHON` and parses at that grammar; every function and class has an `Args:`/`Returns:` docstring; no unsafe text anywhere. Run
`just test` and `just check` before claiming any change complete.

## Cross-project write-back trigger

Any project that invokes this skill and learns reusable programming practice writes it back here before the session closes: a dated Learned entry
in the focused reference (or language file) plus one CHANGELOG line under `## Unreleased`, read back after writing (format in
`references/evolution-and-write-back.md`). If this source is not writable from the engaging task, leave the entry in the engaging project as a
candidate under `## skill-coder write-back candidates`, where `scripts/write_back.py` finds it for the next engagement to promote. A project-specific
rule stays in that project. The calling session owes this whether or not its project routes to this skill; skill-slurp-chat Step 5b rechecks it
(`references/evolution-and-write-back.md`, "Projects that call this skill").

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions and `<RUNNER CHECK COMMAND>` gates on them. It is stdlib-only
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

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- skill-ai-it (bootstrap source): [/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
