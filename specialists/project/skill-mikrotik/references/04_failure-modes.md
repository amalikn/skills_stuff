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
- **Root cause found 2026-10-07 16:02 (VERIFIED-OBSERVED):** the arrkapa RB450Gx4 switch (serial `HCW08285341`) is in a crash-reboot loop. Its log
  holds 43 `router was rebooted without proper shutdown by watchdog timer` and 48 `kernel failure in previous boot` entries in the last 1,000 lines, several a
  minute at times; only 6 are plain power cuts (`probably power outage`, the TSTIK). The SMC's kernel log shows eth0 dropping 249 times between 01:28 and 16:00,
  down about 6 s and up about 23 s each time, and only 18 of those drops fall within a minute of a TSTIK switch reset. The TSTIK app reset the switch 80–104
  times a day from 2026-10-02 (4 on 10-01, none before) plus the modem and phone just as often, without effect. Board health at capture was normal (27.1 V,
  53 C, 948 MiB free, 0% bad blocks, RouterOS 7.8 like the whole fleet), so the unit itself is failing. Action: replace the switch; configure the spare from a
  text export with the `mac-address=` lines removed (cloned-MAC remedy in `01_overview.md`). Only one other switch in the 294-site survey logged the same
  signature: batavia-downs (11 lines, stable for 15 days at survey). Evidence: `local-knowledge-ansible/ansible-wifi/issues/rct-fleet/arrkapa-wan/capture-arrkapa-mikrotik/` and `local-knowledge-ansible/ansible-wifi/issues/rct-fleet/arrkapa-wan/capture-arrkapa/`.

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

## Switch kernel failure and watchdog reboot loop (arrkapa 2026-10, batavia-downs earlier)

Signature in `/log print`: `system,error,critical router was rebooted without proper shutdown by watchdog timer` followed by `kernel failure in previous
boot`, repeating. Every reboot drops every port, so the SMC sees its eth0 link flap (seconds down, tens of seconds up) and loses every VLAN at once, and the
`rct` TSTIK app starts power-cycling the switch, modem and phone without effect. Distinguish from a TSTIK power cut, which logs `router rebooted without proper
shutdown, probably power outage`. A switch showing this repeatedly is a hardware replacement, not a configuration fix. Fleet check: grep the survey raw
files for `watchdog timer`.

