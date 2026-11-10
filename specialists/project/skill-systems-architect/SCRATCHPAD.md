---
Title: skill-systems-architect scratchpad
Category: working-memory
Status: current
Authority: local-supplement
Scope: Current state and next actions for the skill-systems-architect pack
Last reviewed: 2026-10-29
Summary: Where the pack stands and what to do next. Overwrite the state section each session; keep it short.
---

# SCRATCHPAD

## Current state (2026-10-29, closeout)

- 20261110_1355: v2.3.6: edge retention after own upload, provisioning outcome surveys, transient units; SSH changed host key and reverse tunnels (from smc-resiliency koonibba work).
- 20261110_1205: v2.3.4: restore proof by exact row counts (backup-disaster-recovery) and compose `up --wait` false failures (containers-and-platforms), from the UNC Nautobot 3.2.9 upgrade.
- 20261110_0525: v2.3.3: ai-inference-platforms measured Qwen3.8-27B on oMLX, prefill-peak rule, hybrid prefix-cache blocks (from the Cline tuning work).
- 20261110_0025: v2.3.0: write-back from smc-resiliency S1 (bench Pi 4) and the APN operator context extended (see CHANGELOG 20261110_0025); not pushed until the operator's closeout push.

- v2.2.0: research-deepened references on one backbone, incl. databases-and-ha, ai-inference-platforms, edge-appliances,
  fleet-management, service-provider-systems; 8 helpers incl. quorum, ceph, restore, eol; filled examples; reads APN context from
  ../skill-network-architect/operator/apn/.
- Committed in skills_stuff up to b6f399f; push pending (operator).

## Next actions

1. Operator: push skills_stuff (see the network pack SCRATCHPAD).
2. Verify the open items: Apple Business built-in MDM depth (FileVault escrow, enforced updates), Patroni maximum_lag_on_failover default,
   libvirt multiqueue change needing a full stop and start per version, colocation kVA billing as a general rule.
3. PostgreSQL 14 reaches end of support 2026-11-12: any APN database on 14 needs a plan (eol register).
