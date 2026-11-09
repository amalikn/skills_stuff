---
Title: skill-smc Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-smc specialist pack — canonical source for SMC box operational knowledge and ansible-wifi authoring
Last reviewed: 20260731_1300
Summary: Agent guidance for maintaining and using the skill-smc specialist pack. Covers specialist structure, reference routing, and update discipline. Cross-repo trigger rule broadened 2026-07-31 to
  cover the whole local-knowledge-ansible/ansible-wifi tree (current and future subfolders) and both skill-slurp-chat and project-coherence as mandatory feed-back trigger points.
---

@../../../AGENTS.md

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Project-coherence checklist](#project-coherence-checklist)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)
- [Code changes](#code-changes)

---

## Working rules

- `SKILL.md` is the agent-facing activation surface — it defines triggers, inline quick-reference, and pointers to `references/`.
- `RUNBOOK.md` is the navigation index — it maps task types to specific numbered reference files. Do not use it as a content source.
- The numbered `references/<nn>_*.md` files (plus the YAML/CSV registries) are the content source files. Load only the one needed for the task.
- `manifest.json` is the machine-readable specialist metadata. Update `version` and `updated_at` when any content file changes.
- `~/.claude/skills/skill-smc` is a symlink to this folder; there is no copy step or adapter document to keep in sync (retired 2026-10-07).
- Keep `SKILL.md` short: detail belongs in the reference that owns it, and `SKILL.md` keeps only what decides which reference to open.
- Run Python through the pack-root `justfile` (`just bootstrap` once, then `just check` etc.); recipes use the `.mise.toml`-pinned working-cache venv
  (`check_recipe_interpreter` fails a recipe that runs bare `python3`).
- Scripts live in job folders under `scripts/` (`ansible/`, `access/`, `probes/`, `capture/`, `fleet/`, `metrics/`, `routing/`, `switch/`), tests beside
  them; justfiles stay directly under `scripts/`, never in a job folder (operator, 2026-10-27). A moved script's callers in other repos are updated,
  not shimmed. Layout table: `scripts/README.md`.
- After editing any `references/` file, check `SKILL.md` References section and `RUNBOOK.md` routing table for consistency.
- After adding a new reference file, update the `RUNBOOK.md` routing table, `SKILL.md` References section, `AI_NAVIGATION.md` tables and `context-map.yaml` routing in the same pass.
- Follow naming convention for time-bound docs: `<slug>-YYYYMMDD_hhmm.md`.
- Keep `CHANGELOG.md` current — append entries when content or structure changes.
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries live in `docs/history/`; do not read them by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one.

## Project-coherence checklist

When running `project-coherence` on the `skill-smc` specialist pack — whether triggered directly or from an ansible-wifi session — apply this tier order:

### Tier 1 — Reference files (content source — update first)

| New knowledge type                                                        | Target file                          |
| ------------------------------------------------------------------------- | ------------------------------------ |
| Captive portal, Kohana, Eclipse config, portal PHP (mod_php, not PHP-FPM) | `references/10_captive-portal.md`    |
| Vagrant lab bring-up, VirtualBox, vsmc nuances                            | `references/11_vagrant-lab.md`       |
| VLAN 501, content filtering, MAC randomization, CAKE                      | `references/12_content-filtering.md` |
| New coverage gaps, staleness risk, unvalidated assumptions                | `references/13_known-issues.md`      |
| URL capture, PCAP, dns_query                                              | `references/09_url-capture-pcap.md`  |
| Ansible authoring, topology, cache, blast radius                          | `references/08_ansible-authoring.md` |
| All other domains → per routing table in `RUNBOOK.md`                     | matching `references/0N_*.md`        |

**Do not write new operational content to `RUNBOOK.md`** — it is a navigation index only. Write content to the matching reference file.

### Tier 2 — Routing and navigation (check for staleness after Tier 1)

- `RUNBOOK.md` routing table — new reference file or renamed file → add/update routing row
- `SKILL.md` References section — pointer to the new/updated file
- `AI_NAVIGATION.md` routing table and Project context files table — new file → add row
- `context-map.yaml` routing section — new domain → add routing entry

### Tier 3 — Metadata and history

- `manifest.json` — bump `version` + `updated_at` with every CHANGELOG entry, docs-only ones included: `check_version_format` requires the newest
  entry to end with `(vA -> vB)` matching the manifest (found 2026-10-27). Patch runs 0 to 9; after `x.y.9`
  comes `x.(y+1).0` (operator, 2026-10-07; `just check` enforces it)
- `CHANGELOG.md` — append entry for what changed (references updated, routing added, version bump)
- `SCRATCHPAD.md` — update current state, tick/add open items, prepend session history summary

### Tier 4 — Generated context (do last)

Regenerate `.ai-context/governance-pack.md`:
```
repomix --config /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc/repomix.config.json
```

### Cross-repo trigger rule (when triggered from ansible-wifi or local-knowledge-ansible/ansible-wifi)

**Scope: the whole tree, not just top-level sessions.** This rule fires for work done in `/Volumes/Data/_ansible/ansible-wifi` itself, in `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi`,
and in **any current or future subfolder of either** — `issues/**`, `ai-tooling/`, `opa/`, `plans/`, `scripts/`, `history/`, and any new investigation/design workspace bootstrapped later. Every such
subfolder is expected to `@`-import `ansible-wifi-root-governance/AGENTS.md` (the established convention — see e.g. `issues/apn/routing-issue/AGENTS.md`), which is what makes this rule reach new
folders automatically without a separate wiring step per folder.

**Trigger conditions — broader than "bug fixes".** Any of the following, from any session anywhere in that tree, counts as producing knowledge this pack must capture:
- An incident, debug fix, or change in assumptions (the original narrow case).
- A design analysis or recommendation — **even if not yet implemented or canary-tested.** Do not wait for something to ship before capturing it; mark it clearly as a design recommendation with its
  implementation status, so a future session doesn't have to rediscover it from a dated investigation-folder doc.
- A new or updated ADR, rule, guide, or spec under `.archcore/`.
- A change to the OPA policy layer (`opa/policies/`, `opa/data/`) or its precedence/gating logic.
- A reusable script worth generalizing for future investigations (promote to `skill-smc/scripts/` per its own promotion checklist in `scripts/README.md`).
- A ROADMAP-tracked architectural decision or backlog item that changes what this pack currently documents as true.

**Trigger points — both are mandatory, not just one.** Both `skill-slurp-chat` and `project-coherence`, run anywhere in the tree above, must check for unpromoted knowledge before closing out — not
only project-coherence. If either closes a session without this check, treat the closeout as incomplete.

**Steps once new knowledge is identified:**
1. Write content to the matching `references/*.md` in this pack (use `RUNBOOK.md`'s routing table to find the file — never write content to `RUNBOOK.md` itself).
2. Verify the RUNBOOK.md routing table has a row pointing to that reference.
3. Bump `manifest.json` version + `updated_at`.
4. Append CHANGELOG.md entry.
5. Update SCRATCHPAD.md current state.
6. Regenerate `.ai-context/governance-pack.md` (Tier 4, above).

**Closeout self-check (this is what prevents needing another full directory sweep):** before ending any `skill-slurp-chat` or `project-coherence` pass that touched this tree, explicitly ask — did this
session create or change anything under `local-knowledge-ansible/ansible-wifi/**` (a new issue report, design doc, ADR, script, ROADMAP edit, `.remember` entry) that isn't yet reflected here? If yes,
promote it in the same pass per the steps above rather than deferring it.

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

This pack's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions; run `python3 scripts/check_governance.py` to gate on them. It is
stdlib-only and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file. It is cheap and it is the only thing standing between this pack's
documents and silent decay.

### The checker grows with the pack

The check count is a coverage signal, not a score. It is expected to rise as the pack acquires structure. Extend it on these triggers:

| Change made                                           | Required checker update                                                                                                                      |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Add a new `references/*.md` file                      | None — the coverage check fails until `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, and `context-map.yaml` all name it. That is the intended |
|                                                       |   workflow, not an error to route around                                                                                                     |
| Add a script to `scripts/`                            | Catalog it in `scripts/README.md`; coverage fails until then                                                                                 |
| Add a new governance surface that could restate this  | Add it to `VERSION_STAMP_SURFACES` in `scripts/check_governance.py`                                                                          |
|   pack's version number                               |                                                                                                                                              |
| Rename or move a file                                 | Nothing — path resolution catches every stale reference automatically                                                                        |
| Retire a check                                        | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from one that never existed                                      |

### Rules that are not negotiable

- **When a check fails, fix the pack, not the check.** Broadening an ignore-list to silence a true positive, or exempting the file that failed, converts a real finding into a permanent blind spot that
  the next agent has no way to discover.
- **A new check must be able to fail.** Prove it by breaking the pack deliberately and watching it go red.
- **Text matching does not verify behavior.** Where a check must verify behavior, execute the behavior and assert on the result, not grep for a keyword.
- **Do not enforce history.** `CHANGELOG.md` is an append-only history log; a past fact recorded there is evidence, not a live claim, and is exempt from the checks above by design.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime) and the session owes it a write-back.
