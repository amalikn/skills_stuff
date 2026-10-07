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

1. **arrkapa switch not yet read** (offline since 2026-10-07 10:54). Why: confirms cable vs switch for the arrkapa outages. Close: the `WAIT_UP=1` run of `scripts/mikrotik-site-capture.sh` started
   2026-10-07; then update `04_failure-modes.md`.
2. **Layout outside `rct` only partly known.** `wh` has the same RB450Gx4 on 48 V and no MikroTik AP (laramba, canteen-creek, 2026-10-07); its full port map and the VLAN 502 sub-interface are not
   captured; `nbn_wh`, `rcp`, `nbn_accelerate` not checked. Close: `FLAVOR=wh scripts/mikrotik-fleet-survey.sh`, then `scripts/mikrotik-site-capture.sh` on one `wh` site.
3. **Device clock source and timezone.** Log timestamps have no year and an unknown zone, which blocks correlation with SMC and TSTIK logs. Close: `/system clock print`, `/system ntp client print` on
   a few devices.
4. **Log retention beyond the 1,000-line memory buffer.** Link-flap storms push older events out and nothing survives a reboot. Close: `/system logging action print` for disk or remote targets; decide
   whether to send syslog to the SMC.
5. **No central monitoring of these devices.** Uptime, voltage and link-downs are visible only by survey. Close: SNMP or a collector on the SMC; needs the operator's decision.
6. **Cause of delye's 2026-08-17/18 ether1 flapping.** Same signature could recur. Close: any surviving SMC-side log for that window; ask the site team what changed on 2026-08-18.
7. **Two devices refused the correct password for a few minutes on 2026-10-07.** Could be a login rate limit or a local sshpass race. Close: note the time if it recurs; `/log print where
   topics~"account"` on the device.
8. **RouterOS 7.8 (February 2023) everywhere surveyed.** Old release with later fixes. Close: vendor changelog review before any upgrade proposal; upgrades need operator approval.
9. **rollah switch ether1 (SMC trunk): 1,987 link-downs**, the only fleet outlier (median 7). Same signature as delye's flapping. Close: capture rollah's switch log and the SMC's kernel link log.
10. **kwala switch and AP temperatures read 0–2 C.** Faulty sensor or reporting. Close: re-read and compare with the SMC's CPU temperature.
11. **Cloned-MAC remedy untested on a device.** `/interface ethernet reset-mac-address [find]` is not confirmed for Ethernet (docs show the wireless form), and
    whether the `auto-mac=yes` bridges pick up the factory MAC without a reboot is unknown. Why: the fleet fix in `01_overview.md` depends on both. Close: with
    operator approval, run it on one switch, record `/interface ethernet print detail` and `/interface bridge print detail` before and after, then update
    `01_overview.md`.
