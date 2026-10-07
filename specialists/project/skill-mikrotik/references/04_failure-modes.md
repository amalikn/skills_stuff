---
Title: MikroTik failure modes seen in the SMC fleet
Category: reference
Status: current
Authority: local-supplement
Scope: Failure signatures involving the site MikroTik, with the evidence that confirmed each
Last reviewed: 2026-10-07
Summary: Whole-trunk silence at arrkapa, SMC-port link flapping at delye, and how TSTIK power-cycles show in switch uptime.
---

# MikroTik Failure Modes

## Contents

- [Whole trunk silent while the SMC keeps transmitting (arrkapa, rct, 2026-10-02 onward)](#whole-trunk-silent-while-the-smc-keeps-transmitting-arrkapa-rct-2026-10-02-onward)
- [SMC-port link flapping (delye, rct, 2026-08-17/18)](#smc-port-link-flapping-delye-rct-2026-08-1718)
- [Switch uptime shorter than the SMC's](#switch-uptime-shorter-than-the-smcs)

## Whole trunk silent while the SMC keeps transmitting (arrkapa, rct, 2026-10-02 onward)

Looks like a Sky Muster outage; the evidence says it is the SMC-to-switch segment or the switch. Full write-up from the SMC side: skill-smc `references/06_failure-modes.md` "Whole Switch Trunk Goes
Silent While the SMC Keeps Transmitting".

- SMC up since 2026-07-03; Sky Muster path healthy (~660 ms, 30–48 Mbps) until 2026-10-02.
- During each outage every VLAN on the SMC's eth0 received almost nothing (3,641 packets in 54 h) while the SMC kept sending ~750 small packets an hour. Local VLANs (AP management 500, NTD management
  521) went silent together with the internet, which a satellite-only fault would not do.
- The SMC's TSTIK app power-cycles this switch after ~11 minutes of failed switch/AP pings, which fits the few-hour recovery windows.
- **Not yet confirmed on the switch itself:** arrkapa has been unreachable since 2026-10-07 10:54. `scripts/mikrotik-site-capture.sh` with `WAIT_UP=1` is set to capture uptime, ether1 link-downs and the log
  as soon as it reconnects (output: the `capture-arrkapa-mikrotik` folder in the arrkapa-wan investigation folder). Update this entry from that capture.

## SMC-port link flapping (delye, rct, 2026-08-17/18)

VERIFIED-OBSERVED 2026-10-07. delye's switch ether1 (the SMC trunk) shows `link-downs=3715`, last down `aug/18/2026 11:33:56`; the log is full of `ether1 link down` / `link up (speed 1G, full duplex)`
pairs a few seconds apart from 2026-08-17. The SMC's uptime (50 days at 2026-10-07) puts its boot at about 2026-08-18, so the flapping stopped when the SMC was rebooted or replaced. The cause (Pi NIC,
cable, or Pi power) is not established. amuroona, for comparison: `link-downs=2` on ether1.

How to spot it: ether1 `link-downs` in the thousands in `scripts/mikrotik-fleet-survey.sh` output, or many `interface,info ether1 link` lines in the log.

## Switch uptime shorter than the SMC's

The `rct` TSTIK app cuts the switch rail for 10 s when the switch or AP stops answering pings for ~11 minutes, and every ~71 minutes while the internet ping fails. A switch whose uptime is much
shorter than the SMC's has been power-cycled; on `rct` that is the first explanation to test. Confirm against the SMC's `/var/www/html/rct-tstik/storage/logs/laravel.log*` ("Resetting Switch", UTC
timestamps) with skill-smc `scripts/tstik-capture.sh`.

## Port-level link-down patterns across the fleet (rct survey 2026-10-07)

- ether1 (SMC trunk) is quiet fleet-wide: median 7 link-downs since device boot, one outlier (rollah, 1,987). A trunk problem is therefore unusual and worth chasing when seen.
- ether4 (phone UI) carries the largest counts (racecourse 47,914): the phone, its cable or its 10 Mbps half-duplex link drops constantly. Not an outage cause for the SMC.
- ether2 (Sky Muster NTD) up to ~10,000: TSTIK modem power-cycles each add one; a high count with a short switch uptime points at repeated modem resets.
- Survey and ranges: `01_overview.md`.

