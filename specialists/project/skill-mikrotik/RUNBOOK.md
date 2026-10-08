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
| How new switches are built: the Pi provisioning script (`450gmk3_v1.1.py`, read-only), what it sets, its defects | `references/06_provisioning.md` |
| Model specs, SNMP state and MIBs, firmware status, cpu-frequency warning, vendor sources | `references/07_equipment-and-snmp.md` |
| SNMP OIDs per model (candidates from the 7.8 MIB until verified), equipment facts, the list tools read | `references/snmp-oid-registry.yaml` |
| Firmware files kept (RouterOS 7.8, 7.12.2, 7.23.7, 7.24.5; arm, mipsbe): sizes, sha256, source URLs; binaries in `firmware-files/` | `references/firmware-manifest.yaml` |
| Gaps, unverified assumptions, things not yet surveyed                                                 | `references/05_known-issues.md`           |
| Scripts and their safety class                                                                        | `scripts/README.md`                       |

**Do not write operational content here**; write it to the matching reference file.

## Runtime Paths

- KeePass entry: `Network/mikrotik switch & metal ap` in `~/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx`, read with the `kp` wrapper.
- Tools: `tsh`, `sshpass` (Homebrew), `nc`, `python3` (stdlib only). `just check` runs `scripts/check_governance.py`.
- Investigation captures: `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi/issues/<flavor>-fleet/<topic>/`.
