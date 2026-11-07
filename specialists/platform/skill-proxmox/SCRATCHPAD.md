# SCRATCHPAD

Agent working memory for skill-proxmox. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation -->

## Current state

**Phase:** first release (heading in [CHANGELOG.md](CHANGELOG.md)), created 2026-11-07 to skill-nautobot's structure; uncommitted, awaiting operator review.

Standalone, cross-project Proxmox VE 9.x and bpg/proxmox pack. Seeded from the smc-resiliency x86 lab (read-only on one 9.1.5 node) and 51 verbatim captures of primary sources.

---

## Open items

- [ ] Operator review: accept or change the six proposed `.archcore/` documents (memory channel `proxmox`, independent pack, search order, checker in tests, version of record, live-probe plan).
- [ ] Commit (operator): pack folder, the registry rows and the install symlinks are uncommitted.
- [ ] Live probes on a disposable node for the `UNVERIFIED` items: `pvesh set /cluster/sdn` apply form, live restore from PBS, hook-script phase names, the task list's errors filter, the disks list endpoint,
  Ubuntu cloud image without qemu-guest-agent.
- [ ] Client evaluation matrix per [tests/eval-procedure.md](tests/eval-procedure.md) (with and without the skill).
- [ ] Re-verify the cookbook when the lab node moves to 9.2 (pending in its update queue).

---

## Key anchors

| Item             | Detail                                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| Install          | `~/.claude/skills/skill-proxmox` and `~/.agents/skills/skill-proxmox` are symlinks to this folder (as skill-nautobot) |
| Observed version | Proxmox VE 9.1.5 (lab; see `compatibility.yaml`)                                                                      |
| Provider         | bpg/proxmox 0.120.0 (latest on 2026-11-07)                                                                            |
| Memory channel   | memory-keeper `proxmox` (proposed)                                                                                    |
| Origin project   | smc-resiliency (its spike/x86 folder: the x86 lab)                                                                       |
| Gate             | `just test` then `just check`                                                                                         |

---

## Recent decisions

- 2026-11-07 — Pack mirrors skill-nautobot (operator). Sources kept as verbatim captures under `documents/research-sources-20261107/` with sha256 in `documents/readme.md`; captures exempt from the
  redaction scan except private keys.
- 2026-11-07 — New helpers use two-space indentation (skill-coder rule); the copied governance checker keeps four.
