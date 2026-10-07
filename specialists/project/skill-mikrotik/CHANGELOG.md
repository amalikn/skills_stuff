# Changelog

## 20261007_1623 — Mk3 connection diagram: what is on each port, rct vs wh (v0.1.9 -> v0.1.10)

- `references/mk3-connection-diagram-v0.5.pdf` (new): the operator's Mk3 site diagram, moved here from the pack root (was `Mk3 Connection Diagram v0.5 1.pdf`).
- `references/01_overview.md`: port table names the real devices (ether2 and ether3 are the satellite modem's Uni-D1 and Uni-D2, not a separate second WAN;
  ether4 the Dallas Delta ATA UI on `rct`; ether5 the PoE AP, Metal on `rct` and Cambium on `wh`); new Site design section (untagged-internet reason for
  ether1 in `bridge-vlan521`, ATA and Thuraya backup, AP addressing, SMC Wi-Fi SSID).
- skill-smc 0.1.98: SMC-side addressing from ansible-wifi compared with the diagram (diagram stale on management DNS and a `192.168.100.2` note).

## 20261007_1620 — Cloned MACs come from the provisioning script, not a backup (v0.1.8 -> v0.1.9)

- **Correction:** v0.1.4 put the cloned MACs down to one binary backup restored onto every switch. The operator described the real process (a Raspberry Pi
  pushes `routeros-7.8-arm.npk` over TFTP and two SSH command batches) and pasted the commands: part 1 pins `mac-address=` on ether1–ether5. The backup
  explanation and its vendor-doc quote are removed from `references/01_overview.md`; the new-switch fix is now deleting those five commands from the script.
- `references/06_provisioning.md` (new): the process, what the script sets, the issues it leaves on every unit, and the commands one per line, password redacted.
- `references/01_overview.md`: port layout and ether5 PoE confirmed by the script.
- `references/05_known-issues.md`: items 3 (time zone and NTP) and 4 (logging to disk) updated from the script; new 12 (script location, owner, APs) and 13
  (shared clear-text admin password, MAC access on all ports, HTTP on, protected RouterBOOT off).
- `RUNBOOK.md`, `SKILL.md`: routing for `references/06_provisioning.md`. `SCRATCHPAD.md`: cause corrected.

## 20261007_1605 — arrkapa root cause: switch kernel-failure / watchdog reboot loop (v0.1.7 -> v0.1.8)

- `references/04_failure-modes.md`: arrkapa finding with evidence; new signature section (watchdog timer + kernel failure loop) and how to tell it from a power cut.
- `references/05_known-issues.md`: item 1 closed; batavia-downs left open.

## 20261007_1602 — Fleet survey host list without word splitting (v0.1.6 -> v0.1.7)

- `scripts/mikrotik-fleet-survey.sh`: Teleport host list read one per line into an array instead of an unquoted `$(...)` (shellcheck SC2046); works on
  bash 3.2 and with an empty list under `set -u`.

## 20261007_1557 — Operational record and memory channel (v0.1.5 -> v0.1.6)

- Operational, no pack file changed: cross-links added in skill-smc and skill-cambium `SKILL.md` Related Skills and an "Also invoke `skill-mikrotik`" rule in
  ansible-wifi `AGENTS.md`; enterprise-strategy `AGENTS.md` Knowledge sources and `README.md` list this pack (operator: use it like skill-cambium and
  skill-smc), and its three running sessions were messaged. First fleet survey attempt aborted at ~8 sites (per-command SSH sessions, ~4 h ETA); batching fixed
  it. Two devices refused the correct password for a few minutes at about 14:30 (known issue 7).
- Memory: memory-keeper channel `skill-mikrotik` and project-context project `skill-mikrotik` created at this slurp (keys and IDs in `SCRATCHPAD.md`). Until
  then every entry about this pack sat under `ansible-wifi`.

## 20261007_1542 — Cloned-MAC remedy: missing steps and open item (v0.1.4 -> v0.1.5)

- `references/01_overview.md`: remedy split into new switches, existing fleet and rollout; adds why MAC lines must be stripped (golden unit is a clone), setting
  the admin password after `/import`, and one switch, then canary, then fleet.
- `references/05_known-issues.md`: item 11, Ethernet `reset-mac-address` and bridge MAC follow-through untested.
- `SCRATCHPAD.md`: cloned-MAC state and next action.

## 20261007_1534 — Cloned MACs: cause from vendor docs, factory MAC observed, remedy proposed (v0.1.3 -> v0.1.4)

- `references/01_overview.md`: binary backup restores MACs (VERIFIED-DOC); amuroona orig vs current MAC; APs unaffected; text-export template and `reset-mac-address` remedy, proposed not applied.

## 20261007_1525 — KeePass entry renamed; rct single-AP fact (v0.1.2 -> v0.1.3)

- KeePass entry is now `Network/mikrotik switch & metal ap` (operator fixed the spelling); `scripts/mikrotik-exec.sh` default and all references updated.
- `references/01_overview.md`: rct sites have one AP and no point-to-point bridges (operator).

## 20261007_1501 — Cloned switch MACs; wh AP verified as Cambium (v0.1.1 -> v0.1.2)

- `references/01_overview.md`: all 294 rct switches share port MACs (`6C:3B:6B:53:F0:D5` on ether1) despite unique serials; wh `.20` verified as a Cambium XV2-2T0 (previously stated without checking).

## 20261007_1443 — rct fleet survey results, wh canary (v0.1.0 -> v0.1.1)

- `references/01_overview.md` (new content): devices per flavor, delye port/VLAN map, power (rct ~24-28 V, wh 48 V), fleet ranges from the 297-site survey.
- `references/04_failure-modes.md`: fleet port-level link-down patterns (ether1 quiet, ether4 phone and ether2 NTD noisy).
- `references/05_known-issues.md`: rewritten as a list; item 2 narrowed (wh has the switch, 48 V, no MikroTik AP); items 9 (rollah ether1) and 10 (kwala sensors) added.
- `scripts/survey-summary.py` (new, read-only); `scripts/mikrotik-exec.sh` batching and login retry; survey duration corrected to 19 minutes.

## 20261007_1422 — Pack created (v0.1.0)

- Seeded from the arrkapa (`rct`) outage investigation: the operator added the MikroTik login to KeePass (`Network/microtik switch & metal ap`) and asked for a pack built like skill-cambium and
  skill-smc, with a write-back loop.
- `SKILL.md` (triggers, Standing Write-Back Contract, decision tree), `AGENTS.md` (self-evolution loop), `RUNBOOK.md`, `manifest.json`, `justfile`, `README.md`, `SCRATCHPAD.md`.
- `references/01..05`: overview and fleet ranges, device access, RouterOS CLI reference, failure modes (arrkapa trunk silence, delye SMC-port flapping, TSTIK switch power-cycles), known issues.
- `scripts/`: `scripts/mikrotik-exec.sh` (read-only RouterOS over a Teleport port-forward, password never on the SMC, batched sessions, login retry), `scripts/mikrotik-fleet-survey.sh`, `scripts/mikrotik-site-capture.sh`
  (`WAIT_UP=1`), `check_governance.py` (copied from skill-cambium, registries retuned).
- Tested read-only on delye-smc01 and amuroona-smc01; fleet survey of reachable `rct` sites in `local-knowledge-ansible/ansible-wifi/issues/rct-fleet/mikrotik-survey-20261007_1421/`.
