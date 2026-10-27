---
Title: skill-drawio Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-drawio pack — canonical, cross-project source of draw.io practice and the data-first diagram engine
Last reviewed: 2026-10-19
Summary: >-
  Agent guidance for maintaining and using skill-drawio: artifact roles, the engine's consumers and the byte-identity rule, the write-back obligation
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
- [Engine consumers and the byte-identity rule](#engine-consumers-and-the-byte-identity-rule)
- [Package contract](#package-contract)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)

---

## Working rules

- [SKILL.md](SKILL.md) is the activation surface and must route every file in `references/`; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors it.
- Code follows skill-coder (`/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-coder/SKILL.md`): modules under 400 lines and functions
  under 60, Args/Returns/Raises docstrings, stdlib only with PyYAML imported at the edge, `REQUIRES_PYTHON`, a timeout on every subprocess, `--write`
  or `--apply` on every write. `just self-check` (inside `just check`) runs skill-coder's helpers on this pack against [code-map.toml](code-map.toml).
- Runnable front ends sit at the top of `scripts/`; the library is the `drawio` and `flowmap` packages (skill-coder, "Grouping modules into packages").
  Every module is catalogued in [scripts/README.md](scripts/README.md) and every front end has a recipe.
- Every rule says why and cites its source in [sources.yaml](sources.yaml); draw.io behaviour names the version it was seen on
  ([compatibility.yaml](compatibility.yaml)). Unverified material is labelled `UNVERIFIED`.
- No customer names, hostnames, private addresses or tokens in pack files; a governed project is named only as a rule's source.
- Every layout audit has a test that feeds it a bad drawing and sees it fail. The example map ([examples/shop/parts/master.yaml](examples/shop/parts/master.yaml)
  and its parts; `flows.yaml` is assembled from them) must assemble, render, stay current (`just example-check`, in `just check`) and pass every audit.
- The package version lives only in the [CHANGELOG.md](CHANGELOG.md) release heading.
- Research sources go verbatim under `documents/` with a `readme.md` index; downloads never go to `/tmp` or a scratchpad.
- Triage before opening: `just docs <folder>`; run `just stale` before editing; old records via `just history <term>`. <!-- path:example -->

## Engine consumers and the byte-identity rule

unified-network-controller renders its flow map with this pack's `render_flowmap.py` (its profile is the `drawing:` block in its
`docs/flows/flows.yaml`; no project wrapper since 2026-10-19), and its as-built reader re-exports `drawio.read`. A change
to `scripts/drawio/` or `scripts/flowmap/` that is meant to change nothing must leave every consumer's drawing byte-identical: render before and
after, compare with `cmp`, and run the consumer's `just test` and `just check`. A change that does alter drawings is a release with a CHANGELOG
entry, rendered samples reviewed by the operator, and each consumer re-rendered in the same pass.

## Package contract

`tests/test_package_contract.py` is the pack's executable contract: every reference is routed from `SKILL.md`; claims follow the ledger schema; every
Learned or Disputed entry has a CHANGELOG line; every module is catalogued, stdlib-only at import, declares `REQUIRES_PYTHON` when runnable and parses
at that grammar. `tests/test_helpers.py` tests the engine and every audit's ability to fail. Run `just test` and `just check` before claiming any
change complete.

## Cross-project write-back trigger

Any session, in any project, that drew, rendered, exported or read a draw.io file writes what it learned back here before closing: a dated Learned
entry in the focused reference plus one CHANGELOG line under `## Unreleased`, read back and committed (format in
`references/evolution-and-write-back.md`). If this source is not writable, the entry waits in the project under
`## skill-drawio write-back candidates`, where skill-coder's `scripts/write_back.py --skill skill-drawio` finds it. A project's own drawing facts stay
in that project.

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
