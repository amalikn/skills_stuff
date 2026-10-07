# Changelog

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
