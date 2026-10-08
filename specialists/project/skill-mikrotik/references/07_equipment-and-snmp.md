---
Title: MikroTik equipment, SNMP and vendor sources
Category: reference
Status: current
Authority: local-supplement
Scope: The two MikroTik models in the fleet, their vendor specs, SNMP state and MIBs, firmware status, and the vendor sources kept in this pack
Last reviewed: 2026-10-08
Summary: >-
  RB450Gx4 switch and Metal 52 ac AP: specs from MikroTik's pages, SNMP read-only on the canary units and off elsewhere, MIBs for RouterOS 7.8 and 7.24.5, no changelog fix for the
  IPQ-4019 kernel failures, and the cpu-frequency warning. The OID list is snmp-oid-registry.yaml.
---

# MikroTik Equipment, SNMP and Vendor Sources

## Contents

- [The two models](#the-two-models)
- [SNMP](#snmp)
- [Firmware](#firmware)
- [The cpu-frequency warning](#the-cpu-frequency-warning)
- [MAC address commands](#mac-address-commands)
- [Vendor sources](#vendor-sources)

---

## The two models

VERIFIED_PRIMARY from MikroTik's product pages (`references/vendor-sources-20261007_1640/product-rb450gx4.txt`, `references/vendor-sources-20261007_1640/product-rbmetalg-52shpacn.txt`), with the units' own readings (delye and amuroona,
2026-10-07). The machine-readable copy is `snmp-oid-registry.yaml` under `equipment`.

| Item          | RB450Gx4 (switch, `10.255.0.5`)                       | RBMetalG-52SHPacn, "Metal 52 ac" (AP, `10.255.0.20`)      |
| ------------- | ----------------------------------------------------- | --------------------------------------------------------- |
| Revision      | r2                                                    | r2                                                        |
| CPU           | IPQ-4019, 4 cores ARM, nominal 448–896 MHz (auto)     | 1 core MIPSBE 720 MHz (page: QCA9556; unit: qca9550L)     |
| RAM, storage  | 1 GB, 512 MB                                          | 64 MB, 16 MB                                              |
| Ports         | 5 gigabit copper, ether1–ether5; PoE out on ether5    | 1 gigabit (PoE in); radio wlan1, 802.11ac                 |
| Power in      | DC jack 10–57 V, or PoE in 802.3af/at 12–57 V         | Passive PoE 10–30 V (from the switch's ether5)            |
| Max power     | 16 W (4 W without attachments)                        | 11 W                                                      |
| Temperature   | −40 to 70 °C tested ambient                           | −40 to 70 °C tested ambient                               |
| Factory OS    | RouterOS 6.48.7, upgraded to 7.8                      | RouterOS 6.48.6, upgraded to 7.8                          |

The AP's passive PoE input tops out at 30 V. On `rct` the bus is 23.6–30.0 V (01_overview.md), at the limit on the highest readings; `wh` sites (48 V) use a
Cambium AP instead, so a Metal is never fed 48 V there.

## SNMP

- **Off by default, now on at five sites.** RouterOS ships SNMP off (`ros-snmp.txt`: "enabled (yes | no; Default: no)") with a default `public` community
  open to `::/0`, and the provisioning script never turns it on (06_provisioning.md). With operator approval it was enabled read-only, `public` disabled,
  a vault community (`cambium-devices/apn-snmp-ro`) allowed only from the SMC (`10.255.0.1/32`), via `just snmp_community enable`, on:

  | Site | Flavour | Switch serial | AP serial | Enabled |
  | --- | --- | --- | --- | --- |
  | amuroona | `rct` | `HEX096Y47WC` | (in `snmp-oid-registry.yaml`) | 2026-10-07 |
  | 20-mile | `rct` | `HD4086NEMR1` | `HE208T81F2B` | 2026-10-08 |
  | adjamarragu | `rct` | `HEX09ECNCCW` | `HEB08NQZHXD` | 2026-10-08 |
  | areyonga | `wh` | `HEX098KSYZ8` | no MikroTik AP | 2026-10-08 |
  | glen-hill | `wh` | `HEX097QBC2Y` | no MikroTik AP (Cambium XV2-2T0) | 2026-10-08 |

  VERIFIED-OBSERVED 2026-10-08: each 2026-10-08 unit answered sysDescr and the mtxr serial from its SMC. Every other unit still has it off. Known issue 14.
- **What answered** (read from the SMC with `just snmp`; full list with values in `snmp-oid-registry.yaml` `oids`): sysDescr gives the model
  ("RouterOS RB450Gx4", "RouterOS RBMetalG-52SHPacn"); sysObjectID is `.1.3.6.1.4.1.14988.1` for both, so it is not a model key; serial, RouterOS
  version and board name; IF-MIB names, status and 64-bit octets; per-port link-downs; PoE status on ether5. Health: the old scalars still answer on 7.8
  (voltage in dV, temperature x10), but the gauge table gives temperature in **whole degrees** (unit celsius) while voltage stays in dV. The RB450Gx4's
  PoE voltage, current and power read 0: it reports PoE state only. `mtxrHlProcessorTemperature` is `noSuchObject` on the RB450Gx4. Neighbour tables
  are empty (discovery is limited to the `LAN` interface list, which the provisioning leaves empty). The AP's radio runs **2.4 GHz** (2412/20-Ce/gn).
- **Writes** (operator approved, amuroona switch, 2026-10-07; temporary read-write community from `cambium-devices/apn-snmp-rw`, removed after):
  `sysName` SET applies at once (CLI identity changed, then restored), but an SNMP GET straight after returns the old value for a few seconds, so verify a
  write over SSH or after a pause. `sysLocation` SET returns `noError` and is **not applied**: the location stayed empty. The read-only community's SET is
  refused (`readOnly`). RouterOS 7.8 has no `snmp-set` and the rct SMCs no net-snmp, so writes go through `scripts/snmp_via_smc.py`.
- **GPS:** neither model gives coordinates: no receiver on the product pages, no `gps` package, and `mtxrGps` (`.1.3.6.1.4.1.14988.1.1.12`) walks empty.
- **Enabling it is a device change:** operator approval, one unit first. A community's `address` defaults to `0.0.0.0/0` (`ros-snmp.txt`), so any community
  must be limited to `10.255.0.0/24`, read-only. Then verify each candidate OID on that unit and move it to `oids`, and add the lines to the Pi script.
- **MIBs.** MIKROTIK-MIB for RouterOS 7.8 (`references/vendor-sources-20261007_1640/mib-7.8/mikrotik.mib`, LAST-UPDATED 202112210000Z) and 7.24.5 (`references/vendor-sources-20261007_1640/mib-7.24.5/mikrotik.mib`); every OID the
  registry lists is the same in both. RouterOS also answers MIB-2, HOST-RESOURCES, IF, IP, IP-FORWARD, IPV6, BRIDGE, DHCP-SERVER, ENTITY and a few others
  ("Used MIBs in RouterOS", `ros-snmp.txt`); POWER-ETHERNET-MIB is not among them, so PoE is read from `mtxrPOETable`. Neither MIB holds a per-model
  sysObjectID. On a device, `print oid` at any menu prints the OIDs of that menu's values.
- **Version differences that matter:** `mtxrGaugeValue` changed to integer in 7.12, and PoE-out status codes were added to the MIB in 7.15
  (`references/vendor-sources-20261007_1640/routeros-changelogs-7.8-to-7.24.5.txt`). RouterOS 7 reports health through the gauge table, voltage in dV and temperature multiplied by 10
  (`references/vendor-sources-20261007_1640/ros-health.txt`).
- `scripts/mib_oids.py` resolves any MIB name to its OID (`just mib_oids <mib> '<regex>'`).

## Firmware

- The fleet runs **RouterOS 7.8** (February 2023). On 2026-10-07 stable is **7.24.5** and long-term **7.23.7** (`references/vendor-sources-20261007_1640/NEWESTa7.stable`, `NEWESTa7.long-term`).
- **No changelog entry from 7.8 to 7.24.5 fixes IPQ-40xx kernel failures or "rebooted without proper shutdown"** (77 changelogs read): arrkapa's failure
  (04_failure-modes.md) is not a known-fixed bug. Related entries: 7.10 "improved watchdog reporting in log after reboots for several ARM and ARM64
  devices"; 7.16 "improved watchdog and kernel panic reporting" and "routerboard - improved Etherboot stability for IPQ-40xx devices"; 7.22.3 fixed an
  IPQ-40xx switch-reset stability bug introduced in 7.22, which never affected 7.8. Known issue 8.
- **Firmware files kept** (operator 2026-10-08: committed, not gitignored): 7.8, 7.12.2, 7.23.7 and 7.24.5 for arm (RB450Gx4) and mipsbe (Metal 52 ac):
  `routeros`, `all_packages`, `wireless` (7.23.7 and 7.24.5; 7.8 and 7.12.2 bundle it) and `netinstall`, in `firmware-files/<version>/`, each with size, sha256
  and source in `references/firmware-manifest.yaml`.
- **Upgrade path from 7.8 needs a stop at 7.12.x** (VERIFIED-DOC, 7.13 changelog in `references/vendor-sources-20261007_1640/routeros-changelogs-7.8-to-7.24.5.txt`): 7.13 split the `wireless`
  package out of the bundle, and an upgrade to 7.13 or later "must be done through 7.12 in order to convert wireless packages automatically"; Netinstall or a
  manual package install is the exception. The intermediate image kept is **7.12.2** (2023-12-20), the last 7.12.x on the download host (7.12.3 returns 404),
  so the path from these files is 7.8 -> 7.12.2 -> 7.23.7 or 7.24.5. MikroTik publishes no `.sha256` for 7.12.x; the files are checked by size and ETag md5.

## The cpu-frequency warning

`/system routerboard print` on the RB450Gx4 shows `Warning: cpu not running at default frequency`, and the units run 716 MHz. The product page gives the
nominal frequency as "448-896 (auto) MHz" (VERIFIED_PRIMARY), so the setting is fixed rather than auto. Forum answers (VERIFIED_SECONDARY, not MikroTik staff)
say the default became auto in later versions and the warning goes when the setting is auto. Since 7.17 changing it needs device-mode `routerboard=yes`
(`references/vendor-sources-20261007_1640/ros-device-mode.txt`). Nothing links the warning to the arrkapa crashes. Known issue 15.

## MAC address commands

VERIFIED_PRIMARY, `references/vendor-sources-20261007_1640/ros-ethernet.txt`: "reset-mac-address ([id, name]) | Reset MAC address to manufacturers default." and "orig-mac-address (read-only: MAC)
| Original Media Access Control number of an interface." The page states no version, so the command on 7.8 is still to be shown on a unit (known issue 11).
`references/vendor-sources-20261007_1640/ros-bridging-and-switching.txt`: "admin-mac … only has an effect when auto-mac is set to no", "The current MAC address and its priority level are saved
and will be reused after a reboot", and "it is recommended to disable "auto-mac" and manually specifying the MAC address by using "admin-mac"."

## Vendor sources

`references/vendor-sources-20261007_1640/readme.md` indexes every file: the two MIBs (with derived OID index files), help.mikrotik.com pages saved as text (SNMP, Ethernet, Bridging,
RouterBOARD, Device-mode, Health, Packages, WiFi), product pages and PDFs, the concatenated changelogs 7.8 to 7.24.5, and three forum threads (secondary).
Refetch a doc page with `just fetch_doc <confluence-id> <out.txt>`. Firmware binaries are indexed separately in `references/firmware-manifest.yaml` (files in `firmware-files/`).
