# Changelog

## Unreleased

- 2026-11-08 write-back from smc-resiliency X1: references/qemu-vms.md (iTCO_wdt on q35 without i6300esb; explicit modprobe past the deny-list; a crash reset in 91.1 s)
- 2026-11-07 (c) write-back from smc-resiliency X2: references/qemu-vms.md (OVMF entry deletion, watchdog driver), references/opentofu-bpg-provider.md (watchdog block, boot_order)

- 2026-11-07 (b) write-back from smc-resiliency's lab package: per-VMID ACL on 9.2, IPAM bind on start, isolated bridge; Vagrant transport

- 2026-11-07 write-back from smc-resiliency: references/upgrade-and-troubleshooting.md, references/networking-and-sdn.md (Learned 2026-11-07).

- 20261107 Pack created (operator, 2026-11-07: "create and setup skill-proxmox like skill-nautobot ... with the same detail and logic"); not committed.

## 0.1.0 — 2026-11-07

First release, built to skill-nautobot's structure: `SKILL.md`, sixteen focused references, claim and environment ledgers, sixteen scenarios, an offline package contract, three stdlib-only helpers
with tests, the skill-ai-it governance layer (`AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `justfile`, governance checker) and six proposed `.archcore/` documents. Sources: 51 verbatim
captures in `documents/research-sources-20261107/` (Proxmox VE 9.x admin guide chapters, man pages and wiki, 9.0 to 9.2 release notes, bugzilla lists, bpg/proxmox docs, changelog and issues, OpenTofu
docs, edk2 sources, one installed-source excerpt). Lab facts read only, on one Proxmox VE 9.1.5 node.

- 20261107 Helpers: `scripts/pve_ssh.py` (batched read-only reader), `scripts/pve_token_audit.py` (least-privilege audit), `scripts/pve_node_report.py` (node health and inventory; `--refresh --apply`
  is its only write); recipes `node_report`, `token_audit`, `coder_checks`. The contract test indexes captures recursively and exempts them from the redaction scan except for private keys.
- 20261107 Learned 2026-11-07 (a) in `references/architecture-and-cluster.md`: standalone `/cluster/status`, `localhost` as node name, 9.2 arrives as ordinary updates.
- 20261107 Learned 2026-11-07 (b) in `references/storage.md`: adding `import` with the full content list; thin-pool fill on a single-disk lab.
- 20261107 Learned 2026-11-07 (c) and (j) in `references/networking-and-sdn.md`: SDN.Use on localnetwork for `vmbr0`; SDN simple zone DHCP with PVE IPAM binds MACs, token needs the zone ACL.
- 20261107 Learned 2026-11-07 (d) in `references/qemu-vms.md`: provider `efi_disk` to `efidisk0` mapping; cite the installed OVMF version.
- 20261107 Learned 2026-11-07 (e), (f) and (g) in `references/access-control.md`: the pool-scoped token pattern proven by the task log; `Sys.AccessNetwork` alternative for download-url; wide legacy
  tokens found by the audit.
- 20261107 Learned 2026-11-07 (h) in `references/api-and-cli.md`: apt/update GET does not refresh; repositories, resources and task-log reads.
- 20261107 Learned 2026-11-07 (i) in `references/opentofu-bpg-provider.md`: `~> 0.118` resolved to 0.120.0; one-VM apply time.
- 20261107 Learned 2026-11-07 (k) in `references/upgrade-and-troubleshooting.md`: a 9.1.5 node's pending 9.2 stack and repository state.
- 20261107 Learned 2026-11-07 (l) in `references/monitoring-and-metrics.md`: node report runtime and budget.
