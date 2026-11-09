@../../../AGENTS.md

Title: skill-cambium Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-cambium specialist pack — canonical source for Cambium device-fleet operational knowledge
Last reviewed: 20260917
Summary: Agent guidance for maintaining and using the skill-cambium specialist pack. Covers specialist structure, reference routing, cross-pack boundary with skill-smc, and update discipline.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Project-coherence checklist](#project-coherence-checklist)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)
- [Code changes](#code-changes)

---

## Working rules

- `SKILL.md` is the agent-facing activation surface — it defines triggers, the Standing Write-Back Contract, and pointers to `references/`.
- `RUNBOOK.md` is the navigation index — it maps task types to specific numbered reference files. Do not use it as a content source.
- The 6 numbered files under `references/` (from `references/01_overview.md` to `references/06_device-api-cli-reference.md`) are the content source. Load only the one needed for the task.
- `manifest.json` is the machine-readable specialist metadata. Update `version` and `updated_at` when any content file changes.
- Never write a device password or other secret value into any file in this pack — reference convention is `<secret:keepassxc:cambium-devices/<entry>>` (see
  `references/02_device-access-and-vault.md`). Avoid the substrings `credential`/`secret`/`password` in file **paths** in this pack — the workspace's OPA write-gate hard-blocks them regardless of
  content (hit and worked around 2026-09-17 — the file is now named `references/02_device-access-and-vault.md`, not `credentials`, for exactly this reason).
- Boundary with `skill-smc`: device/hardware/credential/asset-register/cnMaestro knowledge belongs here; SMC box, Ansible authoring, and provisioning-role knowledge belongs to `skill-smc`. A fact
  spanning both gets written to both packs in the same session.
- Follow naming convention for time-bound docs: `<slug>-YYYYMMDD_hhmm.md`.
- Keep `CHANGELOG.md` current — append entries when content or structure changes.
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries live in `docs/history/`; do not read them by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one.

## Project-coherence checklist

### Tier 1 — Reference files (content source — update first)

| New knowledge type                                                                             | Target file                                                            |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Device family/model/firmware/EoL fact                                                          | `references/01_overview.md`                                            |
| Vault structure change, `kp`/`keepassxc-cli` behaviour                                         | `references/02_device-access-and-vault.md`                             |
| Asset-register naming/drift, a new site's conventions                                          | `references/03_asset-register-conventions.md`                          |
| `device-inventory.csv` schema change, extraction workflow fact                                 | `references/04_device-inventory-schema.md`                             |
| New coverage gap, staleness risk, unvalidated assumption                                       | `references/05_known-issues.md`                                        |
| Device REST API / SSH CLI data point, adapter method, config-backup or write-ops boundary fact | `references/06_device-api-cli-reference.md`                            |
| New reusable Cambium-domain script or tool                                                     | `scripts/` — see Tier 1b below                                         |
| No existing file fits                                                                          | Propose a new numbered file; add the `RUNBOOK.md` row in the same pass |

**Do not write new operational content to `RUNBOOK.md`** — it is a navigation index only. Write content to the matching reference file.

### Tier 1b — Scripts (moved or written in another project — catalog fully in the same pass)

A script belongs here, not in a consuming project, when it is Cambium-domain tooling reusable across projects rather than specific to one project's investigation — the same test already applied to
`scripts/cambium-portal.sh` (vendor-portal automation) and `scripts/extract-asset-register.py` (asset-register extraction), both moved in from `cambium-swap`. Moving the file alone is not enough —
every one of these must land in the same pass, or the script is invisible to the next agent that opens this pack instead of the consuming project:

| Step                          | Update                                                                                                                                                               |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Move the file                 | `scripts/<name>`, with a header comment stating where it came from and why it belongs here (see the two existing scripts for the pattern)                            |
| Catalog it                    | `scripts/README.md` Raw Script Inventory — purpose, inputs, outputs, safety label(s), idempotency, when to use                                                       |
| Route to it                   | `RUNBOOK.md` — a routing row if the script answers a task type; `justfile` — a recipe if it should run via `just`                                                    |
| Prove the catalog is enforced | Run `scripts/check_governance.py` — it fails on any file under `scripts/` not named in `scripts/README.md` (this is a real, executed check, not a                    |
|                               |   documented intention)                                                                                                                                              |
| Metadata + history            | `manifest.json` version bump; `CHANGELOG.md` entry noting where the script came from                                                                                 |

**Do not treat "I moved the file" as done.** The gap this closes is real: `scripts/cambium-portal.sh` sat uncataloged in `scripts/README.md` for a full session after being moved in, because
`scripts/check_governance.py`'s coverage check only covered `RUNBOOK.md`↔`references/` and had no equivalent for `scripts/README.md`↔`scripts/` — the checker's own documented claim ("fails on an
uncatalogued script") was false until that gap was found and closed 2026-09-17. Re-run the checker after adding a script; do not assume the catalog step happened just because the file is present.

### Tier 2 — Routing and navigation (check for staleness after Tier 1)

- `RUNBOOK.md` Reference Routing table — new reference file or renamed file → add/update routing row
- `SKILL.md` References section — pointer to the new/updated file
- `AI_NAVIGATION.md` routing table and Project context files table — new file → add row
- `context-map.yaml` routing section — new domain → add routing entry

### Tier 3 — Metadata and history

- `manifest.json` — bump `version` (patch) + `updated_at` if any reference file content or structure changed; add/update `stable_facts` for durable new facts
- `CHANGELOG.md` — append entry for what changed
- `SCRATCHPAD.md` — update current state, tick/add open items, prepend session history summary

## Cross-project write-back trigger

Any project that invokes this skill and produces Cambium device/hardware/credential/asset-register/cnMaestro knowledge — **or writes a Cambium-domain script or tool** — must write it back here before
the session closes — this is the `SKILL.md` Standing Write-Back Contract in enforceable form. Concretely: `skill-slurp-chat` and `project-coherence`, run in any project that touched Cambium work this
session, must check for unpromoted Cambium knowledge before closing out. If either closes a session without this check, treat the closeout as incomplete.

**Closeout self-check:** did this session (a) learn a new device fact, credential/vault behaviour, asset-register convention, or inventory-schema gotcha that isn't yet reflected in this pack's
`references/`, or (b) write or modify a Cambium-domain script that isn't yet cataloged in this pack's `scripts/`? If either is yes, promote it in the same pass per the Tier 1/1b–3 steps above rather
than deferring it. A script sitting in a consuming project's own `scripts/` folder because a session ran out of time to move it is exactly the failure mode this trigger exists to catch — this pack's
own governance checker cannot see into another project, so nothing will flag the gap from this side.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

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
12. Treat uncataloged scripts as `unknown` safety until inspected. Run defined audit/check commands before completing work.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. If `scripts/check_governance.py` exists, run it before claiming any durable change is complete. When it fails, fix the project, not the check. Adding a new artifact class, generated output, or a
    constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This pack's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions; run `python3 scripts/check_governance.py` to gate on them. It is
stdlib-only and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file.

### The checker grows with the pack

| Change made                                 | Required checker update                                                                                                                                |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Add a new `references/*.md` file            | None — the coverage check fails until `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, and `context-map.yaml` all name it                                 |
| Add a script to `scripts/`                  | Catalog it in `scripts/README.md`; coverage fails until then                                                                                           |
| Add a new governance surface that could     | Don't — `manifest.json` is the sole version-of-record (see `.archcore/rules/manifest-version-discipline.rule.md`); point to it instead. No automated   |
|   restate this pack's version               |   check enforces this yet — `scripts/check_governance.py` has no anti-duplicate-version check, despite this row previously naming a                    |
|                                             |   `VERSION_STAMP_SURFACES` registry that was never implemented. Treat as a residual governance gap until a real check exists.                          |
| Rename or move a file                       | Nothing — path resolution catches every stale reference automatically                                                                                  |
| Retire a check                              | Record why in `CHANGELOG.md`                                                                                                                           |

### Rules that are not negotiable

- **When a check fails, fix the pack, not the check.**
- **A new check must be able to fail.** Prove it by breaking the pack deliberately and watching it go red.
- **Text matching does not verify behavior.** Where a check must verify behavior, execute it and assert on the result.
- **Do not enforce history.** `CHANGELOG.md` is an append-only log; a past fact recorded there is evidence, not a live claim.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime) and the session owes it a write-back.
