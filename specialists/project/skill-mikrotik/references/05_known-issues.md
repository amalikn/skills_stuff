---
Title: skill-mikrotik known issues and gaps
Category: reference
Status: current
Authority: local-supplement
Scope: Open questions, unverified assumptions and coverage gaps for MikroTik devices in the SMC fleet
Last reviewed: 2026-10-07
Summary: What the pack does not know yet. Read before acting; close or update items as evidence arrives.
---

# Known Issues and Gaps

Each item: what is unknown, why it matters, how to close it. Remove an item only when its answer is written into the matching reference. Kept as a list, not a table, so the markdown formatter never
wraps an item across rows.

1. **Closed 2026-10-07:** arrkapa switch read at 16:02; it is in a kernel-failure / watchdog reboot loop (`04_failure-modes.md`). Open part: why
   batavia-downs logged the same signature earlier (11 entries) and whether it recurs.
2. **Layout outside `rct` only partly known.** `wh` has the same RB450Gx4 on 48 V and no MikroTik AP (laramba, canteen-creek, 2026-10-07); its full port map and the VLAN 502 sub-interface are not
   captured; `nbn_wh`, `rcp`, `nbn_accelerate` not checked. Close: `FLAVOR=wh scripts/mikrotik_fleet_survey.sh`, then `scripts/mikrotik_site_capture.sh` on one `wh` site.
3. **Device clock source and timezone.** Log timestamps have no year, which blocks correlation with SMC and TSTIK logs. The provisioning script sets
   `Australia/Melbourne` and NTP servers `10.255.0.1` (the SMC) and `139.180.160.82` (`06_provisioning.md`); not yet read back from a device. Close:
   `/system clock print`, `/system ntp client print` on a few devices, and whether the SMC answers NTP.
4. **Log retention beyond the 1,000-line memory buffer.** Link-flap storms push older events out of `/log print`. The provisioning script sends logging
   rules 0–2 to `action=disk` (`06_provisioning.md`), so log files may survive a reboot in flash; not yet checked. Close: `/system logging print`,
   `/system logging action print`, `/file print where name~"log"` on one switch; then decide whether to send syslog to the SMC.
5. **No central monitoring of these devices.** Uptime, voltage and link-downs are visible only by survey. Close: SNMP or a collector on the SMC; needs the operator's decision.
6. **Cause of delye's 2026-08-17/18 ether1 flapping.** Same signature could recur. Close: any surviving SMC-side log for that window; ask the site team what changed on 2026-08-18.
7. **Two devices refused the correct password for a few minutes on 2026-10-07.** Could be a login rate limit or a local sshpass race. Close: note the time if it recurs; `/log print where
   topics~"account"` on the device.
8. **RouterOS 7.8 (February 2023) everywhere surveyed.** Stable is 7.24.5 and long-term 7.23.7 (2026-10-07); no changelog in between fixes IPQ-40xx kernel
   failures (07_equipment-and-snmp.md). Close: choose a target version and test it on one switch; upgrades need operator approval.
9. **rollah switch ether1 (SMC trunk): 1,987 link-downs**, the only fleet outlier (median 7). Same signature as delye's flapping. Close: capture rollah's switch log and the SMC's kernel link log.
10. **kwala switch and AP temperatures read 0–2 C.** Faulty sensor or reporting. Close: re-read and compare with the SMC's CPU temperature.
11. **Cloned-MAC remedy untested on a device.** `/interface ethernet reset-mac-address` is documented for Ethernet (07_equipment-and-snmp.md) but with no version, so
    7.8 is unconfirmed; and
    whether the `auto-mac=yes` bridges pick up the factory MAC without a reboot is unknown. Why: the fleet fix in `01_overview.md` depends on both. Close: with
    operator approval, run it on one switch, record `/interface ethernet print detail` and `/interface bridge print detail` before and after, then update
    `01_overview.md`.
12. **Provisioning script: location, owner, first contact, APs.** The operator described the Pi script and pasted its commands (2026-10-07), but where it
    lives, who maintains it, the address part 1 first connects to, how the Metal APs are provisioned, and whether ether4 sits unused on `wh` (no ATA there) are not recorded. Why: the new-switch MAC fix is an
    edit to that script. Close: ask the operator; record the path in `06_provisioning.md`.
13. **Security settings every switch gets from the script.** One admin password on every unit, held in clear text in the script; MAC Winbox and MAC Telnet
    allowed on all interfaces, including the NTD and second-WAN ports; HTTP on with no address limit; `protected-routerboot=disabled` (`06_provisioning.md`).
    Not yet read back from a device. The operator pasted that password into a chat transcript on 2026-10-07; it is in no file, and rotating it is the
    operator's call. Close: `/tool mac-server print`, `/tool mac-server mac-winbox print`, `/ip service print` on one switch; propose
    hardening (per-unit passwords from the vault, MAC access limited to VLAN 500, `www` off) for operator approval.
14. **SNMP off on every MikroTik except amuroona's switch and AP**, enabled read-only there 2026-10-07 with operator approval (default `public` disabled,
    vault community allowed from the SMC only); results in `snmp-oid-registry.yaml`. RouterOS ships SNMP off with a `public` community open to `::/0`,
    so an enable must disable `public` first; RouterOS 7.8 has no `snmp-set`, and the SMC has Python but no net-snmp (`scripts/snmp_via_smc.py`). Why it
    matters: no collector can read the other units. Write test done 2026-10-07 (sysName applies, sysLocation is accepted and ignored). Open: the fleet rollout, and a line in the Pi script. Close: operator decision on the rollout; `just snmp_community <smc> <ip> enable <entry>`
    per unit.
15. **RB450Gx4 `cpu not running at default frequency` warning** on every switch read (716 MHz fixed; nominal 448–896 MHz auto). Effect unknown; secondary sources
    say setting it to auto clears it. Close: compare `/system routerboard settings print` with a factory unit; any change needs operator approval.
