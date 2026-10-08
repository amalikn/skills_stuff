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
   `/system clock print`, `/system ntp client print` on a few devices, and whether the SMC answers NTP. Seen at arrkapa (VERIFIED-OBSERVED 2026-10-07): the switch clock was about 8 h 25 min slow at 16:02 AEDT
   and its log times go backwards around crashes, so NTP was not in sync on that unit; whether healthy units sync is still unchecked.
4. **Log retention beyond the 1,000-line memory buffer.** Link-flap storms push older events out of `/log print`. The provisioning script sends logging
   rules 0–2 to `action=disk` (`06_provisioning.md`), so log files may survive a reboot in flash; not yet checked. Close: `/system logging print`,
   `/system logging action print`, `/file print where name~"log"` on one switch; then decide whether to send syslog to the SMC. Seen at arrkapa (VERIFIED-OBSERVED 2026-10-07): a switch 2 m 31 s after a reboot still listed 43 watchdog-reboot entries, so the log
   it shows does survive reboots on that unit; which action keeps it (disk rules or memory `remember`) is UNVERIFIED.
5. **No central monitoring of these devices.** Uptime, voltage and link-downs are visible only by survey. Close: SNMP or a collector on the SMC; needs the operator's decision.
6. **Cause of delye's 2026-08-17/18 ether1 flapping.** Same signature could recur. Close: any surviving SMC-side log for that window; ask the site team what changed on 2026-08-18.
7. **Two devices refused the correct password for a few minutes on 2026-10-07.** Could be a login rate limit or a local sshpass race. Close: note the time if it recurs; `/log print where
   topics~"account"` on the device.
8. **RouterOS 7.8 (February 2023) everywhere surveyed.** Stable is 7.24.5 and long-term 7.23.7 (2026-10-07); no changelog in between fixes IPQ-40xx kernel
   failures (07_equipment-and-snmp.md). Close: choose a target version and test it on one switch; upgrades need operator approval.
9. **rollah switch ether1 (SMC trunk): 1,987 link-downs**, the only fleet outlier (median 7). Same signature as delye's flapping. Close: capture rollah's switch log and the SMC's kernel link log.
10. **kwala switch and AP temperatures read 0–2 C.** Faulty sensor or reporting. Close: re-read and compare with the SMC's CPU temperature.
11. **Cloned-MAC remedy: CLOSED for the method, 2026-10-08 (VERIFIED-OBSERVED, glen-hill, operator approved).** `/interface ethernet reset-mac-address [find]`
    exists on RouterOS 7.8 and returned each port to its `orig-mac-address` (glen-hill-switch01, serial HEX097QBC2Y: ether1-ether5 `6C:3B:6B:53:F0:D5`-`D9` became
    `78:9A:18:3A:53:36`-`3A`). All four `auto-mac=yes` bridges followed at once, no reboot: `bridge-vlan500` (the management address) took ether4's
    `78:9A:18:3A:53:39`, `bridge-vlan501` and `bridge-vlan521` ether1's, `bridge-vlan522` ether3's. The SMC re-learned the switch by ARP within three
    minutes, switch and AP answered ping throughout, the SMC did not reboot. Open: the other 293 switches (one at a time, read back each), and new switches
    need the five `mac-address=` lines removed from our own version of the provisioning script. Tool for the rest: `scripts/mikrotik_mac_reset.py`
    (`just mac_reset`), one switch per run, plan only unless `--apply`; it saves the before-state, reads back and prints a JSON summary.
12. **Provisioning script: owner and APs.** Partly closed 2026-10-08: the script is `450gmk3_v1.1.py` (read-only reference in this pack's root,
    `06_provisioning.md`); part 1 first connects to the factory `192.168.88.1` with an empty password. Still open: who owns the script and the Pi, how
    the Metal APs are provisioned, and whether ether4 sits unused on `wh` (no ATA there). Why: the new-switch MAC fix is a change to that script, made
    in our own version, never the reference. Close: ask the operator.
13. **Security settings every switch gets from the script.** One admin password on every unit, held in clear text in the script; MAC Winbox and MAC Telnet
    allowed on all interfaces, including the NTD and second-WAN ports; HTTP on with no address limit; `protected-routerboot=disabled` (`06_provisioning.md`).
    Not yet read back from a device. The password is in clear text in the reference script `450gmk3_v1.1.py` in this pack's root (2026-10-08), to be
    committed as is to the private repo (operator, 2026-10-08; not yet committed); the operator decided no rotation is needed (2026-10-07). Close: `/tool mac-server print`, `/tool mac-server mac-winbox print`, `/ip service print` on one switch; propose
    hardening (per-unit passwords from the vault, MAC access limited to VLAN 500, `www` off) for operator approval.
14. **SNMP off on every MikroTik except the canary units**, enabled read-only with operator approval (default `public` disabled, vault community allowed from
    the SMC only): amuroona switch and AP (2026-10-07; results in `snmp-oid-registry.yaml`); 20-mile and adjamarragu switch and AP, areyonga and glen-hill
    switch (2026-10-08, each answered sysDescr and serial; serials in `07_equipment-and-snmp.md`). RouterOS ships SNMP off with a `public` community open to `::/0`,
    so an enable must disable `public` first; RouterOS 7.8 has no `snmp-set`, and the SMC has Python but no net-snmp (`scripts/snmp_via_smc.py`). Why it
    matters: no collector can read the remaining units. Write test done 2026-10-07 (sysName applies, sysLocation is accepted and ignored). Open: the fleet rollout, and a line in the Pi script. Close: operator decision on the rollout; `just snmp_community <smc> <ip> enable <entry>`
    per unit.
15. **RB450Gx4 `cpu not running at default frequency` warning** on every switch read (716 MHz fixed; nominal 448–896 MHz auto). Effect unknown; secondary sources
    say setting it to auto clears it. Close: compare `/system routerboard settings print` with a factory unit; any change needs operator approval.
16. **Which script version built each switch.** The script writes `450g-changelog_v1.1.txt` to flash, and its re-run path treats a switch without it
    as "likely v1.0" (`06_provisioning.md`). What v1.0 set differently, and how many fleet switches it built, is unknown. Close: `/file print` in the
    next read-only fleet survey, counting units with and without the marker; ask the operator for the v1.0 differences.
17. **Two script checks would crash under Python 3** (`str` tested against `bytes`), from reading the code (`06_provisioning.md`, *Defects visible in
    the code*). If confirmed, provisioning has been stopping after the configuration is applied but before the serial is logged, so
    `mikrotik/450g.log` on the Pi would lack serials. Close: ask which Python the Pi runs, or read that log.
