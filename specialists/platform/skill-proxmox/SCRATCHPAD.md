---
Title: Scratchpad
Category: working-state
Status: current
Summary: Current working state; older entries rotate to docs/history, older open items to docs/trackers.
Authority: working-state
Scope: Working state between sessions
Kind: state
Budget: 200 lines, 25 KB
Last reviewed: 2026-11-07
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261109_1125.md
---

# SCRATCHPAD

Agent working memory for skill-proxmox. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation -->

## Current state

**Phase:** first release (heading in [CHANGELOG.md](CHANGELOG.md)), created 2026-11-07 to skill-nautobot's structure; uncommitted, awaiting operator review.

Standalone, cross-project Proxmox VE 9.x and bpg/proxmox pack. Seeded from the smc-resiliency x86 lab (read-only on one 9.1.5 node) and 51 verbatim captures of primary sources.

---

## Open items

- [x] Operator review: the six `.archcore/` documents corrected and accepted (operator, 2026-11-09); their review-date findings left the baseline.
- [x] Commit: pack folder, registry rows and install symlinks committed in skills_stuff bd1691d (2026-11-07).
- [x] `just check` passes (2026-11-09 refresh): summaries written, AI_NAVIGATION 322 to 159 lines. Still baselined: AI_NAVIGATION 9 lines over 150 (its routing table is a checked rule), `.ai-context/` (generated, no header).
- [ ] Live probes on a disposable node for the `UNVERIFIED` items: `pvesh set /cluster/sdn` apply form, live restore from PBS, hook-script phase names, the task list's errors filter, the disks list endpoint,
  Ubuntu cloud image without qemu-guest-agent.
- [ ] Client evaluation matrix per [tests/eval-procedure.md](tests/eval-procedure.md) (with and without the skill).
- [ ] Re-verify the cookbook when the lab node moves to 9.2 (pending in its update queue).
- [ ] Live probe on a cluster for the 2026-11-09 doc-only sections (Ceph, migration, mappings, notifications): today they rest on the docs, with no lab run.

---

## Key anchors

| Item             | Detail                                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| Install          | `~/.claude/skills/skill-proxmox` and `~/.agents/skills/skill-proxmox` are symlinks to this folder (as skill-nautobot) |
| Observed version | Proxmox VE 9.1.5 (lab; see `compatibility.yaml`)                                                                      |
| Provider         | bpg/proxmox 0.120.0 (latest on 2026-11-07)                                                                            |
| Memory channel   | `proxmox`, both backends (accepted)                                                                                   |
| Origin project   | smc-resiliency (its spike/x86 folder: the x86 lab)                                                                       |
| Gate             | `just test` then `just check`                                                                                         |

---

## Recent decisions

- 2026-11-07 — Pack mirrors skill-nautobot (operator). Sources kept as verbatim captures under `documents/research-sources-20261107/` with sha256 in `documents/readme.md`; captures exempt from the
  redaction scan except private keys.
- 2026-11-07 — New helpers use two-space indentation (skill-coder rule); the copied governance checker keeps four.
