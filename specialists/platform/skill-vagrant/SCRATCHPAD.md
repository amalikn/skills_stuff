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
Open items tracker: docs/trackers/open-items-20261109_1123.md
---

# SCRATCHPAD

Agent working memory for skill-vagrant. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation -->

## Current state

**Phase:** first release, heading in [CHANGELOG.md](CHANGELOG.md); created 2026-11-07 beside skill-nautobot and skill-proxmox, not yet committed.

## Open items

- [x] `just check` green 2026-11-09 (front matter added, `.archcore/` dated, AI_NAVIGATION.md in budget; `.ai-context` baselined as generated).
- [x] ports.ubuntu.com snapshot question: resolved by the Learned 2026-11-07 entry in `references/tool-choice-and-lab-symmetry.md` (prose promotion at next release).
- [x] Box copies made 2026-11-09 on the external storage disk, restore tested (was: storage place for the box copies (Parallels and VirtualBox builds of bento/ubuntu-24.04 202510.26.0) before 2026-12-31 — `.archcore/plans/`.
- [x] All five `.archcore/` documents accepted 2026-11-09 (operator) (was: accept or change the five documents (new: `.archcore/rules/name-the-provider.rule.md`, ADR amendment 2026-11-09).
- [x] Extension Pack recorded as personal use (operator, 2026-11-09); PUEL excludes business use (`references/virtualbox.md`, Licence).
- [x] Done 2026-11-09 (spike VM: no /vagrant mount; scratch VM under 2.4.10: fuse.prl_fsd): `findmnt /vagrant` on smc-pi-spike01 (does 24.04 use `prl_fsd`? settles the issue-526 reach).
- [x] Done 2026-11-09 (VirtualBox VMs, provider-aware ids, 37 tests): extend to `VBoxManage list vms` and vagrant-qemu machines (skill-coder; tests first).
- [x] Committed 2026-11-09 as vagrant_stuff 35f6247, teleport.yaml left untracked (token) (was: commit `/Volumes/Data/_vagrant/vagrant_stuff/family-friendly-vsmc01` and `/Volumes/Data/_vagrant/vagrant_stuff/mikrotik-qemu01` (untracked; cited as working copies) and pin `bento/ubuntu-22.04` there.
- [x] Tested 2026-11-09 on scratch VMs (new id, new lease) (was: test the machine-id reset procedure on a Parallels clone and record the new DHCP lease (UNVERIFIED in `references/clones-snapshots-and-identity.md`).
- [x] vagrant-parallels ignores `config.vm.cloud_init` (lab run 2026-11-09).
- [ ] Re-check the Vagrant LICENSE at the next release tag (MIT revert is on `main` only; no release after v2.4.9 on 2026-11-09).
- [x] Evaluation 2026-11-09: V-S16 and V-S18 recorded in tests/eval-procedure.md (was: live evaluation per [tests/eval-procedure.md](tests/eval-procedure.md), now including V-S15 to V-S18.

- [ ] `family-friendly-vsmc01`: VirtualBox has no VMs for its two machines (deleted); the next `vagrant up` there recreates them.
- [ ] Watch where bento publishes after 2026-12-31 (plan step 5).

## Key anchors

| Item              | Detail                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| Install           | symlinks in `~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` |
| Observed versions | see `compatibility.yaml` (lab-mac-2026-11-07)                                                    |
| Memory channel    | memory-keeper `vagrant`                                                                          |
| Origin project    | smc-resiliency (Pi spike lab)                                                                    |
| Gate              | `just test` then `just check`                                                                    |
