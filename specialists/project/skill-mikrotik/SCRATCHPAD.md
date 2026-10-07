---
Title: skill-mikrotik scratchpad
Category: working-memory
Status: current
Authority: local-supplement
Scope: Current state and next actions for the skill-mikrotik pack
Last reviewed: 2026-10-07
Summary: Where the pack stands, what is running, and what to do next. Overwrite the state section each session; keep it short.
---

# SCRATCHPAD

## Current state (2026-10-07)

- v0.1.0 created from the arrkapa investigation; read-only access verified on delye and amuroona.
- First `rct` fleet survey done (294/297 switches, 289/297 APs): `local-knowledge-ansible/ansible-wifi/issues/rct-fleet/mikrotik-survey-20261007_1421/` (survey.csv, summary.txt).
- `wh` canary (laramba, canteen-creek): RB450Gx4 on 48 V, no MikroTik AP.
- All 294 `rct` switches carry cloned MACs set by the Pi provisioning script (`references/06_provisioning.md`). Remedy written up, not applied; waiting on operator go-ahead.
- Provisioning (operator, 2026-10-07): a Pi pushes RouterOS 7.8 over TFTP and two SSH batches (`references/06_provisioning.md`); the Mk3 connection diagram
  (`references/mk3-connection-diagram-v0.5.pdf`) shows what is on each port, `rct` and `wh` alike apart from the ATA and the AP.
- Vendor sources, MIBs and the OID registry (candidates only; SNMP disabled everywhere checked) in `references/` (v0.1.11); UNC carries the vendor.
- Background waiter for arrkapa: `scripts/mikrotik-site-capture.sh` with `WAIT_UP=1`, output the `capture-arrkapa-mikrotik` folder in the arrkapa-wan investigation folder.

## Next actions

1. arrkapa switch must be replaced (kernel-failure / watchdog reboot loop, found 16:02); build the spare with the Pi script minus its five `mac-address=` commands. Watch batavia-downs.
2. Survey `wh` (known issue 2).
3. With operator approval: test the cloned-MAC remedy on one switch (known issue 11), then a small canary.
4. Decide with the operator on central monitoring for these devices (known issue 5).
5. SNMP read-only on one switch and one AP (operator approved 2026-10-07): verify the registry candidates, test a harmless write, record results.
6. Ask the operator for the provisioning script's location and owner and how APs are provisioned (known issue 12); read back the script's security
   settings on one switch (known issue 13).

## Recent decisions

- 2026-10-07 — Separate pack modelled on skill-cambium and skill-smc, with a write-back loop; the device vendor decides the pack (operator).
- 2026-10-07 — Read-only by default; secrets never run on the SMC (TCP port-forward, client on the Mac).
- 2026-10-07 — Cloned-MAC remedy (text-export template for new switches; `reset-mac-address` for the fleet) is proposed, not decided.

## Session history

- 2026-10-07 — Pack created from the arrkapa investigation; 297-site `rct` survey; `wh` canary; cloned MACs traced to the provisioning script (first thought to be a binary backup); v0.1.5 committed (`e720222`).
- 2026-10-07 16:20 — Provisioning script and Mk3 diagram supplied by the operator: cause corrected (v0.1.9), ports and site design (v0.1.10), SMC addressing
  vs ansible-wifi in skill-smc 0.1.98.

## Memory pointers

- memory-keeper channel `skill-mikrotik`: `skill-mikrotik.origin-and-structure`, `.access-method`, `.rct-survey-20261007`, `.layout-and-wh`,
  `.cloned-mac-remedy` (updated 16:26), `.provisioning-script-20261007`, `.mk3-diagram-20261007`, `.cloned-mac-evidence-delta`, `.arrkapa-and-open`, `.cross-links-20261007`. Related keys in channel `ansible-wifi`:
  `skill-mikrotik-created-20261007`, `ansible-wifi.mikrotik.cloned-macs-keepass-rename-20261007`.
- project-context project `skill-mikrotik` (`ee2796d9-6122-42c8-9aba-2d453b8a5f55`): one note, two decisions. Checkpoints `slurp-20261007-skill-mikrotik`, `slurp-20261007-mikrotik-provisioning`.

