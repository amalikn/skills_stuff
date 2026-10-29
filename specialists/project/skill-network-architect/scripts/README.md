---
Title: Offline script catalogue
Category: script-catalogue
Status: current
Authority: authored-guidance
Scope: skill-network-architect scripts/
Last reviewed: 2026-10-29
Summary: Every helper in scripts/, its inputs, outputs, safety class, exit codes, recipe and limits.
---

# Offline script catalogue

Standard library only; run through the working-cache venv (`just bootstrap` once, then the recipes). No helper touches a network, device or controller, and none writes a file. Every helper reads a
bounded JSON file and prints JSON with `status`, `findings`, `elapsed_seconds` and `limits`.

## Helpers

| Script           | Recipe                           | Input -> output                                                       | Safety and limits                                                      |
| ---------------- | -------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| [ip_plan_check.py](ip_plan_check.py) | `just ip-plan <plan.json>`       | Concrete segments per routing scope -> overlaps and gateway errors    | Read-only; 1 MiB, 5,000 segments                                       |
| [mtu_budget.py](mtu_budget.py) | `just mtu <budget.json>`         | Underlay MTU and encapsulation stack per path -> payload MTU          | Read-only; 500 paths; fixed header sizes only                          |
|                  |                                  |   and shortfall                                                       |                                                                        |
| [link_budget.py](link_budget.py) | `just link-budget <links.json>`  | PtP radio parameters -> FSPL, received level, fade margin,            | Read-only; 1,000 links; free space plus k-factor bulge only            |
|                  |                                  |   Fresnel clearance                                                   |                                                                        |
| [availability.py](availability.py) | `just availability <model.json>` | Series/parallel block model -> composite availability and downtime    | Read-only; 2,000 blocks; assumes independent failures. Shared:         |
|                  |                                  |   per year                                                            |   symlinked into skill-systems-architect                               |
| [fibre_budget.py](fibre_budget.py) | `just fibre <links.json>` | Fibre type, length, connections, splices, optic Tx min and Rx sensitivity -> plant loss and margin per link | Read-only; 500 links; TIA-568 maximum defaults (0.75 dB connector, 0.3 dB splice, 3.5/1.5/1.0/0.5 dB/km), overridable |
| [power_budget.py](power_budget.py) | `just power <site.json>` | Switches with PoE budget and port draws, other loads, UPS -> PoE headroom, class violations, UPS load and linear runtime | Read-only; PSE class watts af 15.4, at 30, bt3 60, bt4 90; runtime is linear, real runtime lower |
| [check_links.py](check_links.py) | `just links` | Skill folder -> every cited external URL probed (HEAD, GET fallback); failures and redirects with citing files | Read-only but uses the network; 8 workers, 15 s timeout, 2,000 URLs; Shared: canonical here, symlinked into skill-systems-architect |
| [fetch_sources.py](fetch_sources.py) | `just fetch-sources [--apply]` | Both packs' Markdown -> RFC .txt, PDFs and all-scraper Markdown snapshots in `sources/`, indexed in `sources/index.json` | Plan by default; writes only the store with --apply; resumable; 4 workers, timeouts, process-group kill; Shared: canonical here, symlinked into skill-systems-architect |
| [sources_ledger.py](sources_ledger.py) | `just ledger [--add f.json] [--apply]` | Pack Markdown + curated lists + store index -> rebuilt `sources.json` (curated evidence kept, every other cited URL as CITED, local copy paths) | Plan by default; writes only sources.json with --apply; Shared: canonical here, symlinked into skill-systems-architect |
| [check_package.py](check_package.py) | `just check`                     | Skill folder -> broken links, headers, JSON and Python syntax         | Read-only; skips dot folders. Shared: symlinked                        |
|                  |                                  |                                                                       |   into skill-systems-architect                                         |

Exit status for every helper: 0 = no findings, 1 = findings, 2 = invalid input.

## Domain models

**IP plan** (`examples/ip-plan.json`): `segments=[{id, scope, cidr, optional gateway}]`. id is unique within scope; CIDRs must be canonical; IPv4 and IPv6 are checked separately. Intervals are sorted
per scope and family, carrying the furthest end so nested overlaps cannot hide. Scoped reuse (VRFs) is allowed. IPv6 segments must be /64 (RFC 7421), except /127 links (RFC 6164) and /128 loopbacks. Not checked: allocation hierarchy, route leaks, DHCP/DNS, reserved pools, utilisation.

**MTU budget** (`examples/mtu-budget.json`, failing `examples/mtu-budget-short.json`): `paths=[{id, underlay_mtu, layers, required_payload_mtu}]`. A layer is a known name (`wireguard-ipv4` 60,
`wireguard-ipv6` 80, `vxlan-ipv4` 50, `vxlan-ipv6` 70, `geneve-ipv4` 50, `gre-ipv4` 24, `gretap-ipv4` 38, `pppoe` 8, `mpls-label` 4, `dot1q-inner` 4, `esp-gcm-ipv4` 57, `esp-gcm-ipv4-natt` 65, `esp-gcm-ipv6` 77: AES-GCM tunnel mode, worst-case padding) or `{name, bytes}` for any other cipher
such as IPsec ESP. Prove the result with a do-not-fragment probe on the real path.

**Link budget** (`examples/link-budget.json`): FSPL = 20 log10(d km) + 20 log10(f MHz) + 32.44; received level = Tx + gains - losses - FSPL; fade margin = received - sensitivity. First Fresnel radius
r = sqrt(lambda d1 d2 / d); earth bulge = d1 d2 / (2 k R) with k = 4/3 unless given. An obstacle's `clearance_m` is measured below the straight line of sight; the finding fires below 60% of r. No
rain, multipath or regulatory EIRP check.

**Availability** (`examples/availability.json`): `{name, availability}`, `{series: [...]}` (all needed: product) or `{parallel: [...]}` (any one suffices: 1 - product of unavailabilities). Correlated
failures (shared power, path, software release, operator) are series blocks, not parallel ones.

## Runtime budget

Target: under 5 seconds per command on a workstation; measured 2026-10-29: each example under 0.01 s helper time, `just test` about 1.3 s for 11 tests. 5,000 IP segments measured 0.02 s
(evals/results.md). Re-measure when an input grows past its cap.
