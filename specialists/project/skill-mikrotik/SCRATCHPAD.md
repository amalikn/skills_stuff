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
- All 294 `rct` switches carry cloned MACs from one binary backup (`references/01_overview.md`). Remedy written up, not applied; waiting on operator go-ahead.
- Background waiter for arrkapa: `scripts/mikrotik-site-capture.sh` with `WAIT_UP=1`, output the `capture-arrkapa-mikrotik` folder in the arrkapa-wan investigation folder.

## Next actions

1. When the arrkapa capture lands: read ether1 link-downs, uptime, health and log; update `references/04_failure-modes.md` and skill-smc's arrkapa entry.
2. Survey `wh` (known issue 2).
3. With operator approval: test the cloned-MAC remedy on one switch (known issue 11), then a small canary.
4. Decide with the operator on central monitoring for these devices (known issue 5).
