---
Title: Provisioning, automation and lifecycle
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Provisioning, automation and lifecycle: state model, first-boot identity, image and config chain, fleet waves with stop rules, EOL register, upgrade and retirement, acceptance tests.
---

# Provisioning, automation and lifecycle

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Lifecycle states](#lifecycle-states)
- [Supply and configuration chain](#supply-and-configuration-chain)
- [Rollout waves](#rollout-waves)
- [EOL register and retirement](#eol-register-and-retirement)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- The path from request to retirement for hosts, guests and services: intent, image, install, configuration, verification, operation.
- Fleet rollouts, EOL tracking, upgrade order and retirement.
- Nautobot/NetBox are optional adapters, not the architecture.

## Decision rules

| Decision             | Rule and threshold                                                                                         | Evidence                                             |
| -------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Field ownership      | One authoritative writer per field. Discovery observations never silently create production intent         | Design rule                                          |
| Identities           | Separate asset (serial), host (OS instance), guest, application and service identities                     | Design rule                                          |
| Cloned templates     | Regenerate machine-id and SSH host keys on first boot; a clone that keeps them is a defect                 | Design rule; [machine-id(5)][mid]                    |
| Secrets              | Deliver at runtime from the vault of record; never in images, plain-text cloud-init user-data or inventory | Design rule                                          |
| Infrastructure state | OpenTofu: plan state ownership, locking, backups, credential protection and provider version pins          | VERIFIED_PRIMARY (OpenTofu docs, checked 2026-10-29) |
| Batch composition    | Never one whole site or both halves of a redundant pair in one batch                                       | Design rule                                          |
| Uncertain write      | Never retry until its result is reconciled; retry only idempotent reads                                    | Design rule                                          |
| Wave sizes           | Canary 1 per role; sample ~5-10%; bulk with bounded concurrency                                            | UNVERIFIED as universal                              |
| Upgrade trigger      | Start at least two planning cycles before end of security support; more lead for edge sites                | Design rule                                          |
| Upgrade order        | firmware -> hypervisor -> guest OS -> runtime -> application; check schema compatibility both ways         | Design rule                                          |
| EOL review           | Quarterly and before budgets                                                                               | Design rule                                          |
| Retirement           | Observe zero traffic for an agreed period first. Erasure needs the task's explicit authorization           | Design rule                                          |

## Lifecycle states

| State                 | Exit check                                           |
| --------------------- | ---------------------------------------------------- |
| requested -> approved | Owner and purpose recorded                           |
| provisioned           | Asset and host IDs assigned                          |
| configured            | Converge OK; second run reports no change            |
| service-ready         | Acceptance tests pass                                |
| maintained            | Patch and EOL reviews current                        |
| retiring -> retired   | Data, DNS, monitoring, secrets and inventory cleared |

- Give each transition an owner and an exit check.
- Replacement must not inherit the wrong history; keep identities separate.

## Supply and configuration chain

```text
Supply and configuration chain with the reconcile loop

+---------+     +-------------------+     +-----------+     +-----------+     +--------+     +---------+
| request | --> | intent            | --> | image /   | --> | configure | --> | verify | --> | operate |
+---------+     | (source of truth) |     | provision |     +-----------+     +--------+     +---------+
                +-------------------+     +-----------+                                         |
                         ^                                                                      |
                         |      reconcile: diff observed against intent, never overwrite        |
                         +----------------------------------------------------------------------+

Legend: --> build step   loop = observed state returns as a diff for review
```

| Layer          | Tooling options                                                  | Prove                                                              |
| -------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| Infrastructure | OpenTofu/Terraform, Proxmox API                                  | State ownership, locking, backup, plan review, drift detection     |
| Base image     | Packer, debootstrap/mkosi, cloud images + cloud-init             | Pinned source and checksum, rebuild reproducibility, CVE scan date |
| Install        | Debian preseed, Ubuntu autoinstall, PXE/iPXE, cloud-init NoCloud | Unattended install from a clean target                             |
| Configuration  | Ansible (or Salt, Puppet)                                        | Check/diff mode, second run = no change, partial-failure handling  |
| Application    | Compose/Kubernetes manifests, packages                           | Pinned versions/digests, health checks                             |

- Capture exact source, version and run metadata for every build.
- First boot order: unique hostname and machine-id, fresh SSH host keys, access-layer enrollment, monitoring registration, time sync.
- Access-layer enrollment means an SSH CA host certificate or an access-proxy join token with a short TTL.
- Time sync must come before anything that needs TLS or Kerberos.

## Rollout waves

| Wave       | Scope                                      | Stop if                              |
| ---------- | ------------------------------------------ | ------------------------------------ |
| 0 canary   | 1 per role, lab or least-critical site     | Any failure                          |
| 1 sample   | ~5-10%, mixed sites, hardware and firmware | More than 0 unexplained failures     |
| 2 bulk     | Remainder, bounded concurrency per site    | Failure rate above the set threshold |
| 3 holdouts | Offline, special, manual-window targets    | Tracked to closure, never dropped    |

- Wave sizes and thresholds are a starting design (UNVERIFIED as universal). Set them per change from blast radius and rollback cost.
- Partition by role, platform, dependency and failure domain.
- Set a runtime budget, per-target timeouts, bounded concurrency (Ansible `serial`, `max_fail_percentage`, `throttle`) and checkpoint/resume.
- Record per-target outcome and a service check. Controller or API success is not service success.
- Measure each wave's runtime and report it with correctness evidence; re-measure when the fleet grows.

## EOL register and retirement

- One register row per component class: firmware/BIOS, BMC, OS release, kernel line, hypervisor, storage stack, container runtime, databases, applications.
- Columns: version in use, end of security support, end of extended support, source URL and check date, owner, planned window, status.
- Each upgrade has backup or snapshot, canary, abort criteria, and a rollback or forward-fix path stated before starting.
- Verified OS dates live in [linux-unix](linux-unix.md) and [windows-and-identity](windows-and-identity.md).
- Before retirement identify: active services and listeners (traffic evidence, not inventory alone), retained data and its retention duty.
- Also identify: DNS/DHCP/identity/monitoring/backup references, certificates and secrets to revoke, licences, owners.

```text
Retirement sequence (the host stays restorable until erase; erase is final)

drain --> zero traffic for --> power off --> revoke      --> remove     --> erase or destroy --> update
          agreed period        (restorable)  credentials     references     (explicit auth)      inventory
```

## Patterns and anti-patterns

| Pattern                                          | Use when                      | Anti-pattern                              | Why it fails                                              |
| ------------------------------------------------ | ----------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| Intent in a source of truth, reconciled by diff  | Any fleet                     | Discovery overwrites intent               | Drift becomes the new design silently                     |
| Host keys and machine-id generated on first boot | Templates and images          | Bake keys into the image                  | Every clone shares an identity; host trust is meaningless |
| Runtime secret fetch                             | Any secret                    | Secrets in images, user-data or inventory | Every copy of the image leaks them                        |
| Waves with stop rules                            | Fleet changes                 | All targets at once                       | One defect hits the whole fleet before anyone sees it     |
| Reconcile before retry                           | Writes with uncertain outcome | Blind retry on timeout                    | Duplicate or conflicting changes                          |
| Traffic evidence before retirement               | Decommissioning               | Retire from inventory alone               | A hidden consumer breaks                                  |

## Failure modes and tests

| Failure                             | Symptom                                                   | Blast radius      | Proving test                                                   |
| ----------------------------------- | --------------------------------------------------------- | ----------------- | -------------------------------------------------------------- |
| Clone keeps machine-id or host keys | Duplicate IDs in monitoring or DHCP; SSH host key clashes | Every clone       | Build two hosts from one template; compare IDs and keys        |
| Not idempotent                      | Second run reports changes                                | Role-wide drift   | Rerun with no changes; expect zero changes                     |
| Interrupted run                     | Half-configured targets                                   | Batch in flight   | Kill a run mid-wave; resume from checkpoint                    |
| Missing secret or failed dependency | Build stops or host comes up unusable                     | That build        | Remove a secret in the lab; expect a clean refusal             |
| Wrong target                        | Change lands on production                                | Unplanned hosts   | Wrong-target guard refuses a mismatched inventory              |
| Host replacement fails              | Rebuilt host differs from the old one                     | Role on that host | Replace a failed host from source of truth; verify the service |
| State file lost or unlocked         | Concurrent applies or orphaned resources                  | Whole stack       | State backup restore; lock contention test                     |

## Worked example

Fleet change: 240 hosts, 12 sites, 4 roles. About 6 minutes per host.

1. Wave 0: 4 hosts (1 per role). Wave 1: 8% of 240 = 19.2, rounded to 20.
2. Wave 2: 240 - 4 - 20 = 216 hosts. Concurrency: 2 per site x 12 sites = 24 at once.
3. Runtime: 216 / 24 = 9 rounds x 6 minutes = 54 minutes of wave 2.
4. Stop rule (illustrative): more than 2% failures, that is more than 4 of 216 hosts, stops wave 2.
5. Never place both members of a redundant pair in the same round.
6. Re-measure per-host time on wave 0 and 1; recompute before wave 2 starts.

## Review checklist

- [ ] Every field has one authoritative writer; observations never create intent.
- [ ] Builds record source, version and run metadata; images are reproducible and scanned.
- [ ] First boot generates identity and keys, enrolls access and monitoring, and syncs time.
- [ ] Secrets arrive at runtime from the vault of record.
- [ ] Waves have sizes, stop rules, timeouts, bounded concurrency and a measured runtime.
- [ ] The EOL register has every component class, with source, check date and owner.
- [ ] Acceptance: fresh build, host replacement, interrupted run and resume, no-change rerun, missing secret, failed dependency, wrong-target guard.
- [ ] After replacement the service is verified, then inventory and monitoring are reconciled.

## Further reading

Infrastructure and images:
- [OpenTofu introduction](https://opentofu.org/docs/intro/) - read this for state, plan and provider concepts (VERIFIED_PRIMARY, checked 2026-10-29).
- [OpenTofu state](https://opentofu.org/docs/language/state/) - read this for state locking, backends and sensitive data.
- [cloud-init documentation](https://docs.cloud-init.io/en/latest/) - read this for first-boot datasources and modules.
- [Packer documentation](https://developer.hashicorp.com/packer/docs) - read this for reproducible image builds (check its current licence before calling it FOSS).

Install automation:
- [Debian installation guide: preseeding](https://www.debian.org/releases/stable/amd64/apb.en.html) - read this for unattended Debian installs.
- [Ubuntu autoinstall reference][autoinst] - read this for Ubuntu Server unattended installs.

Configuration management:
- [Ansible: controlling playbook execution][ansstrat] - read this for serial, throttle and max_fail_percentage.
- [Ansible check mode and diff][anscheck] - read this for dry-run validation.

Identity on first boot:
- [machine-id(5)][mid] - read this for why cloned images must regenerate machine-id.

[autoinst]: https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html

[ansstrat]: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_strategies.html

[anscheck]: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html

[mid]: https://www.freedesktop.org/software/systemd/man/latest/machine-id.html
