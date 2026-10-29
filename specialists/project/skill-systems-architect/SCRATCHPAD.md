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

- v2.2.0: research-deepened references on one backbone, incl. databases-and-ha, ai-inference-platforms, edge-appliances,
  fleet-management, service-provider-systems; 8 helpers incl. quorum, ceph, restore, eol; filled examples; reads APN context from
  ../skill-network-architect/operator/apn/.
- Committed in skills_stuff up to b6f399f; push pending (operator).

## Next actions

1. Operator: push skills_stuff (see the network pack SCRATCHPAD).
2. Verify the open items: Apple Business built-in MDM depth (FileVault escrow, enforced updates), Patroni maximum_lag_on_failover default,
   libvirt multiqueue change needing a full stop and start per version, colocation kVA billing as a general rule.
3. PostgreSQL 14 reaches end of support 2026-11-12: any APN database on 14 needs a plan (eol register).
