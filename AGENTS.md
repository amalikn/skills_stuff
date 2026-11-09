@/Users/malik.ahmad/.agents/AGENTS.md

Title: Skills Stuff Repo Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: Repo-local agent behavior for the skills_stuff source-of-truth repo
Source of truth: [AGENTS.md](/Volumes/Data/_ai/_mcp/skills_stuff/AGENTS.md)
Synced from: [agent-governance-guide.md](/Volumes/Data/_ai/governance/categories/agent-governance-guide.md)
Synced to: /Volumes/Data/_ai/governance/sync-map.yaml
Last reviewed: 2026-05-14
Summary: Repo-local agent guidance for skills_stuff with explicit linkage to the canonical governance stack.

# AGENTS.md

This repository is the canonical source-of-truth for specialist packs and client export adapters. Treat `specialists/` as the authoring surface and `exports/` as delivery/adaptation layers unless the
task explicitly says otherwise.

Working rules for this repo:
- Inspect the touched specialist and any corresponding export adapter before editing.
- Do not treat runtime installs such as `~/.codex/skills` as the source-of-truth for reusable guidance.
- Keep canonical content and export adapters aligned when a change affects both layers.
- Follow the canonical markdown policy from [`/Volumes/Data/_ai/governance/categories/markdown-guide.md`](/Volumes/Data/_ai/governance/categories/markdown-guide.md). For new time-bound markdown files in this repo, use `<slug>-YYYYMMDD_hhmm.md` unless the file
  is a stable convention-locked entrypoint.
- Use [`skills.md`](/Volumes/Data/_ai/_mcp/skills_stuff/skills.md) for common task patterns and [`.agents/validation.md`](/Volumes/Data/_ai/_mcp/skills_stuff/.agents/validation.md) for current validation limits.
- If the correct source-of-truth or adapter scope is unclear, stop and ask the operator instead of editing both sides speculatively.
- **venv + ephemeral runtime placement (2026-04-23, aligned with the packs 2026-10-07):** a skill pins its Python in its own `.mise.toml` (`python = "3.14"` unless the skill's pyproject or operator
  instruction requires another version) and builds the venv with `just bootstrap` (`mise install`, then `mise exec -- python -m venv .venv`) at
  `/Volumes/Data/_ai/_skills/skills-working-cache/<skill>/.venv` (rebuildable), as skill-smc, skill-cambium and skill-mikrotik do. Its `justfile` sets `wc` to that peer and `py := wc +
  "/.venv/bin/python"`; every recipe calls `{{py}}` and depends on `_require-venv`, never a bare interpreter or a script's shebang (skill-ai-it SKILL.md, Runtime isolation; its `check_governance.py`
  enforces it). Ephemeral runtime state (logs, pid files, sockets) goes under `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/{logs,run}/`. Never place the venv or runtime state inside
  `skills_stuff/<skill>/` — even when the `-github` colocation override applies, it only governs operator-managed persistent state, not rebuildable caches or ephemeral runtime. See the
  [storage-routing-guide](/Volumes/Data/_ai/governance/categories/storage-routing-guide.md) entry for the full rule.
- **Local `-github` clone override (2026-04-23):** when a skill under this repo has a local upstream clone at `skills_stuff/<skill>/<skill>-github/`, colocate the skill's operator-managed persistent
  state — `config/`, saved inputs/queries, output artifacts, outcome docs, and the skill-level `README.md` — inside the same `skills_stuff/<skill>/` folder instead of routing to a sibling `*-data`
  root. Rebuildable caches and ephemeral runtime state still follow default routing. The `<skill>-github/` directory stays untouched as the upstream reference. Note: this does NOT change the canonical
  `specialists/` → `exports/` authoring/adapter split — it only governs where operator-managed persistent state lives for skills that carry a local upstream clone. See the [storage-routing-guide](/Volumes/Data/_ai/governance/categories/storage-routing-guide.md) entry
  for the full rule.
- **Vendor device packs record GPS per device type (operator, 2026-10-07).** A pack covering a hardware vendor (skill-cambium, skill-mikrotik, TP-Link in skill-smc, any future one) gives every device
  type in its OID registry a `gps` block: `provides_coordinates` `"yes"` (own fix), `"configured"` (a typed-in position, no receiver), `"no"` or `"unknown"`, `how` (the OIDs, API getter or reason) and
  `verified`. GPS sync on a radio is not coordinates. unified-network-controller mirrors the answer in its catalog `gps.device_types` and its `check_device_type_gps` fails on a type with none.
- **Every skill's code follows skill-coder (operator, 2026-10-20):** invoke `skill-coder` before adding or changing any script in any skill here, the operator's packs and local changes to vendored
  ones alike, and follow its rules (purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime); the session owes it a write-back. Each of the operator's `skill-*` packs that
  holds scripts names skill-coder in its own AGENTS.md (or SKILL.md where it has none). Vendored packs (superpowers, caveman, financial-services, swarms, the Codex system skills) are not edited for
  this; this rule covers them.
- Treat this file as repo-local guidance only. It is not a global cross-repo policy file and not a native requirement of any client runtime.
- Route Graphify workspace governance through `graphify/` with upstream source in `graphify/graphify-github/`; keep local macOS install fact (`/Users/malik.ahmad/.local/bin/graphify`) documented in
  the workspace README and synced with runtime reality.

## Contents

- [Detailed Skill Surfaces](#detailed-skill-surfaces)
- [Shared tools and skills](#shared-tools-and-skills)
- [Canonical Governance Linkage](#canonical-governance-linkage)

---

## Detailed Skill Surfaces

Detailed catalog, installation, and authoring guidance lives in [`.agents/skill-surfaces.md`](.agents/skill-surfaces.md). Read it before changing a skill surface or runtime install.

## Shared tools and skills

Known to every project here (operator, 2026-11-02):

- **all-scraper** (`/Volumes/Data/_ai/_tool/tools_stuff/all-scraper`): `just -f <that folder>/justfile md <url>` turns a web page into Markdown with a real browser; `fetch <url> --markdown [--js]` is
  the fallback when a page blocks agents. A problem met is written back to the tool (its AGENTS.md, Feedback write-back). A bot wall that still refuses goes to the operator, who fetches the page.
- **skill-coder**: invoke it before writing, changing or reviewing any code. It holds the practice, the language rules, the design patterns (`references/design-patterns.md`), and how a many-language
  engine interlocks (`references/engine-composition.md`).
- **skill-drawio**: any `.drawio` file or diagram from data. One YAML flow map draws step pages, flowcharts, vertical swimlanes and BPMN (`references/charts-and-trace.md`); `trace_query.py` answers
  from a map before reading the code, and `trace_sync.py` holds a map to the code it cites.
- **skill-proxmox** (`specialists/platform/skill-proxmox`; operator, 2026-11-09): invoke it for any Proxmox VE 9.x work (nodes, clusters, storage and Ceph, networking and SDN, VMs and containers,
  migration, access control and API tokens, backups and PBS, HA, upgrades, notifications) and for OpenTofu with the bpg/proxmox provider. It reads by default; any write to a node needs the project's
  authorization and `--apply`. Node names, addresses and VMIDs stay in the project. Reusable Proxmox learning is written back to the pack before the session closes (its `SKILL.md`, Standing write-back
  contract).

## Canonical Governance Linkage

- Cross-repo reusable governance lives under [`/Volumes/Data/_ai/governance/README.md`](/Volumes/Data/_ai/governance/README.md).
- The local governance index for this repo lives under [`/Volumes/Data/_ai/_mcp/skills_stuff/governance/README.md`](/Volumes/Data/_ai/_mcp/skills_stuff/governance/README.md).
- This file remains repo-local operational guidance and reconciles reusable rules upward only through explicit review.
