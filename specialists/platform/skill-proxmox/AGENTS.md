---
Title: skill-proxmox Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-proxmox platform pack — canonical, cross-project source of reusable Proxmox VE and bpg/proxmox knowledge
Last reviewed: 2026-11-09
Summary: >-
  Agent guidance for maintaining and using skill-proxmox: artifact roles, the package contract, the write-back obligation, and the gates to
  run before calling work complete; scope and decisions are linked, not restated.
Budget: 150 lines, 12 KB
---

@../../../AGENTS.md

# AGENTS.md

## Working rules

- **Entry:** [SKILL.md](SKILL.md) is the activation surface (role and non-goals, routing, write-back contract) and must route every file in `references/`; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors its routing table. Load only the
  reference the task needs.
- **Decisions:** [.archcore/index.guide.md](.archcore/index.guide.md) (pack boundary, bpg not Telmate, search order, version of record, dated latest claims, live-node writes, project boundary, memory channel `proxmox`, live-probe plan) outranks this file.
- **Evidence:** claims in [sources.yaml](sources.yaml), environments in [compatibility.yaml](compatibility.yaml); a lab observation is not a production guarantee. Version of record: Proxmox VE 9.1.5 (lab, observed 2026-11-07).
- **Captures:** `documents/research-sources-<YYYYMMDD>/` holds verbatim pages, indexed in its `readme.md` and with sha256 in [documents/readme.md](documents/readme.md), both rows in the same pass. Captures are exempt from
  the redaction scan except for private keys.
- **Helpers:** `scripts/` is tested and stdlib-only; a new helper needs a test in `tests/test_helpers.py` and an entry in [scripts/README.md](scripts/README.md). Reads by default; a write prints its plan and needs
  `--apply`. Invoke `skill-coder` first (operator, 2026-10-20): new scripts use two spaces, the copied checker keeps four; the session owes it a write-back.
- **Live nodes:** reads are fine where the engaging project allows them; no `apt update`, `pvesh create|set|delete`, `qm set` or OpenTofu apply without that project's authorization.
- **Project facts** (node names, addresses, VMIDs, password-manager entries) stay in the engaging project; worked cases such as smc-resiliency's x86 lab are examples.
- **Redaction:** no credential, private address, production domain or unredacted field-data path in any pack file outside the captures; the contract scans every `.md`, `.yaml` and `.txt`, generated
  ones included.
- **Records:** time-bound notes use `<slug>-YYYYMMDD_hhmm.md`. Triage with `just docs <folder>` and `just stale` before editing; old entries via `just history <term>` or `just history-show <stamp>`;
  `just rotate --apply` creates `docs/history/` the first time a record passes its budget. <!-- path:example -->

## Package contract

`tests/test_package_contract.py` is executable and outranks generic skill-ai-it conventions. No manifest JSON, RUNBOOK or agents directory; every capture hashed; every reference routed in `SKILL.md`;
ledgers in schema; every Learned or Disputed entry has a CHANGELOG line naming the file and date (write-back is always two edits); no unsafe text, generated `.ai-context/` included (regenerate, then
re-run). `just test` runs the contract, the helper tests and the governance checker; run it before claiming any change complete.

## Cross-project write-back

A project that invokes this skill and learns reusable Proxmox VE or bpg/proxmox knowledge writes it back before the session closes ([SKILL.md](SKILL.md), Standing write-back contract;
[references/evolution-and-write-back.md](references/evolution-and-write-back.md)). If this source is not writable, the entry waits in the project as a candidate; a closeout in an engaging project that does not check for unpromoted Proxmox
knowledge is incomplete.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## AI navigation and context preflight

Before answering, planning or editing, read [AI_NAVIGATION.md](AI_NAVIGATION.md) first: it routes everything else (read order, source priority, task routing, scripts, checks, compaction recovery). Read [context-map.yaml](context-map.yaml)
only when changing routing or companion files.

- Sources disagree: stop and report, never guess. `SCRATCHPAD.md` is not durable truth unless marked `KEEP`; generated output never is.
- Run catalogued tasks only (`just --list`, `scripts/README.md`); an uncatalogued script is unknown safety. A new or changed script updates `scripts/README.md`.
- Before calling work done: `just check` (fix the project, not the check), and a `CHANGELOG.md` entry for any governance or navigation change.
- Preserve user content outside managed blocks.

<!-- END MANAGED: skill-ai-it:navigation -->

## Governance checks

[`scripts/check_governance.py`](scripts/check_governance.py) turns this pack's governance claims into assertions; `just check` gates on it and `just test` runs it. When a check fails, fix the project, not the check. A new check
must be able to fail (break a copy of the pack and watch it go red). Text matching does not verify behaviour. Do not enforce history: mark past counts `<!-- count:asat -->`. When to extend it (new
artifact class, generated output, restated constant, retired check): [governance-checks pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

## Linkage

Parent [../../../AGENTS.md](../../../AGENTS.md); structure mirrors [skill-nautobot](../skill-nautobot/SKILL.md); bootstrap source [skill-ai-it](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md); cross-repo governance [README](/Volumes/Data/_ai/governance/README.md).
