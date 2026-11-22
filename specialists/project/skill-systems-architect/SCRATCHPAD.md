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

- **20261119_1109** v2.3.14: `references/backup-disaster-recovery.md` keyless verification of a pulled restic copy and SeaweedFS S3 open by default (Continuum TASK-30).
- **20261118_2124** v2.3.11: `references/fleet-management.md` gained the asset-identity entry (ID register and restore, storage card as an asset, no-deletion against a backfill), from a design review for unified-network-controller (D17) that the operator asked this pack to do; nothing else changed.

- 20261116_1735: v2.3.10: edge-appliances, remote single-disk conversion tool limits and per-platform paths (from smc-resiliency).
- 20261116_1425: v2.3.9: edge-appliances, a password proxy does not isolate same-user processes.
- 20261116_1340: v2.3.8: edge-appliances bench power-cut automation through a Matter smart strip (from smc-resiliency afe4f03b).
- 20261110_1355: v2.3.6: edge retention after own upload, provisioning outcome surveys, transient units; SSH changed host key and reverse tunnels (from smc-resiliency koonibba work).
- 20261110_1205: v2.3.4: restore proof by exact row counts (backup-disaster-recovery) and compose `up --wait` false failures (containers-and-platforms), from the UNC Nautobot 3.2.9 upgrade.
- 20261110_0525: v2.3.3: ai-inference-platforms measured Qwen3.8-27B on oMLX, prefill-peak rule, hybrid prefix-cache blocks (from the Cline tuning work).
- 20261110_0025: v2.3.0: write-back from smc-resiliency S1 (bench Pi 4) and the APN operator context extended (see CHANGELOG 20261110_0025); not pushed until the operator's closeout push.

- v2.2.0: research-deepened references on one backbone, incl. databases-and-ha, ai-inference-platforms, edge-appliances,
  fleet-management, service-provider-systems; 8 helpers incl. quorum, ceph, restore, eol; filled examples; reads APN context from
  ../skill-network-architect/operator/apn/.
- Committed in skills_stuff up to b6f399f; push pending (operator).

- 2026-11-19: v2.3.15, two identity write-backs from continuum-app TASK-164 (edge client-certificate anchor, Keycloak issuer across networks).

## Next actions

- 2026-11-22 night: v2.3.23 write-backs from continuum (backup library vs process; incremental/chunked artefacts and retention; private-key copy on a removable drive; OpenFGA owner checks). Next: confirm prune with rustic_core before trusting it for retention.
- 2026-11-22: v2.3.22 write-backs from continuum (OrbStack disk/endpoints/volumes, JVM perf-data crash recurrence, software WebAuthn test authenticator, Bluetooth-free guest sign-in). Next: a containers-and-platforms check that services with state in the container filesystem have a volume.

- 2026-11-21: the client-authenticated recipient set entry (security-and-service-identity.md) rests on one project and Keybase; add a second source (Signal or MLS device linking) on the next E2EE design.
- 2026-11-11 (v2.3.7): edge-appliances read-only root entry is design reasoning; promote to VERIFIED once smc-resiliency records the R28 outcome with scheduled writers run in a trial.

1. Operator: push skills_stuff (see the network pack SCRATCHPAD).
2. Verify the open items: Apple Business built-in MDM depth (FileVault escrow, enforced updates), Patroni maximum_lag_on_failover default,
   libvirt multiqueue change needing a full stop and start per version, colocation kVA billing as a general rule.
3. PostgreSQL 14 reaches end of support 2026-11-12: any APN database on 14 needs a plan (eol register).
