---
Title: skill-vagrant Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-vagrant platform pack — canonical, cross-project source of reusable Vagrant and Parallels lab knowledge
Last reviewed: 20261107_1700
Summary: "Agent guidance for maintaining and using skill-vagrant: artifact roles, the package contract, the write-back obligation, the boundary with skill-proxmox, and the gates to run before"
Budget: 150 lines, 12 KB
---

@../../../AGENTS.md

calling work complete.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Package contract](#package-contract)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)
- [Code changes](#code-changes)

---

## Working rules

- [SKILL.md](SKILL.md) is the agent-facing activation surface: role, boundaries, orient-first commands, task routing and the standing write-back contract. It must route every file in `references/`.
- `references/` is the content source. Load only the reference the task needs; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors the routing table.
- Scope: local lab VMs on macOS Apple silicon with Vagrant and the Parallels provider (boxes, Vagrantfiles, networks, clones, prlctl, lab guards, licensing). Not Proxmox or OpenTofu — that is
  [skill-proxmox](../skill-proxmox/SKILL.md) — and not what runs inside the guest. Choose the primary pack by the object being changed.
- Evidence discipline: every load-bearing claim lives in [sources.yaml](sources.yaml) with an evidence rung, source type, reference and scenario; environment facts live in
  [compatibility.yaml](compatibility.yaml). An observed install is not behavioural proof. Versions of record: Vagrant 2.4.9, vagrant-parallels 2.4.9, prlctl 27.1.0 (see `compatibility.yaml`).
- `documents/research-sources-<YYYYMMDD>/` holds verbatim captures with a provenance header; adding or replacing one requires a row with its sha256 in that folder's `readme.md`.
- `scripts/` holds tested, stdlib-only, read-only helpers. A new helper needs tests in `tests/test_helpers.py` and an entry in [scripts/README.md](scripts/README.md) in the same pass; one that
  changes a VM needs a plan by default, `--apply`, a fixed lab VM name and a deadline on every call.
- Lab safety: from this pack, run read-only `vagrant` and `prlctl` commands only (status, list, box list, global-status, capture). Starting, stopping, resetting, cloning, snapshotting or
  destroying a VM is the engaging project's write, behind its own gate.
- Never write a credential, private address, production domain or box registry token into an authored pack file — the contract test scans every authored `.md`/`.yaml`/`.txt` file. Verbatim
  captures keep the publishers' example addresses and are checked only for keys and live credentials.
- Durable decisions, rules and plans live in `.archcore/`, indexed by [.archcore/index.guide.md](.archcore/index.guide.md); they outrank this file's prose where they differ.
- memory-keeper channel for this pack is exactly `vagrant`.
- The package version lives only in the [CHANGELOG.md](CHANGELOG.md) release heading. Do not restate it in other governance files.
- Time-bound notes use `<slug>-YYYYMMDD_hhmm.md`. <!-- path:example -->
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries are not read by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one. Rotation
  (`just rotate --apply`) creates their folder, `docs/history/`, the first time either record passes its budget. <!-- path:example -->

## Package contract

`tests/test_package_contract.py` is the pack's own executable contract and outranks generic skill-ai-it conventions where they differ:

| Rule | Consequence |
|---|---|
| A manifest JSON file, a RUNBOOK file, an agents directory and any `Vagrantfile` are forbidden | Lab Vagrantfiles live in `vagrant_stuff` and their projects, never here |
| Every required reference is named in `SKILL.md` | Routing changes start in `SKILL.md` |
| Claims and environments follow a fixed schema and evidence ladder | Edit `sources.yaml`/`compatibility.yaml` only in schema |
| Every research capture is indexed with its sha256 and carries a provenance header | Re-fetching a page means a new row and hash |
| Every Learned/Disputed entry in a reference has a CHANGELOG line naming the file and date | Write-back is two edits, always |
| Every helper in `scripts/` is tested, stdlib-only, and passes a timeout to every subprocess or URL call | Includes `scripts/check_governance.py`, tested by running it |
| No unsafe text in authored files | Applies to generated `.ai-context/` too — regenerate, then re-run `just test` |

Run `just test` (contract + helpers + governance checker) before claiming any change complete.

## Cross-project write-back trigger

Any project that invokes this skill and learns reusable Vagrant, Parallels or lab-tooling knowledge writes it back here before the session closes, per the `SKILL.md` standing write-back
contract and [references/evolution-and-write-back.md](references/evolution-and-write-back.md): a dated Learned entry in the focused reference plus one CHANGELOG line under `## Unreleased`, read
back after writing. If this source is not writable from the engaging task, leave the entry in the engaging project as a candidate.

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

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions and ``just check`` gates on them. It is stdlib-only
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

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Counterpart pack: [../skill-proxmox/SKILL.md](../skill-proxmox/SKILL.md)
- Model pack this one mirrors: [../skill-nautobot/SKILL.md](../skill-nautobot/SKILL.md)
- skill-ai-it (bootstrap source): [/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime, two-space indentation for new files) and the session owes it a write-back.
