# SCRATCHPAD

Agent working memory for skill-vagrant. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-11-07 at creation -->

## Current state

**Phase:** first release, heading in [CHANGELOG.md](CHANGELOG.md); created 2026-11-07 beside skill-nautobot and skill-proxmox, not yet committed.

## Open items

- [ ] `just check` fails (seen 2026-11-08 from smc-resiliency's slurp): files with no header summary (AI_NAVIGATION, .ai-context and others), as in skill-proxmox: pack adoption work, write each summary from its file.
- [ ] Operator review of the four `.archcore/` documents (all `proposed`) — index [.archcore/index.guide.md](.archcore/index.guide.md).
- [ ] Keep the pinned box before the registry closes (2026-12-31): `vagrant box repackage bento/ubuntu-24.04 parallels 202510.26.0`, stored outside the repo with its sha256 (operator's call where).
- [ ] Test on the arm64 lab whether `apt-get update --snapshot <id>` works against `ports.ubuntu.com` (UNVERIFIED in `references/tool-choice-and-lab-symmetry.md`).
- [ ] Test the machine-id reset procedure on a Parallels clone and record the new DHCP lease (UNVERIFIED in `references/clones-snapshots-and-identity.md`).
- [ ] Whether vagrant-parallels delivers `config.vm.cloud_init` data (UNVERIFIED).
- [ ] Re-check the Vagrant LICENSE at the next release tag (MIT revert is on `main` only as of 2026-11-07).
- [ ] Live evaluation per [tests/eval-procedure.md](tests/eval-procedure.md).

## Key anchors

| Item              | Detail                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| Install           | symlinks in `~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` |
| Observed versions | see `compatibility.yaml` (lab-mac-2026-11-07)                                                    |
| Memory channel    | memory-keeper `vagrant`                                                                          |
| Origin project    | smc-resiliency (Pi spike lab)                                                                    |
| Gate              | `just test` then `just check`                                                                    |
