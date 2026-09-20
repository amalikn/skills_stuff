# Cambium Device Fleet Operational Runbook

**Validated against:** seeded 2026-09-17 from operator-supplied data only; superseded the same day once live-authenticated sessions began. As of 2026-09-17 20:57, all four Cambium device families
(Enterprise Wi-Fi XV2/E-series, ePMP AP/SM, cnWave 60GHz, cnPilot R195P) have real, live-verified adapter code and `VERIFIED-OBSERVED` data (SSH CLI and/or REST API, plus fleet-wide SNMPv2c GETs) —
see `references/06_device-api-cli-reference.md` for the adapter data points and `CHANGELOG.md` for the live-test trail. Coverage gaps that remain are tracked individually in
`references/05_known-issues.md`, not as a blanket "no device session yet" state.
**Scope:** Cambium Enterprise Wi-Fi, cnPilot R-series, ePMP AP/SM, and cnWave 60 GHz hardware deployed by APN

This file is the navigation index for the `skill-cambium` specialist pack. Load only the focused reference needed for the task instead of reading every Cambium detail up front.

## Related Workspaces

| Path                                                                   | Relationship                                                                                                                |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap`            | Live source of truth — its own `inventory/` holds the device-family matrix, device inventory, cnMaestro instance list, and  |
|                                                                        |   site asset registers                                                                                                      |
| `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller`       | FOSS controller build (Nautobot + adapter layer) replacing cnMaestro's monitoring/dashboard and TR-069 provisioning roles — |
|                                                            |   consumes this pack's device-access/API knowledge, does not duplicate it; split out of `cambium-swap` 2026-09-18           |
| `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc` | SMC box / ansible-wifi provisioning layer — the Cambium fleet's management plane. Cross-reference at the                    |
|                                                                        |   `smc_cnmaestro_provisioning` role boundary                                                                                |
| `/Volumes/Data/_ansible/ansible-wifi`                                  | Production Ansible source; canonical `site_name` values live in `inventories/<flavour>/group_vars/<site>.yml`               |
| `/Volumes/Data/_ansible/local-knowledge-ansible`                       | Local-only SMC/Cambium plans, reports, and investigation knowledge — check here before assuming a gap is unresearched       |

Reference hygiene: when a fact affects both packs (e.g. a new site's `site_name`, a cnMaestro-provisioning behaviour), update this pack's matching reference **and** flag it for `skill-smc` — see each
pack's `AGENTS.md` Standing Write-Back Contract.

## Reference Routing

| Task                                                                                                          | Read                                          |
| ------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Device families, models, firmware/EoL snapshot, evidence-state discipline                                     | `references/01_overview.md`                   |
| Device local-admin access, KeePassXC `cambium-devices/` vault structure, `kp` wrapper gotchas                 | `references/02_device-access-and-vault.md`    |
| Asset-register naming convention, per-site drift, site-name convention, R195P IP-derivation rule              | `references/03_asset-register-conventions.md` |
| Machine-readable per-site/family IP addressing trust state (verified/contradicted/unverified), MAC-OUI lookup | `references/site-addressing.yaml`             |
| `device-inventory.csv` column contract, `UNKNOWN` discipline, cross-site IP collisions, extraction workflow   | `references/04_device-inventory-schema.md`    |
| Coverage gaps, unverified assumptions, pack staleness risks                                                   | `references/05_known-issues.md`               |
| Device REST API / SSH CLI data points per adapter method, config-backup source, write-ops boundary            | `references/06_device-api-cli-reference.md`   |

**Do not write new operational content to this file** — it is a navigation index only. Write content to the matching reference file.

## Runtime Paths

- KeePassXC vault: `~/Library/CloudStorage/OneDrive-Personal/A/APN_keepassDB.kdbx` (`cambium-devices/` group)
- `kp` wrapper: `~/.config/keepassxc/kp`
- Live device inventory: `/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap/inventory/`

- venv (working-cache peer, never in the repo): `/Volumes/Data/_ai/_skills/skills-working-cache/skill-cambium/.venv`
- `just bootstrap` builds it from `.mise.toml`'s pin (Python 3.14) and `requirements.txt` (`openpyxl`, needed only by `scripts/extract-asset-register.py`); `just runtimes` reports what's actually
  resolved; `just check` runs `scripts/check_governance.py`. See [justfile](justfile).
- `scripts/cambium-portal.sh` (moved from `cambium-swap` 2026-09-17): Cambium support-portal (support.cambiumnetworks.com) automation — `login` (optional Downloads search) and `fetch-release <model>
  <version> <dest>` (find and download a specific dated release's files, sniffing each one's real type since the portal gives download links no filename). Needs a live MFA code from the operator each
  run — cannot run unattended. `just cambium-login [search]` / `just cambium-fetch-release <model> <version> <dest>`. Consuming projects (e.g. `cambium-swap`) call this canonical path directly rather
  than keeping their own copy.
