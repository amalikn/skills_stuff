---
Title: Scratchpad
Category: working-state
Status: current
Summary: Current working state; older entries rotate to docs/history, older open items to docs/trackers.
Authority: working-state
Scope: Working state between sessions
Kind: state
Budget: 200 lines, 25 KB
Last reviewed: 2026-11-09
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261109_1125.md
---

# SCRATCHPAD

Agent working memory for skill-proxmox. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation; updated 2026-11-09 slurp close -->

## Current state

**Phase:** first release plus Unreleased write-backs (heading in [CHANGELOG.md](CHANGELOG.md)); committed and pushed (skills_stuff bd2a566, 95bf5f2).

Standalone, cross-project Proxmox VE 9.x and bpg/proxmox pack. Seeded from the smc-resiliency x86 lab (read-only on one 9.1.5 node) and 58 verbatim captures of primary sources.

2026-11-09: gap review filled Ceph, node removal, arm64 hosts, migration, resource mappings and virtiofs, notifications, 2FA, PBS 4.x and PDM 1.x from the docs (no lab run yet); skill-ai-it refresh
done; `.archcore/` accepted; AGENTS.md trimmed and tracked in Git.

---

## Open items

- [ ] Live probes on a disposable node for the `UNVERIFIED` items: `pvesh set /cluster/sdn` apply form, live restore from PBS, hook-script phase names, the task list's errors filter, the disks list
  endpoint, Ubuntu cloud image without qemu-guest-agent.
- [ ] Client evaluation matrix per [tests/eval-procedure.md](tests/eval-procedure.md) (with and without the skill), scenarios P-S01 to P-S20.
- [ ] Re-verify the cookbook when the lab node moves to 9.2 (pending in its update queue).
- [ ] Live probe on a three-node lab cluster for the 2026-11-09 doc-only sections (Ceph, migration, mappings, notifications, node removal): accepted plan step 3.
- [ ] Proposed, not decided: archcore rule `dated-latest-claims` ([ARCHCORE_PROMOTION_CANDIDATES.md](ARCHCORE_PROMOTION_CANDIDATES.md)); promote or reject.
- [ ] Still baselined: AI_NAVIGATION.md 9 lines over its 150-line budget (the routing table is a checked rule); `.ai-context/` (generated, no header).

---

## Key anchors

| Item             | Detail                                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| Install          | `~/.claude/skills/skill-proxmox` and `~/.agents/skills/skill-proxmox` are symlinks to this folder (as skill-nautobot) |
| Observed version | Proxmox VE 9.1.5 (lab; see `compatibility.yaml`); latest 9.2 (x86 2026-05-21, arm64 2026-08-05), checked 2026-11-09   |
| Provider         | bpg/proxmox 0.120.0 (still latest on 2026-11-09)                                                                      |
| Memory channel   | `proxmox`, both backends (accepted)                                                                                   |
| Origin project   | smc-resiliency (its spike/x86 folder: the x86 lab)                                                                    |
| Gate             | `just test` then `just check`                                                                                         |
| Registered in    | project_stuff and skills_stuff AGENTS.md, "Shared tools and skills" (2026-11-09)                                      |

---

## Recent decisions

- 2026-11-09 — Six `.archcore/` documents corrected and accepted (operator); version-of-record rule enforced by `check_version_restated`; candidates file written, tags left.
- 2026-11-09 — AGENTS.md trimmed to one line plus a link per rule (operator); governance files are tracked in Git on the operator's GitHub (global rule).
- 2026-11-07 — Pack mirrors skill-nautobot (operator). Sources kept as verbatim captures with sha256 in `documents/readme.md`; captures exempt from the redaction scan except private keys.

---

## Session history

- 2026-11-09 — Gap review with online research, ASCII diagrams, skill-ai-it refresh, archcore review and acceptance, AGENTS.md trim; global Git-tracking rule and memory-index split done from this
  session. Record: [docs/session-record-20261109_1235.md](docs/session-record-20261109_1235.md).
- 2026-11-07 — Pack created from the smc-resiliency x86 lab and 51 captures; write-backs from smc-resiliency X1 and X2.

---

## Next actions

- Run the lab probes above when a disposable node or a three-node lab cluster is available; record each as a Learned or Disputed entry plus a CHANGELOG line.

---

## Memory pointers

- memory-keeper channel `proxmox`: `skill-proxmox.gap-review-20261109`, `skill-proxmox.refresh-archcore-20261109`, `session.closeout.20261109.skill-proxmox`; channel `global-governance`:
  `governance.git-tracking-rule-20261109`, `memory.index-hybrid-split-20261109`. project-context: skills_stuff (channel `proxmox`), global-governance-policy.
