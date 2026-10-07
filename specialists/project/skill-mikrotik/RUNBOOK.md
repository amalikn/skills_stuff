# MikroTik Site Device Runbook

**Validated against:** RB450Gx4 and Metal 52 ac on RouterOS 7.8, read-only sessions 2026-10-07 (delye, amuroona, then the reachable `rct` fleet).
**Scope:** MikroTik devices behind SMC boxes.

This file is the navigation index for `skill-mikrotik`. Load only the reference the task needs.

## Reference Routing

| Task                                                                                                  | Read                                      |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Models, firmware, port and VLAN layout, fleet ranges (uptime, voltage, temperature)                   | `references/01_overview.md`               |
| Logging in: KeePass entry, Teleport port-forward, read-only guard, why nothing secret runs on the SMC | `references/02_device-access.md`          |
| Which RouterOS command shows what; field meanings; RouterOS 7 gotchas                                 | `references/03_routeros-cli-reference.md` |
| A site is dark or flapping: known signatures and how they were confirmed                              | `references/04_failure-modes.md`          |
| How new switches are built: the Pi provisioning script, what it sets, issues it puts on every unit | `references/06_provisioning.md` |
| Gaps, unverified assumptions, things not yet surveyed                                                 | `references/05_known-issues.md`           |
| Scripts and their safety class                                                                        | `scripts/README.md`                       |

**Do not write operational content here**; write it to the matching reference file.

## Runtime Paths

- KeePass entry: `Network/mikrotik switch & metal ap` in `~/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx`, read with the `kp` wrapper.
- Tools: `tsh`, `sshpass` (Homebrew), `nc`, `python3` (stdlib only). `just check` runs `scripts/check_governance.py`.
- Investigation captures: `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/issues/<flavor>-fleet/<topic>/`.
